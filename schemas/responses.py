from pydantic import BaseModel
from typing import List, TypeVar, Generic, Optional

T = TypeVar("T")

class Meta(BaseModel):
    total: int


class ResponseData(BaseModel, Generic[T]):
    data: List[T]
    message: Optional[str] = None
    meta: Optional[Meta] = None


class ResponseCreate(BaseModel, Generic[T]):
    data: T
    message: Optional[str] = 'Запись успешно создана.'
    meta: Optional[Meta] = None


class ResponseDelete(BaseModel):
    message: Optional[str] = 'Запись успешно удалена'
    meta: Optional[Meta] = None