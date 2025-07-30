from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.params import Query, Body

from schemas.service import RequestCreate
from schemas import song as song_schemes

from database import models
from database.cruds import CRUDManagerSQL, SongCruds

from typing import List, Optional, Annotated
from schemas.responses import ResponseData, Meta, ResponseDelete, ResponseCreate

from common_lib.background_tasks import insert_user_requests

SONG_CATEGORY_TAG = 'song_category'
SONG_TAG = 'song'

song_router = APIRouter(prefix='/songs', tags=['song_methods'])

@song_router.post(
    path='/',
    tags=['song'],
    summary='Добавить песню',
    response_model=ResponseCreate[song_schemes.SongResponse]
)
async def insert_song(
        songs: Annotated[
            List[song_schemes.SongCreate],
            Body(
                description="Тело песни"
            )
        ]
):

    for song in songs:
        if await CRUDManagerSQL.get_data(
            model=models.Songs,
            row_filter={
                'title': song.title,
                'category': song.category,
            }
        ):
            raise HTTPException(
                status_code=500,
                detail=f'Данная песня уже существует в БД. Песня {song.title}'
            )

    if data := await CRUDManagerSQL.insert_data(
            model=models.Songs,
            body=[song.model_dump() for song in songs]
    ):
        return ResponseCreate(
            data=data,
            meta=Meta(total=len(data))
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
    bg_task: BackgroundTasks,
    song_ids: Annotated[
        List[int],
        Query(
            description="Список id песен",
        )
    ] = None,
    tg_user_id: Annotated[
        Optional[int],
        Query(
            description="Id пользователя telegram"
        )
    ] = None,
    category_id: Annotated[
        Optional[int],
        Query(
            description="Id категории, песни которой нужно получить"
        )
    ] = None,
    is_create_user_request: Annotated[
        bool,
        Query(
            description="Создать записи в таблице запросов пользователей"
        )
    ] = False,
):

    row_filter = {"category": category_id} if category_id else None

    songs = await CRUDManagerSQL.get_data(
        model=models.Songs,
        row_id=song_ids,
        row_filter=row_filter
    )

    if is_create_user_request and tg_user_id:
        bg_task.add_task(
            func=insert_user_requests,
            tg_user_id=tg_user_id,
            data=songs
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
    title_song: Annotated[
        str,
        Query(
            description="Текст, по которому осуществляется поиск"
        )
    ],
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
        song_id: Annotated[
            int,
            Query(
                description="Id песни"
            )
        ],
        song: Annotated[
            song_schemes.SongCreate,
            Body(
                description="Тело песни"
            )
        ]
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
    song_ids: Annotated[
        List[int],
        Query(
            description="Id песни"
        )
    ],
):

    deleted_ids = await CRUDManagerSQL.delete_data(
            model=models.Songs,
            row_id=song_ids
    )
    return ResponseDelete(
        data=deleted_ids,
        meta=Meta(total=len(deleted_ids))
    )


@song_router.get(
    path='/categories/',
    tags=[SONG_CATEGORY_TAG],
    response_model=ResponseData[song_schemes.CategorySongResponse],
    summary='Получить категории песен'
)
async def get_categories(
    category_ids: Annotated[
        List[int],
        Query(
            description="Id категорий"
        )
    ] = None,
    only_parents: Annotated[
        bool,
        Query(
            description="Вернуть категории у которых нет родителя. В случае true из переданных category_ids вернет только те, у которых нет родителя"
        )
    ] = False
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
        id_category: Annotated[
            int,
            Query(
                description="Id категории, детей которой нужно получить"
            )
        ] = None
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
    summary='Добавить категорию',
    response_model=ResponseCreate[song_schemes.CategorySongResponse]
)
async def insert_category(
        categories: Annotated[
            List[song_schemes.CategorySongCreate],
            Body(
                description="Тело категории"
            )
        ]
):

    for category in categories:
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

    if new_categories := await CRUDManagerSQL.insert_data(
            model=models.CategorySong,
            body=[category.model_dump() for category in categories]
    ):

        return ResponseCreate(
            data=new_categories,
            meta=Meta(total=len(new_categories))
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
    summary='Удалить категорию',
    response_model=ResponseDelete
)
async def delete_category(
        category_ids: Annotated[
            List[int],
            Query(
                description="Id категории"
            )
        ]
):

    deleted_ids = await CRUDManagerSQL.delete_data(
            model=models.CategorySong,
            row_id=category_ids
    )

    return ResponseDelete(
        deleted_ids=deleted_ids,
        meta=Meta(total=len(deleted_ids)),
    )

