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
    file_path: str
    group_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию. Участники разбиваются на две команды: 'убегающие' и 'догоняющие'. Цель 'догоняющих' - поймать всех 'убегающих' за отведенное время. Игра развивает ловкость, стратегическое мышление и командную работу.",
                "file_path": '/home/1.docx',
                "group_id": 1
            }
        }


class PiggyBankBaseStructureResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: str


class PiggyBankGameCreate(PiggyBankBaseStructureCreate):

    type_id: int

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Поймай меня если сможешь",
                "description": "Увлекательная игра на скорость и реакцию. Участники разбиваются на две команды: 'убегающие' и 'догоняющие'. Цель 'догоняющих' - поймать всех 'убегающих' за отведенное время. Игра развивает ловкость, стратегическое мышление и командную работу.",
                "file_path": '/home/1.docx',
                "type_id": 1
            }
        }


class PiggyBankGameResponse(BaseModel):

    id: int
    title: str
    description: str
    file_path: str

