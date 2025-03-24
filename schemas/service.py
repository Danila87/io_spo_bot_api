from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class ReviewCreate(BaseModel):
    id_user: int
    text_review: str
    looked_status: int = 0
    created_data: datetime

class ReviewResponse(ReviewCreate):
    id: int

class RequestCreate(BaseModel):
    id_content: int
    id_user: Optional[int] = None
    content_display_value: str

class FileResponse(BaseModel):
    filename: str
    suffix: str
    file_data: bytes
    content_type: str

class AdditionalPath(Enum):
    KTD_PATH = "piggy_bank/ktds"
    LEGENDS_PATH = "piggy_bank/legends"
    GAMES_PATH = "piggy_bank/games"
    METHODICAL_BOOKS_PATH = "methodical_book"
    SONGS_PATH = "songs"