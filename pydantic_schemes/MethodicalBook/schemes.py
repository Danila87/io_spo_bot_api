from pydantic import BaseModel


class MethodicalChapter(BaseModel):

    section_id: int
    title: str


class MethodicalSection(BaseModel):

    title: str


class MethodicalSectionsResponse(MethodicalSection):

    id: int


class MethodicalChaptersResponse(MethodicalChapter):

    id: int
    file_path: str

