from datetime import date
from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class SongEventCreate(BaseModel):
    title: str
    start_dt: date
    duration: int
    end_dt: Optional[date] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Спевка ИО СПО",
                "start_dt": "2023-01-01",
                "duration": 1,
                "end_dt": "2023-01-02"
            }
        }
    )

class SongEventCreateWithSong(SongEventCreate):
    song_ids: Optional[List[int]] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "title": "Спевка ИО СПО",
                "start_dt": "2023-01-01",
                "duration": 1,
                "end_dt": "2023-01-02",
                "song_ids": [1, 2]
            }
        }
    )

class SongEventResponse(SongEventCreate):
    id: int
    song_ids: Optional[List[int]] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Спевка ИО СПО",
                "start_dt": "2023-01-01",
                "duration": 1,
                "end_dt": "2023-01-02",
                "song_ids": [1, 2]
            }
        }
    )


class SongEventCreateResponse(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "title": "Спевка ИО СПО"
            }
        }
    )