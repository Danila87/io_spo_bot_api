from fastapi import APIRouter, HTTPException

from pydantic_schemes.Song import schemes as song_schemes

from database import models
from database.cruds import BaseCruds, SongCruds

from misc.verify_data import verify_data

song_router = APIRouter(prefix='/song', tags=['all_song_methods'])


@song_router.get('/songs/by_category', tags=['song', 'category'])
async def get_songs_by_category() -> list[song_schemes.SongsByCategory]:
    """
    Получаем категорию и все песни которые ей принадлежат
    :return: Songs - Список категорий, которые в свою очередь содержат список песен
    """

    songs = await SongCruds.get_all_songs_by_category()

    return songs


@song_router.get('/songs', tags=['song'])
async def get_songs() -> list[song_schemes.SongResponse]:
    """
    Получаем все песни
    :return: Список словарей всех песен
    """

    songs = await BaseCruds.get_all_data(model=models.Songs,
                                         schema=song_schemes.SongResponse)

    return songs


@song_router.post('/songs/search_title', tags=['song'])
async def search_songs_by_title(request_data: song_schemes.SongSearch) -> list[song_schemes.SongSearch]:
    """
    Поиск песни по ее названию. В поиске используется алгоритм расстояния Левенштейна
    :param request_data:
    :return: Список словарей подходящих песен
    """

    songs = await SongCruds.search_all_songs_by_title(title_song=request_data.title_song)

    return songs


@song_router.post('/', tags=['song'])
async def insert_song(song: song_schemes.Song):
    """
    Вставляем песню, но перед этим проводим проверку что такой песни в бд нет.
    ВАЖНО: Текст песни должен быть одной строкой где переносы экранированы //n. В сервисных методах есть функция которая правит данный момент
    :param song: Объект песни которую вставляем
    :return: HTTPException с статус кодом и detail
    """

    await verify_data(schema=song,
                      model=models.Songs,
                      error_msg='Такая песня уже существует',
                      title=song.title
                      )

    if await BaseCruds.insert_data(model=models.Songs,
                                   title=song.title,
                                   title_search=song.title_search,
                                   text=song.text,
                                   file_path=song.file_path,
                                   category=song.category):
        return HTTPException(status_code=201,
                             detail='Песня успешно добавлена!')

    return HTTPException(status_code=400,
                         detail='Произошла ошибка на сервере')


@song_router.get('/{song_id}', tags=['song'])
async def get_song(song_id: int) -> song_schemes.SongResponse | bool:
    """
    Получаем песню по ее id
    :param song_id: id искомой песни
    :return: HTTPException в случае если песни нет либо song если песня найдена
    """

    song = await BaseCruds.get_data_by_id(model=models.Songs,
                                          model_id=song_id,
                                          schema=song_schemes.SongResponse)

    if not song:
        raise HTTPException(status_code=400,
                            detail='Песни не существует')

    return song


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
async def delete_song_by_id(song_id: int):
    """
    Удаляем песню по ее id
    :param song_id: id искомой песни
    :return: HTTPException с статус кодом и detail
    """

    if await BaseCruds.delete_data_by_id(model=models.Songs,
                                         model_id=song_id):
        return HTTPException(status_code=200,
                             detail='Песня успешно удалена')

    return HTTPException(status_code=500,
                         detail='Возникли проблемы при удалении')


@song_router.get('/categories/', tags=['category'])
async def get_all_categories() -> list[song_schemes.CategorySongResponse]:
    """
    Получаем все категории
    :return: categories - Список словарей категорий
    """

    categories = await BaseCruds.get_all_data(model=models.CategorySong,
                                              schema=song_schemes.CategorySongResponse)

    return categories


@song_router.post('/category', tags=['category'])
async def insert_category(category: song_schemes.CategorySong):
    """
    Добавляем категорию. Сначала проходит верификацию на отсутствие такой же категории в бд
    :param category: Словарь категории
    :return: HTTPException со статус кодом и detail
    """

    await verify_data(data=category,
                      schema=song_schemes.CategorySong,
                      model=models.CategorySong,
                      error_msg='Такая категория уже существует',
                      name=category.name
                      )

    if await BaseCruds.insert_data(
            model=models.CategorySong,
            name=category.name,
            parent_id=category.parent_id
    ):

        return HTTPException(status_code=201,
                             detail='Категория успешно добавлена')


@song_router.get('/categories/{category_id}', tags=['category'])
async def get_category_by_id(category_id: int) -> song_schemes.CategorySongResponse:
    """
    Получаем категорию по ее id
    :param category_id: id искомой категории
    :return: category - словарь категории
    """

    category = await BaseCruds.get_data_by_id(model=models.CategorySong,
                                              model_id=category_id,
                                              schema=song_schemes.CategorySongResponse)

    return category


@song_router.put('/categories/{category_id}', tags=['category'])
async def update_category_by_id(category_id: int):
    """
    Изменяем категорию по ее id
    :param category_id: id изменяемой категории
    :return:
    """

    pass


@song_router.delete('/categories/{category_id}', tags=['category'])
async def delete_category_by_id(category_id: int):
    """
    Удаляем категорию по ее id
    :param category_id: id удаляемой категории
    :return: HTTPException - Результат удаления. Возвращает статус код и detail
    """

    if await BaseCruds.delete_data_by_id(model=models.CategorySong,
                                         model_id=category_id):

        return HTTPException(status_code=200,
                             detail='Категория успешно удалена')

    return HTTPException(status_code=500,
                         detail='Произошла ошибка на сервере')


@song_router.get('/by_category/{category_id}', tags=['category'])
async def get_songs_by_category(category_id: int) -> list[song_schemes.SongResponse]:
    return await BaseCruds.get_data_by_filter(model=models.Songs,
                                              schema=song_schemes.SongResponse,
                                              category=category_id)
