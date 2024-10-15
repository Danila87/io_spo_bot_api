from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from pydantic_schemes.Song import schemes as song_schemes

from database import models
from database.cruds import CRUDManagerSQL, SongCruds

from typing import List
from functools import wraps

song_router = APIRouter(prefix='/song', tags=['all_song_methods'])

@song_router.post('/', tags=['song'])
async def insert_song(
        song: song_schemes.Song
) -> JSONResponse:

    if await CRUDManagerSQL.insert_data(
            model=models.Songs,
            body=dict(song)
    ):
        return JSONResponse(
            status_code=201,
            content={'message': 'Песня успешно добавлена!'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка на сервере'
    )


@song_router.get('/', tags=['song'])
async def get_song(
        song_id: int
) -> song_schemes.SongResponse:

    if not (data := await CRUDManagerSQL.get_data(
            model=models.Songs,
            row_id=song_id,
    )):
        raise HTTPException(
            status_code=404,
            detail='Не найдена песня с указанным id'
        )

    return song_schemes.SongResponse(
        **data[0].to_dict()
    )


@song_router.put('/', tags=['song'])
async def update_song_by_id(song_id: int, song: song_schemes.Song):
    """
    Обновляем песню по ее id
    :param song_id: id обновляемой песни
    :param song: новый объект песни, на который будет происходить обновление
    :return:
    """

    return await CRUDManagerSQL.update_data(
        model=models.Songs,
        row_id=song_id,
        body=dict(song)
    )


@song_router.delete('/', tags=['song'])
async def delete_song_by_id(
        song_id: int
) -> JSONResponse:
    """
    Удаляем песню по ее id
    :param song_id: id искомой песни
    :return: HTTPException с статус кодом и detail
    """

    if await CRUDManagerSQL.delete_data(
            model=models.Songs,
            row_id=song_id
    ):
        return JSONResponse(
            status_code=200,
            content={'message': 'Песня успешно удалена'}
        )

    raise HTTPException(
        status_code=500,
        detail='Возникла ошибка при удалении'
    )


@song_router.get('/songs', tags=['song'])
async def get_songs() -> List[song_schemes.SongResponse]:
    """
    Получаем все песни
    :return: Список словарей всех песен
    """

    data = await CRUDManagerSQL.get_data(
        model=models.Songs
    )

    return [
        song_schemes.SongResponse(**row.to_dict()) for row in data
    ]


@song_router.get('/songs/by_category', tags=['song', 'category'])
async def get_songs_by_category() -> List[song_schemes.SongsByCategory]:
    """
    Получаем категорию и все песни которые ей принадлежат
    :return: Songs - Список категорий, которые в свою очередь содержат список песен
    """
    data = await SongCruds.get_all_songs_by_category()

    return [
        song_schemes.SongsByCategory(**row.to_dict()) for row in data
    ]


@song_router.post('/songs/search_title', tags=['song'])
async def search_songs_by_title(
        request_data: song_schemes.SongSearch
) -> List[song_schemes.SongResponse]:
    """
    Поиск песни по ее названию. В поиске используется алгоритм расстояния Левенштейна
    :param request_data:
    :return: Список словарей подходящих песен
    """

    data = await SongCruds.search_all_songs_by_title(
        title_song=request_data.title_song
    )

    return [
        song_schemes.SongResponse(**row.to_dict()) for row in data
    ]


@song_router.post('/categories/', tags=['category'])
async def insert_category(
        category: song_schemes.CategorySong
) -> JSONResponse:
    """
    Добавляем категорию. Сначала проходит верификацию на отсутствие такой же категории в бд
    :param category: Словарь категории
    :return: HTTPException со статус кодом и detail
    """

    if await CRUDManagerSQL.insert_data(
            model=models.CategorySong,
            body=dict(category)
    ):

        return JSONResponse(
            status_code=201,
            content={'message':'Категория успешно добавлена'}
        )

    raise HTTPException(
        status_code=500,
        detail={'Произошла ошибка при создании категории.'}
    )

@song_router.get('/categories/', tags=['category'])
async def get_category_by_id(
        category_id: int
) -> song_schemes.CategorySongResponse:
    """
    Получаем категорию по ее id
    :param category_id: id искомой категории
    :return: category - словарь категории
    """

    if not (data := await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_id=category_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Не найдена категория под указанным id'
        )

    return song_schemes.CategorySongResponse(**data[0].to_dict())


@song_router.put('/categories/', tags=['category'])
async def update_category_by_id(category_id: int):
    """
    Изменяем категорию по ее id
    :param category_id: id изменяемой категории
    :return:
    """
    # TODO добавить схему
    pass


@song_router.delete('/categories/', tags=['category'])
async def delete_category_by_id(
        category_id: int
) -> JSONResponse:
    """
    Удаляем категорию по ее id
    :param category_id: id удаляемой категории
    :return: HTTPException - Результат удаления. Возвращает статус код и detail
    """

    if await CRUDManagerSQL.delete_data(
            model=models.CategorySong,
            row_id=category_id
    ):

        return JSONResponse(
            status_code=200,
            content={'message':'Категория успешно удалена'}
        )

    raise HTTPException(
        status_code=500,
        detail='Произошла ошибка на сервере'
    )


@song_router.get('/categories/mains', tags=['category'])
async def get_main_chapters() -> List[song_schemes.CategorySongResponse]:
    data = await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_filter={
            'parent_id': None
        }
    )

    return [
        song_schemes.CategorySongResponse(**row.to_dict()) for row in data
    ]


@song_router.get('/categories/get_childs/', tags=['category'])
async def get_child_chapters(
        id_category: int
) -> List[song_schemes.CategorySongResponse]:
    data = await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_filter={
            'parent_id': id_category
        }
    )

    return [
        song_schemes.CategorySongResponse(**row.to_dict()) for row in data
    ]


@song_router.get('/by_category/', tags=['category'])
async def get_songs_by_category(
        category_id: int
) -> List[song_schemes.SongResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.Songs,
        row_filter={
            'category_id': category_id
        }
    )

    return [
        song_schemes.SongResponse(**row.to_dict()) for row in data
    ]
