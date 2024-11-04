from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from pydantic_schemes.Song import schemes as song_schemes

from database import models
from database.cruds import CRUDManagerSQL, SongCruds

from typing import List


song_router = APIRouter(prefix='/song', tags=['all_song_methods'])

# def check_existence(model, **fields):
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(*args, **kwargs):
#             if await CRUDManagerSQL.get_data(model=model, row_filter=fields):
#                 raise HTTPException(
#                     status_code=400,
#                     detail=f'Запись уже существует в БД'
#                 )
#             return await func(*args, **kwargs)
#         return wrapper
#     return decorator

@song_router.post('/', tags=['song'])
async def insert_song(
        song: song_schemes.SongCreate
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.Songs,
        row_filter={
            'title': song.title,
            'category': song.category,
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная категория уже существует в БД'
        )

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
async def update_song_by_id(
        song_id: int,
        song: song_schemes.SongCreate
):

    return await CRUDManagerSQL.update_data(
        model=models.Songs,
        row_id=song_id,
        body=dict(song)
    )


@song_router.delete('/', tags=['song'])
async def delete_song_by_id(
        song_id: int
) -> JSONResponse:

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

    data = await CRUDManagerSQL.get_data(
        model=models.Songs
    )

    return [
        song_schemes.SongResponse(**row.to_dict()) for row in data
    ]


@song_router.get('/songs/by_category', tags=['song', 'category'])
async def get_songs_by_category() -> List[song_schemes.SongsByCategoryResponse]:

    data = await SongCruds.get_all_songs_by_category()

    return [
        song_schemes.SongsByCategoryResponse(**row.to_dict()) for row in data
    ]


@song_router.post('/songs/search_title', tags=['song'])
async def search_songs_by_title(
        request_data: song_schemes.SongSearch
) -> List[song_schemes.SongResponse]:

    data = await SongCruds.search_all_songs_by_title(
        title_song=request_data.title_song
    )

    return [
        song_schemes.SongResponse(**row.to_dict()) for row in data
    ]


@song_router.post('/categories/', tags=['category'])
async def insert_category(
        category: song_schemes.CategorySongCreate
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_filter={
            'name': category.name
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная категория уже существует в БД'
        )

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

    # TODO добавить схему
    pass


@song_router.delete('/categories/', tags=['category'])
async def delete_category_by_id(
        category_id: int
) -> JSONResponse:

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


@song_router.get('/categories/get_children/', tags=['category'])
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
