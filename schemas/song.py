from pydantic import BaseModel, ConfigDict


class SongCreate(BaseModel):

    """
    Базовая модель песни. Используется для создания
    """

    title: str
    title_search: str
    text: str
    file_path: str | None = None
    category: int | None = None  # Это внешний ключ, посмотреть как сюда передавать только корректные значения

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Ангел света",
                "title_search": "ангелсвета",
                "text": "А мы не ангелы парень, нет мы не ангелы",
                "file_path": "/path/to/file.mp3",
                "category": 1
            }
        }
    )

class SongResponse(SongCreate):

    """
    Полная модель созданной песни. Наследуется от Song.
    """

    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Ангел света",
                "title_search": "ангелсвета",
                "text": "А мы не ангелы парень, нет мы не ангелы",
                "file_path": "/path/to/file.mp3",
                "category": 1
            }
        }
    )


class CategorySongCreate(BaseModel):

    """
    Модель для создания категории
    """

    name: str
    parent_id: int | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "Песни ИО СПО (Авторские)",
                "parent_id": 1
            }
        }
    )


class CategorySongResponse(CategorySongCreate):


    """
    Модель готовой категории
    """

    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Песни ИО СПО (Авторские)",
                "parent_id": 1
            }
        }
    )


class SongSearch(BaseModel):

    telegram_id: int = 1
    title_song: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "telegram_id": 1,
                "title_song": "Ангел света"
            }
        }
    )


class SongsByCategoryResponse(CategorySongResponse):
    rel_songs: list[SongResponse]

