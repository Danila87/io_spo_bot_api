from fastapi import APIRouter, HTTPException
from fastapi.params import Query, Body
from fastapi.responses import JSONResponse

from schemas.service import RequestCreate
from schemas import song as song_schemes

from database import models
from database.cruds import CRUDManagerSQL, SongCruds

from typing import List, Optional, Annotated
from schemas.responses import ResponseData, Meta, ResponseDelete

SONG_CATEGORY_TAG = 'song_category'
SONG_TAG = 'song'

song_router = APIRouter(prefix='/songs', tags=['song_methods'])

@song_router.post(
    path='/',
    tags=['song'],
    summary='Добавить песню',
)
async def insert_song(
        song: Annotated[song_schemes.SongCreate, Body(
            description="Тело песни"
        )]
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
            detail='Данная песня уже существует в БД'
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


@song_router.get(
    path='/',
    tags=[SONG_TAG],
    response_model=ResponseData[song_schemes.SongResponse],
    summary='Получить песни'
)
async def get_songs(
        song_ids: Annotated[List[int], Query(
            description="Список id песен",
        )] = None,
        user_id: Annotated[Optional[int], Query(
            description="Id пользователя telegram"
        )] = None,
        category_id: Annotated[Optional[int], Query(
            description="Id категории, песни которой нужно получить"
        )] = None
):

    row_filter = {"category": category_id} if category_id else None

    songs = await CRUDManagerSQL.get_data(
        model=models.Songs,
        row_id=song_ids,
        row_filter=row_filter
    )

    await CRUDManagerSQL.insert_request(
        request_type_title='Песня',
        body=[RequestCreate(
            id_content=song.id,
            id_user=user_id,
            content_display_value=song.title
        ) for song in songs]
    )

    return ResponseData(
        data=songs,
        meta=Meta(total=len(songs))
    )

@song_router.get(
    path='/search/',
    tags=[SONG_TAG],
    response_model=ResponseData[song_schemes.SongResponse],
    summary='Поиск песен по названию'
)
async def search_songs_by_title(
    title_song: Annotated[str, Query(
        description="Текст, по которому осуществляется поиск"
    )],
):

    songs = await SongCruds.search_all_songs_by_title(
        title_song=title_song
    )

    return ResponseData(
        data=songs,
        meta=Meta(total=len(songs))
    )


@song_router.put(
    path='/',
    tags=[SONG_TAG],
    summary='Обновить песню'
)
async def update_song_by_id(
        song_id: Annotated[int, Query(
            description="Id песни"
        )],
        song: Annotated[song_schemes.SongCreate, Body(
            description="Тело песни"
        )]
):

    return await CRUDManagerSQL.update_data(
        model=models.Songs,
        row_id=song_id,
        body=dict(song)
    )


@song_router.delete(
    path='/',
    tags=[SONG_TAG],
    response_model=ResponseDelete,
    summary='Удалить песню'
)
async def delete_song_by_id(
        song_id: Annotated[int, Query(
            description="Id песни"
        )],
):

    if await CRUDManagerSQL.delete_data(
            model=models.Songs,
            row_id=song_id
    ):
        return ResponseDelete()

    raise HTTPException(
        status_code=500,
        detail='Возникла ошибка при удалении'
    )


@song_router.get(
    path='/categories/',
    tags=[SONG_CATEGORY_TAG],
    response_model=ResponseData[song_schemes.CategorySongResponse],
    summary='Получить категории песен'
)
async def get_categories(
    category_ids: Annotated[List[int], Query(
        description="Id категорий"
    )] = None,
    only_parents: Annotated[bool, Query(
        description="Вернуть категории у которых нет родителя. В случае true из переданных category_ids вернет только те, у которых нет родителя"
    )] = False
):
    row_filter = {"parent_id": None} if only_parents else {}

    categories = await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_id=category_ids,
        row_filter=row_filter
    )

    return ResponseData(
        data=categories,
        meta=Meta(total=len(categories))
    )

@song_router.get(
    path='/categories/childrens/',
    tags=[SONG_CATEGORY_TAG],
    response_model=ResponseData[song_schemes.CategorySongResponse],
    summary='Получить дочерние категории категорий'
)
async def get_childs_categories(
        id_category: Annotated[int, Query(
            description="Id категории, детей которой нужно получить"
        )] = None
):

    categories = await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_filter={
            'parent_id': id_category
        }
    )

    return ResponseData(
        data=categories,
        meta=Meta(total=len(categories))
    )


@song_router.post(
    path='/categories/',
    tags=[SONG_CATEGORY_TAG],
    summary='Добавить категорию'
)
async def insert_category(
        category: Annotated[song_schemes.CategorySongCreate, Body()]
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


@song_router.put(
    path='/categories/',
    tags=[SONG_CATEGORY_TAG],
    summary='Обновить категорию'
)
async def update_category(
    category_id: Annotated[int, Query(
        description="Id категории"
    )],
    category: Annotated[song_schemes.CategorySongCreate, Body(
        description="Тело категории"
    )]
):
    # TODO добавить схему
    pass


@song_router.delete(
    path='/categories/',
    tags=[SONG_CATEGORY_TAG],
    summary='Удалить категорию'
)
async def delete_category(
        category_id: Annotated[int, Query(
            description="Id категории"
        )]
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
