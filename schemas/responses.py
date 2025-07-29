from pydantic import BaseModel
from typing import List, TypeVar, Generic, Optional, Union

T = TypeVar("T")

class Meta(BaseModel):
    total: int


class ResponseData(BaseModel, Generic[T]):
    data: List[T]
    message: Optional[str] = None
    meta: Optional[Meta] = None


class ResponseCreate(BaseModel, Generic[T]):
    data: Union[List[T], T]
    message: Optional[str] = 'Запись успешно создана.'
    meta: Optional[Meta] = None


class ResponseDelete(BaseModel):
    message: Optional[str] = 'Запись успешно удалена'
    deleted_ids: Optional[List[int]] = None
    meta: Optional[Meta] = None