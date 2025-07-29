import asyncio
from datetime import datetime, timedelta

from common_lib.logger import logger
from .db_connection import postgres_db

from schemas import pyggy_bank as pb_schemes
from schemas.service import RequestCreate
from schemas.song_event import SongEventCreate, SongEventCreateWithSong

from sqlalchemy import select, and_, inspect, update
from sqlalchemy.orm import DeclarativeBase, selectinload
from fuzzywuzzy import fuzz

from typing import (
    Type,
    List,
    Union,
    Dict,
    Optional
)

from .models import (
    Base,
    CategorySong,
    Songs,
    PiggyBankKTD,
    PiggyBankGroupsForKTD,
    PiggyBankLegends,
    PiggyBankGroupsForLegend,
    PiggyBankGames,
    PiggyBankGroupForGame,
    PiggyBankTypesGamesForGame,
    RequestTypes,
    Requests,
    SongEvents,
    SongsForSongsEvent
)

from abc import ABC, abstractmethod

from functools import wraps

##### Абстрактные классы #####

class CRUDManagerInterface(ABC):

    @abstractmethod
    def get_data(self):
        pass

    @abstractmethod
    def insert_data(self):
        pass

    @abstractmethod
    def update_data(self):
        pass

    @abstractmethod
    def delete_data(self):
        pass

##############################


##### Классы SQL #####


class CRUDManagerSQL(CRUDManagerInterface):

    @classmethod
    def get_primary_key(
            cls,
            model: Type[DeclarativeBase]
    ):
        name_primary_key = (inspect(model)).primary_key[0].key
        return getattr(model, name_primary_key)

    @classmethod
    def get_model_columns(
            cls,
            model: Type[DeclarativeBase]
    ):
        inspector = inspect(model)
        keys = inspector.columns.keys()

        return keys

    @classmethod
    def check_body(
            cls,
            model: Type[DeclarativeBase],
            body: Union[List[Dict], Dict]
    ) -> List[str]:
        """
        Проверяет наличие переданных ключей в модели
        """
        model_keys = cls.get_model_columns(
            model=model
        )
        error_keys = []

        if isinstance(body, List):
            for row in body:
                error_keys.extend([key for key, value in row.items() if key not in model_keys])
        else:
            error_keys.extend([key for key, value in body.items() if key not in model_keys])

        return error_keys


    @staticmethod
    def check_body_decorator(func):
        @wraps(func)
        async def wrapper(
                *args,
                **kwargs
        ):
            error_keys = []
            model = kwargs.get('model')
            body = kwargs.get('row_filter') or kwargs.get('body')

            if body:
                error_keys = CRUDManagerSQL.check_body(
                    model=model,
                    body=body
                )

            return await func(
                *args,
                **kwargs
            ) if not error_keys else f'Данные ключи отсутствуют в модели: {error_keys}'

        return wrapper

    @classmethod
    @check_body_decorator
    async def get_data(
            cls,
            model: Type[DeclarativeBase],
            row_id: Optional[Union[int| List[int]]] = None,
            row_filter: Optional[Dict] = None
    ) -> List[Base]:

        primary_key = cls.get_primary_key(
            model=model
        )

        async with postgres_db.db_session() as session:
            query = select(model)

            if isinstance(row_id, List):
                query = query.filter(primary_key.in_(row_id))

            elif isinstance(row_id, int):
                query = query.filter(primary_key == row_id)

            if row_filter:
                query = query.filter_by(**row_filter)

            result = await session.execute(query)
            data = result.scalars().all()

            return data

    @classmethod
    @check_body_decorator
    async def delete_data(
            cls,
            model: Type[DeclarativeBase],
            row_id: Union[int | List[int]],
            row_filter: Optional[Dict] = None
    ) -> List[int]:

        async with postgres_db.db_session() as session:
            rows = await cls.get_data(
                model=model,
                row_id=row_id,
                row_filter=row_filter
            )

            if not rows:
                return []

            for row in rows:
                await session.delete(row)

            try:
                await session.commit()
                if isinstance(row_id, List):
                    return row_id
                else:
                    return [row_id]

            except Exception as e:
                logger.error(f'Возникла ошибка при удалении {e}')
                session.rollback()
                return []


    @classmethod
    @check_body_decorator
    async def insert_data(
            cls,
            model: Type[DeclarativeBase],
            body: Union[List[Dict], Dict]
    ) -> List[Dict]:
        data = [model(**item) for item in (body if isinstance(body, list) else [body])]

        async with postgres_db.db_session() as session:
            async with session.begin():
                try:
                    session.add_all(data)
                    await session.flush()
                    return [row.to_dict() for row in data]

                except Exception as e:
                    logger.error(f'Возникала непредвиденная ошибка при вставке {e}')
                    return []


    @classmethod
    @check_body_decorator
    async def update_data(
            cls,
            model: Type[DeclarativeBase],
            row_id: int,
            body: Dict
    ) -> bool:
        primary_key = cls.get_primary_key(
            model=model
        )

        async with postgres_db.db_session() as session:
            query = update(model).filter(primary_key == row_id).values(**body)
            await session.execute(query)

            try:
                await session.commit()
                return True

            except Exception as e:
                logger.error(f'Возникала непредвиденная ошибка при обновлении {e}')
                session.rollback()
                return False

    @classmethod
    async def search_by_title(
            cls,
            title_search
    ):
        async def get_data_with_key(key, model, column_view):
            # Получаем данные а затем фильтруем их по поисковой строке
            data = await cls.get_data(model=model)
            filtered_data = [row for row in data if fuzz.WRatio(getattr(row, column_view).lower(), title_search) > 60]

            return key, filtered_data

        models_search = {
            'songs': {'model': Songs, 'column_view': 'title'},
            'ktds': {'model': PiggyBankKTD, 'column_view': 'title'},
            'legends': {'model': PiggyBankLegends, 'column_view': 'title'},
            'games': {'model': PiggyBankGames, 'column_view': 'title'}
        }

        tasks = [
            get_data_with_key(
                key=key,
                model=model_data['model'],
                column_view=model_data['column_view']
            )
            for key, model_data in models_search.items()
        ]

        result = dict(await asyncio.gather(*tasks))

        # Перед возвратом удаляем пустые ключи
        return result

    @classmethod
    async def insert_request(
            cls,
            request_type_title: str,
            body: Union[List[RequestCreate], RequestCreate]
    ):
        if not (request_type := await cls.get_data(
            model=RequestTypes,
            row_filter={
                'title': request_type_title
            }
        )):
            return

        if isinstance(body, Dict):
            body = [body]


        for request in body:
            request_data = dict(request)
            request_data['id_request_type'] = request_type[0].id

            await cls.insert_data(
                model=Requests,
                body=request_data
            )


