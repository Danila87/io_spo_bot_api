from typing import Union, List, Optional

from pydantic import BaseModel


class PiggyBankGroupCreate(BaseModel):

    title: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Старший возраст",
            }
        }

class PiggyBankGroupResponse(PiggyBankGroupCreate):

    id: int


class PiggyBankTypeGameCreate(BaseModel):

    title: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Игры на сплочение",
            }
        }


class PiggyBankTypeGameResponse(PiggyBankTypeGameCreate):

    id: int


class PiggyBankBaseStructureCreate(BaseModel):

    """
    Базовая структура для сущностей копилки.
    Почти все сущности копилки имеют одинаковые атрибуты.
    """

    title: str
    description: str
    group_id: Union[List[int], int]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию.",
                "group_id": [1]
            }
        }


class PiggyBankBaseStructureResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: Optional[str] = None


class PiggyBankGameCreate(PiggyBankBaseStructureCreate):

    type_id: Union[List[int], int]

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию.",
                "group_id": [1],
                "type_id": [1]
            }
        }


class PiggyBankGameResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: Optional[str] = None


class IntersectionGroupTypeIds(BaseModel):
    group_ids: Optional[List[int]] = None
    type_ids: Optional[List[int]] = None