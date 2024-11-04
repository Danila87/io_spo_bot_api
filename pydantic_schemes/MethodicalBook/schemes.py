from pydantic import BaseModel


class MethodicalChapterCreate(BaseModel):

    parent_id: int | None = None
    title: str

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Глава 1.1 История ИО СПО",
                "parent_id": 1
            }
        }

class MethodicalChaptersResponse(MethodicalChapterCreate):

    id: int
    file_path: str | None

