from pydantic import BaseModel, ConfigDict


class MethodicalChapterCreate(BaseModel):

    parent_id: int | None = None
    title: str

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "parent_id": 1,
                "title": "Глава 1"
            }
        }
    )

class MethodicalChaptersResponse(MethodicalChapterCreate):

    id: int
    file_path: str | None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "parent_id": 1,
                "title": "Глава 1",
                "file_path": "/path/to/file.pdf"
            }
        }
    )