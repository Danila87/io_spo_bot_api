from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pydantic_schemes.Song import schemes as song_schemes

from database import models
from database.cruds import CRUDManagerSQL, SongCruds

song_router = APIRouter(prefix='/song', tags=['all_song_methods'])


@song_router.get('/songs/by_category', tags=['song', 'category'])
async def get_songs_by_category() -> list[song_schemes.SongsByCategory]:
    """
    Получаем категорию и все песни которые ей принадлежат
    :return: Songs - Список категорий, которые в свою очередь содержат список песен
    """

    return await SongCruds.get_all_songs_by_category()


@song_router.get('/songs', tags=['song'])
async def get_songs() -> list[song_schemes.SongResponse]:
    """
    Получаем все песни
    :return: Список словарей всех песен
    """

    return await CRUDManagerSQL.get_data(
        model=models.Songs
    )


@song_router.post('/songs/search_title', tags=['song'])
async def search_songs_by_title(
        request_data: song_schemes.SongSearch
) -> list[song_schemes.SongSearch]:
    """
    Поиск песни по ее названию. В поиске используется алгоритм расстояния Левенштейна
    :param request_data:
    :return: Список словарей подходящих песен
    """

    return await SongCruds.search_all_songs_by_title(
        title_song=request_data.title_song
    )


@song_router.post('/', tags=['song'])
async def insert_song(
        song: song_schemes.Song
) -> JSONResponse:
    """
    Вставляем песню, но перед этим проводим проверку что такой песни в бд нет.
    ВАЖНО: Текст песни должен быть одной строкой где переносы экранированы //n. В сервисных методах есть функция которая правит данный момент
    :param song: Объект песни которую вставляем
    :return: HTTPException с статус кодом и detail
    """

    if await CRUDManagerSQL.insert_data(
            model=models.Songs,
            title=song.title,
            title_search=song.title_search,
            text=song.text,
            file_path=song.file_path,
            category=song.category):
        return JSONResponse(
            status_code=201,
            content={'message': 'Песня успешно добавлена!'}
        )

    return JSONResponse(
        status_code=400,
        content={'message': 'Произошла ошибка на сервере'}
    )


# @song_router.get('/{song_id}', tags=['song'])
# async def get_song(
#         song_id: int
# ) -> Union[song_schemes.SongResponse, JSONResponse, bool]:
#     """
#     Получаем песню по ее id
#     :param song_id: id искомой песни
#     :return: HTTPException в случае если песни нет либо song если песня найдена
#     """
#
#     song = await BaseCruds.get_data_by_id(
#         model=models.Songs,
#         model_id=song_id,
#         schema=song_schemes.SongResponse
#     )
#
#     if not song:
#         return JSONResponse(
#             status_code=400,
#             content={'message': 'Песни не существует'}
#         )
#
#     return song


@song_router.put('/{song_id}', tags=['song'])
async def update_song_by_id(song_id: int, song: song_schemes.Song):
    """
    Обновляем песню по ее id
    :param song_id: id обновляемой песни
    :param song: новый объект песни, на который будет происходить обновление
    :return:
    """
    pass


@song_router.delete('/{song_id}', tags=['song'])
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

    return JSONResponse(
        status_code=500,
        content={'message': 'Возникли проблемы при удалении'}
    )


@song_router.get('/categories/mains', tags=['category'])
async def get_main_chapters() -> list[song_schemes.CategorySongResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_filter={
        'parent_id': None
        }
    )

@song_router.get('/categories/get_childs/{id_category}', tags=['category'])
async def get_child_chapters(
        id_category: int
) -> list[song_schemes.CategorySongResponse]:



    return await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_filter={
            'parent_id': id_category
        }
    )

@song_router.post('/category', tags=['category'])
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
            name=category.name,
            parent_id=category.parent_id
    ):

        return JSONResponse(
            status_code=201,
            content={'message':'Категория успешно добавлена'}
        )

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка при создании категории.'}
    )

@song_router.get('/categories/{category_id}', tags=['category'])
async def get_category_by_id(
        category_id: int
) -> song_schemes.CategorySongResponse:
    """
    Получаем категорию по ее id
    :param category_id: id искомой категории
    :return: category - словарь категории
    """

    return await CRUDManagerSQL.get_data(
        model=models.CategorySong,
        row_id=category_id
    )


@song_router.put('/categories/{category_id}', tags=['category'])
async def update_category_by_id(category_id: int):
    """
    Изменяем категорию по ее id
    :param category_id: id изменяемой категории
    :return:
    """

    pass


@song_router.delete('/categories/{category_id}', tags=['category'])
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

    return JSONResponse(
        status_code=500,
        content={'message': 'Произошла ошибка на сервере'}
    )


@song_router.get('/by_category/{category_id}', tags=['category'])
async def get_songs_by_category(
        category_id: int
) -> list[song_schemes.SongResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.Songs,
        row_filter={
            'category_id': category_id
        }
    )
