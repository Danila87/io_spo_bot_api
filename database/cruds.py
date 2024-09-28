from __future__ import annotations

from . import models
from .connection import postgres_db

from pydantic import BaseModel

from pydantic_schemes import schemes
from pydantic_schemes.Song import schemes as song_schemes
from pydantic_schemes.PyggyBank import schemes as pb_schemes

from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload, DeclarativeBase

from fastapi.encoders import jsonable_encoder

from fuzzywuzzy import fuzz

from typing import Literal, Type, TypeVar

any_schema = TypeVar('any_schema', bound=BaseModel)


class BaseCruds:

    @staticmethod
    async def get_all_data(model: Type[DeclarativeBase], schema: Type[BaseModel]) -> list[any_schema]:

        async with postgres_db.db_session() as session:
            query = select(model)
            result = await session.execute(query)

            data = result.scalars().all()

            return [schema.model_validate(jsonable_encoder(item)) for item in data]

    @staticmethod
    async def get_data_by_id(model,
                             model_id: int,
                             schema: Type[BaseModel],
                             encode: bool = True, ) -> any_schema | bool:

        async with postgres_db.db_session() as session:

            query = select(model).filter(model.id == model_id)

            result = await session.execute(query)
            data = result.scalar_one_or_none()

            if not data:
                return False

            if encode:
                print(jsonable_encoder(data))
                return schema.model_validate(jsonable_encoder(data))

            return data

    @staticmethod
    async def delete_data_by_id(model, model_id: int) -> bool:

        async with postgres_db.db_session() as session:
            data = await BaseCruds.get_data_by_id(model=model, model_id=model_id, encode=False)

            await session.delete(data)
            await session.commit()

            return True

    @staticmethod
    async def get_data_by_filter(model,
                                 schema: Type[BaseModel],
                                 verify: bool = False,
                                 **kwargs) -> list[any_schema] | bool:

        async with postgres_db.db_session() as session:

            query = select(model).filter_by(**kwargs)
            result = await session.execute(query)

            data = result.scalars().all()

            if verify:

                if len(data) == 0:
                    return False

                return True
            print(jsonable_encoder(data))
            return [schema.model_validate(jsonable_encoder(item)) for item in data]

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

        all_songs = await BaseCruds.get_all_data(model=models.Songs,
                                                 schema=song_schemes.SongResponse)
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
