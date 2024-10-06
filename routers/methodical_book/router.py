from fastapi import APIRouter, UploadFile, Form, File
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse

from pydantic_schemes.MethodicalBook import schemes as mb_schemes

from database import models
from database.cruds import CRUDManagerSQL

from typing import Annotated
from misc import file_work


methodical_book_router = APIRouter(prefix='/methodical_book', tags=['methodical_book'])

@methodical_book_router.get('/chapters/mains', tags=['methodical_book'])
async def get_main_chapters() -> list[mb_schemes.MethodicalChaptersResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'parent_id':None
        }
    )

@methodical_book_router.get('/chapters/get_childs/{id_chapter}', tags=['methodical_book'])
async def get_child_chapters(
        id_chapter: int
) -> list[mb_schemes.MethodicalChaptersResponse]:

    return await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'parent_id': id_chapter
        }
    )


@methodical_book_router.post('/chapters/', tags=['methodical_book'])
async def create_chapter_methodical_book(
        title: Annotated[str, Form()],
        parent_id: Annotated[int, Form()],
        file: Annotated[UploadFile, File()]
) -> JSONResponse:
    # TODO реализовать проверку что такая запись уже есть

    if file_work.save_file(path='database/files_data/methodical_data/',
                           file=file):

        data = {
            'title': title,
            'parent_id': parent_id,
            'file_path': f'database/files_data/methodical_data/{file.filename}'
        }

        if await CRUDManagerSQL.insert_data(
                model=models.MethodicalBookChapters,
                **data
        ):
            JSONResponse(
                status_code=201,
                content={'message': 'Запись сохранена'}
            )

        return JSONResponse(
            status_code=400,
            content={'message': 'Ошибка сохранения'}
        )

    else:
        return JSONResponse(
            status_code=400,
            content={'message': 'Ошибка сохранения'}
        )


@methodical_book_router.get('/chapters/file/{chapter_id}', tags=['methodical_book'])
async def get_chapter_file(
        chapter_id: int
) -> FileResponse:

    chapter = await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_id=chapter_id
    )

    file = chapter.file_path

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(
        path=file,
        filename='avc.pdf',
        headers=headers_data
    )