class SongCruds(CRUDManagerSQL):

    @classmethod
    async def get_all_songs_by_category(
            cls
    ) -> List[Songs]:

        async with postgres_db.db_session() as session:
            query = select(CategorySong).join(Songs, CategorySong.id == Songs.category, isouter=True)
            query_result = await session.execute(query)
            data = query_result.scalars().all()

            return data

    @classmethod
    async def search_all_songs_by_title(
            cls,
            title_song: str
    ) -> List[Songs]:

        all_songs = await cls.get_data(
            model=Songs,
        )

        return [song for song in all_songs if fuzz.WRatio(song.title, title_song) > 75]


class KTDCruds(CRUDManagerSQL):

    @classmethod
    async def insert_ktd_transaction(
            cls,
            ktds: List[pb_schemes.PiggyBankBaseStructureCreate]
    ) -> List[Dict]:
        new_ktds = []
        async with postgres_db.db_session() as session:

            try:
                async with session.begin():
                    for data in ktds:
                        item_data = PiggyBankKTD(
                            title=data.title,
                            description=data.description,
                        )

                        session.add(item_data)

                        session.add_all(
                            [
                                PiggyBankGroupsForKTD(
                                    group_id=g_id,
                                    ktd_id=item_data.id
                                ) for g_id in data.group_id
                            ]
                        )

                        await session.flush()
                        new_ktds.append(item_data.to_dict())

            except Exception as e:
                logger.error(f'Возникла неожиданная ошибка при создании КТД {e}')
                await session.rollback()

        return new_ktds

    @classmethod
    async def get_ktd_by_group(
            cls,
            group_id: int
    ) -> List[PiggyBankKTD]:

        async with postgres_db.db_session() as session:
            query = select(PiggyBankKTD).where(
                PiggyBankKTD.rel_groups.any(PiggyBankGroupsForKTD.group_id == group_id)
            )

            result = await session.execute(query)
            data = result.scalars().all()

            return data


class LegendCruds(CRUDManagerSQL):

    @classmethod
    async def insert_legend_transaction(
            cls,
            legends: List[pb_schemes.PiggyBankBaseStructureCreate]
    ) -> List[Dict]:
        new_legends = []
        async with postgres_db.db_session() as session:

            try:
                async with session.begin():
                    for data in legends:
                        item_data = PiggyBankLegends(
                            title=data.title,
                            description=data.description,
                        )

                        session.add(item_data)

                        session.add_all(
                            [
                                PiggyBankGroupsForLegend(
                                    group_id=g_id,
                                    legend_id=item_data.id
                                )
                                for g_id in data.group_id
                            ]
                        )

                        await session.flush()
                        new_legends.append(item_data.to_dict())

            except Exception as e:
                logger.error(f'При создании легенды возникла ошибка: {e}')

        return new_legends

    @classmethod
    async def get_legends_by_group(
            cls,
            group_id: int
    ) -> List[PiggyBankLegends]:

        async with postgres_db.db_session() as session:
            query = select(PiggyBankLegends).where(
                PiggyBankLegends.rel_groups.any(PiggyBankGroupsForLegend.group_id == group_id)
            )

            result = await session.execute(query)
            data = result.scalars().all()

            return data


