from pydantic import BaseModel


class Song(BaseModel):

    """
    Базовая модель песни. Используется преимущественно для создания
    """

    title: str
    title_search: str
    text: str
    file_path: str | None = None
    category: int | None = None  # Это внешний ключ, посмотреть как сюда передавать только корректные значения


class SongResponse(Song):

    """
    Полная модель созданной песни. Наследуется от Song.
    """

    id: int


class CategorySong(BaseModel):

    """
    Модель для создания категории
    """

    name: str
    parent_id: int | None = None


class CategorySongResponse(CategorySong):


    """
    Модель готовой категории
    """

    id: int
    name: str

class SongSearch(BaseModel):

    telegram_id: int = 1
    title_song: str


class SongsByCategory(CategorySongResponse):
    rel_songs: list[SongResponse]