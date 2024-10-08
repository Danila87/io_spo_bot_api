from .connection import postgres_db

from pydantic_schemes.Song import schemes as song_schemes
from pydantic_schemes.PyggyBank import schemes as pb_schemes

from sqlalchemy import select, and_, inspect, update
from sqlalchemy.orm import DeclarativeBase

from fuzzywuzzy import fuzz

from typing import (
    Type,
    List,
    Union,
    Dict,
    Optional
)

from .models import (
    CategorySong,
    Songs,
    PiggyBankKTD,
    PiggyBankGroupsForKTD,
    PiggyBankLegends,
    PiggyBankGroupsForLegend,
    PiggyBankGames,
    PiggyBankGroupForGame,
    PiggyBankTypesGamesForGame
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
            body: Dict
    ) -> List[str]:
        model_keys = cls.get_model_columns(
            model=model
        )
        return [key for key, value in body.items() if key not in model_keys]


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
    ) -> List[DeclarativeBase]:

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
            row_id: Optional[Union[int | List[int]]] = None,
            row_filter: Optional[Dict] = None
    ) -> bool:

        async with postgres_db.db_session() as session:
            rows = await cls.get_data(
                model=model,
                row_id=row_id,
                row_filter=row_filter
            )

            for row in rows:
                await session.delete(row)

            try:
                await session.commit()
                return True

            except Exception as e:
                print(f'Возникала непредвиденная ошибка при удалении {e}')
                session.rollback()
                return False


    @classmethod
    @check_body_decorator
    async def insert_data(
            cls,
            model: Type[DeclarativeBase],
            body: Union[List[Dict], Dict]
    ) -> bool:

        async with postgres_db.db_session() as session:
            if isinstance(body, List):
                data = [model(**row) for row in body]
            else:
                data = [model(**body)]
            session.add_all(data)

            try:
                await session.commit()
                return True

            except Exception as e:
                print(f'Возникала непредвиденная ошибка при вставке {e}')
                session.rollback()
                return False

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
                print(f'Возникала непредвиденная ошибка при обновлении {e}')
                session.rollback()
                return False


class SongCruds(CRUDManagerSQL):

    @classmethod
    async def get_all_songs_by_category(
            cls
    ) -> list[song_schemes.SongsByCategory]:

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
            data: pb_schemes.PiggyBankBaseStructureCreate
    ) -> bool:

        async with postgres_db.db_session() as session:

            try:
                async with session.begin():
                    item_data = PiggyBankKTD(
                        title=data.title,
                        description=data.description,
                        file_path=data.file_path
                    )

                    session.add(item_data)
                    await session.flush()
                    await session.refresh(item_data)

                    session.add(
                        PiggyBankGroupsForKTD(
                            group_id=data.group_id,
                            ktd_id=item_data.id
                        )
                    )

                    await session.flush()

                    return True

            except Exception as e:
                print(f'Возникла неожиданная ошибка при создании КТД {e}')
                await session.rollback()
                return False

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
            data: pb_schemes.PiggyBankBaseStructureCreate
    ) -> bool:

        async with postgres_db.db_session() as session:

            try:
                async with session.begin():
                    item_data = PiggyBankLegends(
                        title=data.title,
                        description=data.description,
                        file_path=data.file_path
                    )

                    session.add(item_data)
                    await session.flush()
                    await session.refresh(item_data)

                    session.add(
                        PiggyBankGroupsForLegend(
                            group_id=data.group_id,
                            legend_id=item_data.id
                        )
                    )

                    await session.flush()

                    return True

            except Exception as e:
                print(f'При создании легенды возникла ошибка: {e}')
                await session.rollback()
                return False

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
            game: pb_schemes.PiggyBankGameCreate
    ) -> bool:

        async with postgres_db.db_session() as session:

            try:
                async with session.begin():
                    game_data = PiggyBankGames(
                        title=game.title,
                        description=game.description,
                        file_path=game.file_path
                    )

                    session.add(game_data)
                    await session.flush()
                    await session.refresh(game_data)

                    session.add(
                        PiggyBankTypesGamesForGame(
                            type_id=game.type_id,
                            game_id=game_data.id
                        )
                    )
                    session.add(
                        PiggyBankGroupForGame(
                            group_id=game.group_id,
                            game_id=game_data.id
                        )
                    )

                    await session.flush()

                    return True

            except Exception as e:
                print(f'Возникла ошибка при создании игры {e}')
                return False

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

########################