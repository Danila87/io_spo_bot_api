from pydantic import BaseModel


class User(BaseModel):

    telegram_id: int

    first_name: str | None = None
    last_name: str | None = None
    nickname: str
