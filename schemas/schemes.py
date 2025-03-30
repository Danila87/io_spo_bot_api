from pydantic import BaseModel


class User(BaseModel):

    telegram_id: int
    nickname: str
    first_name: str | None = None
    last_name: str | None = None

class SearchData(BaseModel):
    id: int
    title: str