class GameCruds(CRUDManagerSQL):


    @classmethod
    async def insert_game_transaction(
            cls,
            games: List[pb_schemes.PiggyBankGameCreate]
    ) -> List[Dict]:
        new_games = []

        async with postgres_db.db_session() as session:

            try:
                async with session.begin():

                    for game in games:
                        game_data = PiggyBankGames(
                            title=game.title,
                            description=game.description
                        )

                        session.add(game_data)

                        session.add_all(
                            [
                                PiggyBankTypesGamesForGame(
                                    type_id=type_id,
                                    game_id=game_data.id
                                ) for type_id in game.type_id
                            ]
                        )

                        session.add_all(
                            [
                                PiggyBankGroupForGame(
                                    group_id=group_id,
                                    game_id=game_data.id
                                ) for group_id in game.group_id
                            ]
                        )
                        await session.flush()
                        new_games.append(game_data.to_dict())

                        await session.flush()

            except Exception as e:
                logger.error(f'Возникла ошибка при создании игры {e}')

        return new_games

    @classmethod
    async def get_game_by_group_type(
            cls,
            group_id: int,
            type_id: int
    ) -> List[PiggyBankGames]:

        async with postgres_db.db_session() as session:
            query = select(PiggyBankGames).where(
                and_(

                    PiggyBankGames.rel_types_for_game.any(PiggyBankTypesGamesForGame.type_id == type_id),
                    PiggyBankGames.rel_groups_for_game.any(PiggyBankGroupForGame.group_id == group_id)

                )
            )

            result = await session.execute(query)
            data = result.scalars().all()

            return data


    @classmethod
    async def check_available_game(
            cls,
            title: str,
            type_ids: List[int],
            group_ids: List[int],
    ) -> pb_schemes.IntersectionGroupTypeIds:
        '''
        Функция получает уже созданные type_id и group_id на игру.
        Сверяет с параметрами и если все созданные ids есть в параметрах, то считаем что такая игра уже есть
        '''
        async with postgres_db.db_session() as session:

            query = select(PiggyBankGames).filter(PiggyBankGames.title == title).options(
                selectinload(PiggyBankGames.rel_types_for_game),
                selectinload(PiggyBankGames.rel_groups_for_game),
            )

            result = await session.execute(query)
            data = result.scalars().first()

            if not data:
                return pb_schemes.IntersectionGroupTypeIds (
                group_ids=[],
                type_ids=[]
            )

            available_group_ids = [row.group_id for row in data.rel_groups_for_game]
            available_type_ids = [row.type_id for row in data.rel_types_for_game]

            new_type_ids = list(set(available_type_ids).intersection(set(type_ids)))
            new_group_ids = list(set(available_group_ids).intersection(set(group_ids)))

            return pb_schemes.IntersectionGroupTypeIds(
                group_ids=new_group_ids,
                type_ids=new_type_ids
            )


class SongEventCruds(CRUDManagerSQL):
    @classmethod
    async def insert_song_event(
        cls,
        song_events: List[SongEventCreateWithSong]
    ) -> List[Dict]:

        new_events = []

        async with postgres_db.db_session() as session:

            try:
                async with session.begin():

                    for song_event in song_events:
                        song_ids = song_event.song_ids if song_event.song_ids else []
                        song_event = SongEventCreate(
                            **song_event.model_dump()
                        )

                        song_event.end_dt = song_event.start_dt + timedelta(days=song_event.duration)

                        event_data = SongEvents(
                            **song_event.model_dump()
                        )

                        session.add(event_data)
                        await session.flush()

                        session.add_all(
                            [
                                SongsForSongsEvent(
                                    song_id=song_id,
                                    event_id=event_data.id
                                ) for song_id in song_ids
                            ]
                        )

                        new_events.append(event_data.to_dict())
                        await session.flush()

            except Exception as e:
                logger.error(f'Возникла неожиданная ошибка при создании КТД {e}')

        return new_events

    @classmethod
    async def get_song_event(
        cls,
        is_actual: bool = False,
        row_id: Optional[Union[int | List[int]]] = None,
    ):
        async with postgres_db.db_session() as session:
            query = select(SongEvents).options(
                selectinload(SongEvents.rel_songs)
            )

            if isinstance(row_id, List):
                query = query.filter(SongEvents.id.in_(row_id))

            elif isinstance(row_id, int):
                query = query.filter(SongEvents.id == row_id)

            if is_actual:
                query = query.filter(SongEvents.end_dt > datetime.now())

            result = await session.execute(query)
            data = result.scalars().all()

            return data

