from fastapi import APIRouter, HTTPException
from fastapi.params import Query, Body
from fastapi.responses import JSONResponse

from schemas.service import RequestCreate
from schemas import song as song_schemes

from database import models
from database.cruds import CRUDManagerSQL, SongCruds

from typing import List, Optional, Annotated
from schemas.responses import ResponseData, Meta, ResponseDelete

song_router = APIRouter(prefix='/songs', tags=['all_song_methods'])

@song_router.post(path='/', tags=['song'])
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
    '/',
    tags=['song'],
    response_model=ResponseData[song_schemes.SongResponse]
)
async def get_songs(
        song_ids: Annotated[List[int], Query(
            description="Список id песен",
        )] = None,
        user_id: Annotated[Optional[int], Query(
            description="Id пользователя telegram"
        )] = None,
):

    if not (songs := await CRUDManagerSQL.get_data(
            model=models.Songs,
            row_id=song_ids,
    )):
        raise HTTPException(
            status_code=404,
            detail='Не найдена песня с указанным id'
        )

    # await CRUDManagerSQL.insert_request(
    #     request_type_title='Песня',
    #     body=RequestCreate(
    #         id_content=data[0].id,
    #         id_user=user_id,
    #         content_display_value=data[0].title
    #     )
    # )

    return ResponseData(
        data=songs,
        meta=Meta(total=len(songs))
    )


@song_router.put('/', tags=['song'])
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
    tags=['song'],
    response_model=ResponseDelete
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
    tags=['category'],
    response_model=ResponseData[song_schemes.CategorySongResponse]
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
    tags=['category'],
    response_model=ResponseData[song_schemes.CategorySongResponse]
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

@song_router.get('/songs/by_category', tags=['song', 'category'])
async def get_songs_by_category() -> List[song_schemes.SongsByCategoryResponse]:

    data = await SongCruds.get_all_songs_by_category()

    return [
        song_schemes.SongsByCategoryResponse(**row.to_dict()) for row in data
    ]

@song_router.get('/songs/by_category/', tags=['song', 'category'])
async def get_songs_by_category(
        category_id: int
) -> List[song_schemes.SongResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.Songs,
        row_filter={
            'category': category_id
        }
    )

    return [
        song_schemes.SongResponse(**row.to_dict()) for row in data
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