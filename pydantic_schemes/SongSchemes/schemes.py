from datetime import datetime

from pydantic import BaseModel, field_validator

from database.cruds import BaseCruds
from database import models


class Song(BaseModel):

    """
    Базовая модель песни. Используется преимущественно для создания
    """

    title: str
    title_search: str
    text: str
    file_path: str | None = None
    category: int | None = None  # Это внешний ключ, посмотреть как сюда передавать только корректные значения

    @classmethod
    @field_validator('category')
    async def validate_category(cls, value):
        if await BaseCruds.get_data_by_id(model=models.CategorySong, model_id=value):
            return value

        raise ValueError('Категория не найдена в БД')


class SongResponse(Song):

    """
    Полная модель созданной песни
    """

    id: int


class CategorySong(BaseModel):

    """
    Модель для создания категории
    """

    category: str


class CategorySongResponse(CategorySong):

    id: int
    type_category: int | None


class SongSearch(BaseModel):

    telegram_id: int = 1
    title_song: str


class CategoryType(BaseModel):

    name: str


class CategoryTypeResponse(CategoryType):

    id: int
