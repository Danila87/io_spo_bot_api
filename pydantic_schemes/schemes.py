from pydantic import BaseModel


class User(BaseModel):

    telegram_id: int

    first_name: str | None = None
    last_name: str | None = None
    nickname: str


class MethodicalChapter(BaseModel):

    title: str
    chapter_id: int


class MethodicalSection(BaseModel):

    title: str


class PiggyBankGroup(BaseModel):

    title: str


class PiggyBankTypeGame(BaseModel):
    title: str


class PiggyBankBaseStructure(BaseModel):
    """
    Базовая структура для сущностей копилки.
    Почти все сущности копилки имеют одинаковые атрибуты.
    """
    title: str
    description: str
    file_path: str
    group_id: int


class PiggyBankGame(PiggyBankBaseStructure):

    type_id: int
