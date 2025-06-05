from datetime import date
from pydantic import BaseModel
from typing import Optional, List


class SongEventCreate(BaseModel):
    title: str
    start_dt: date
    duration: int
    end_dt: Optional[date] = None


class SongEventCreateWithSong(SongEventCreate):
    song_ids: Optional[List[int]] = None


class SongEventResponse(SongEventCreate):
    id: int
    song_ids: Optional[List[int]] = None

class SongEventCreateResponse(BaseModel):
    id: int
    title: str