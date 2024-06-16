from pydantic import BaseModel


class PiggyBankGroup(BaseModel):

    title: str


class PiggyBankGroupResponse(PiggyBankGroup):

    id: int


class PiggyBankTypeGame(BaseModel):

    title: str


class PiggyBankTypeGameResponse(PiggyBankTypeGame):

    id: int


class PiggyBankBaseStructureCreate(BaseModel):

    """
    Базовая структура для сущностей копилки.
    Почти все сущности копилки имеют одинаковые атрибуты.
    """

    title: str
    description: str
    file_path: str
    group_id: int


class PiggyBankBaseStructureResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: str


class PiggyBankGameCreate(PiggyBankBaseStructureCreate):

    type_id: int


class PiggyBankGameResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: str

