from pkgutil import get_data

from certifi import where

from . import models
from .connection import postgres_db

from pydantic import BaseModel

from pydantic_schemes.Song import schemes as song_schemes
from pydantic_schemes.PyggyBank import schemes as pb_schemes

from sqlalchemy import select, and_, inspect
from sqlalchemy.orm import selectinload, DeclarativeBase

from fastapi.encoders import jsonable_encoder

from fuzzywuzzy import fuzz

from typing import Literal, Type, TypeVar, List, Union, Dict, Optional
from abc import ABC, abstractmethod

any_schema = TypeVar('any_schema', bound=BaseModel)


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


class CRUDManagerSQL:

    @staticmethod
    def get_primary_key(
            model: Type[DeclarativeBase]
    ):
        name_primary_key = (inspect(model)).primary_key[0].key
        return getattr(model, name_primary_key)

    @staticmethod
    def get_model_columns(
            model: Type[DeclarativeBase]
    ):
        inspector = inspect(model)
        keys = inspector.columns.keys()

        return keys

    @staticmethod
    def check_body(
            model: Type[DeclarativeBase],
            body: Dict
    ) -> bool:
        model_keys = CRUDManagerSQL.get_model_columns(
            model=model
        )

        for key, value in body.items():
            if key not in model_keys:
                return False

        return True

    @staticmethod
    async def get_data(
            model: Type[DeclarativeBase],
            row_id: Optional[Union[int| List[int]]] = None,
            row_filter: Optional[Dict] = None
    ):

        primary_key = CRUDManagerSQL.get_primary_key(
            model=model
        )

        async with postgres_db.db_session() as session:
            query = select(model)

            if isinstance(row_id, List):
                query = query.filter(primary_key.in_(row_id))

            elif isinstance(row_id, int):
                query = query.filter(primary_key == row_id)

            if row_filter and CRUDManagerSQL.check_body(
                model=model,
                body=row_filter
            ):
                query = query.filter_by(**row_filter)

            result = await session.execute(query)
            data = result.scalars().all()

            return data

    @staticmethod
    async def delete_data(
            model: Type[DeclarativeBase],
            row_id: Optional[Union[int | List[int]]] = None,
            row_filter: Optional[Dict] = None
    ):
        async with postgres_db.db_session() as session:

            rows = await CRUDManagerSQL.get_data(
                model=model,
                row_id=row_id,
                row_filter=row_filter
            )

            for row in rows:
                await session.delete(row)

            await session.commit()


    @staticmethod
    async def insert_data(model, **kwargs) -> bool:
        async with postgres_db.db_session() as session:
            data = model(**kwargs)
            session.add(data)

            await session.commit()

            return True


class SongCruds:

    @staticmethod
    async def get_all_songs_by_category() -> list[song_schemes.SongsByCategory]:

        async with postgres_db.db_session() as session:
            query = select(models.CategorySong).options(selectinload(models.CategorySong.rel_songs))

            result = await session.execute(query)
            result = result.scalars().all()

            return [song_schemes.SongsByCategory.model_validate(jsonable_encoder(item)) for item in result]

    @staticmethod
    async def search_all_songs_by_title(title_song: str) -> list[song_schemes.SongSearch] | bool:

        all_songs = await CRUDManagerSQL.get_data(
            model=models.Songs,
        )

        result_songs = []

        for song in all_songs:

            if fuzz.WRatio(song.title, title_song) < 75:
                continue

            result_songs.append(
                song_schemes.SongSearch.model_validate({
                    'id_song': song.id,
                    'title_song': song.title
                })
            )

        if not result_songs:
            return False

        return result_songs


class PiggyBankCruds:

    @staticmethod
    async def get_game_by_group_type(group_id: int, type_id: int) -> list[pb_schemes.PiggyBankGameResponse]:

        async with postgres_db.db_session() as session:
            query = select(models.PiggyBankGames).where(
                and_(

                    models.PiggyBankGames.rel_types_for_game.any(models.PiggyBankTypesGamesForGame.type_id == type_id),
                    models.PiggyBankGames.rel_groups_for_game.any(models.PiggyBankGroupForGame.group_id == group_id)

                )
            )

            result = await session.execute(query)
            data = result.scalars().all()

            return [pb_schemes.PiggyBankGameResponse.model_validate(jsonable_encoder(item)) for item in data]

    @staticmethod
    async def insert_game_transaction(game: pb_schemes.PiggyBankGameCreate):

        data = dict(game)

        game_data = {
            'title': data['title'],
            'description': data['description'],
            'file_path': data['file_path']
        }

        type_id, group_id = data['type_id'], data['group_id']

        async with postgres_db.db_session() as session:

            async with session.begin():

                try:

                    game_data = models.PiggyBankGames(**game_data)

                    session.add(game_data)
                    await session.flush()
                    await session.refresh(game_data)

                    session.add(models.PiggyBankTypesGamesForGame(type_id=type_id, game_id=game_data.id))
                    session.add(models.PiggyBankGroupForGame(group_id=group_id, game_id=game_data.id))

                    await session.flush()

                    return True

                except:
                    await session.rollback()
                    return False

    @staticmethod
    async def insert_ktd_or_legend_transaction(
            item_model,
            item_type: Literal['ktd', 'legend'],
            data: pb_schemes.PiggyBankBaseStructureCreate) -> bool:

        data = dict(data)

        item_data = {
            'title': data['title'],
            'description': data['description'],
            'file_path': data['file_path']
        }

        group_id = data['group_id']

        async with postgres_db.db_session() as session:
            async with session.begin():

                try:
                    item_data = item_model(**item_data)

                    session.add(item_data)
                    await session.flush()
                    await session.refresh(item_data)

                    if item_type == 'ktd':
                        session.add(models.PiggyBankGroupsForKTD(group_id=group_id, ktd_id=item_data.id))
                    elif item_type == 'legend':
                        session.add(models.PiggyBankGroupsForLegend(group_id=group_id, legend_id=item_data.id))

                    await session.flush()
                    
                    return True
                
                except Exception as e:
                    await session.rollback()
                    return False

    @staticmethod
    async def get_legends_or_krd_by_group(item_model,
                                          mtm_model,
                                          group_id: int) -> list[pb_schemes.PiggyBankBaseStructureResponse]:

        async with postgres_db.db_session() as session:
            query = select(item_model).where(
                item_model.rel_groups.any(mtm_model.group_id == group_id)
            )

            result = await session.execute(query)
            data = result.scalars().all()

            return [pb_schemes.PiggyBankBaseStructureResponse.model_validate(jsonable_encoder(item)) for item in data]
