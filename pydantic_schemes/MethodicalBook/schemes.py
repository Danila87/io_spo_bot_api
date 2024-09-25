from pydantic import BaseModel


class MethodicalChapter(BaseModel):

    parent_id: int | None = None
    title: str


class MethodicalChaptersResponse(MethodicalChapter):

    id: int
    file_path: str | None

