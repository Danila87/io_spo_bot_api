from typing import Union, List, Optional

from pydantic import BaseModel, ConfigDict


class PiggyBankGroupCreate(BaseModel):

    title: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Старший возраст"
            }
        }
    )


class PiggyBankGroupResponse(PiggyBankGroupCreate):

    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Старший возраст"
            }
        }
    )


class PiggyBankTypeGameCreate(BaseModel):

    title: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Поймай меня если сможешь"
            }
        }
    )


class PiggyBankTypeGameResponse(PiggyBankTypeGameCreate):

    id: int

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Поймай меня если сможешь"
            }
        }
    )


class PiggyBankBaseStructureCreate(BaseModel):

    """
    Базовая структура для сущностей копилки.
    Почти все сущности копилки имеют одинаковые атрибуты.
    """

    title: str
    description: str
    group_id: Union[List[int], int]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию.",
                "group_id": [1]
            }
        }
    )


class PiggyBankBaseStructureResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию.",
                "file_path": "/path/to/file.pdf"
            }
        }
    )


class PiggyBankGameCreate(PiggyBankBaseStructureCreate):

    type_id: Union[List[int], int]

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию.",
                "group_id": [1],
                "type_id": [1]
            }
        }
    )


class PiggyBankGameResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию.",
                "file_path": "/path/to/file.pdf"
            }
        }
    )

class IntersectionGroupTypeIds(BaseModel):
    group_ids: Optional[List[int]] = None
    type_ids: Optional[List[int]] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "group_ids": [1],
                "type_ids": [1]
            }
        }
    )