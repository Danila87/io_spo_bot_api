from fastapi import APIRouter, HTTPException, UploadFile, Form, File
from fastapi.responses import FileResponse

from pydantic_schemes.MethodicalBook import schemes as mb_schemes

from database import models
from database.cruds import BaseCruds

from typing import Annotated
from misc import file_work, verify_data


methodical_book_router = APIRouter(prefix='/methodical_book', tags=['methodical_book'])


@methodical_book_router.get('/sections/', tags=['methodical_book'])
async def get_sections_methodical_book() -> list[mb_schemes.MethodicalSectionsResponse]:

    return await BaseCruds.get_all_data(model=models.SectionsMethodologicalBook,
                                        schema=mb_schemes.MethodicalSectionsResponse)


@methodical_book_router.post('/sections/', tags=['methodical_book'])
async def create_section_methodical_book(data: mb_schemes.MethodicalSection):

    await verify_data.verify_data(
        data=data,
        schema=mb_schemes.MethodicalSection,
        model=models.SectionsMethodologicalBook,
        error_msg='Такая секция уже существует',
        title=data.title
    )

    if await BaseCruds.insert_data(model=models.SectionsMethodologicalBook,
                                   title=data.title):

        return HTTPException(status_code=201,
                             detail=f'Секция "{data.title}" создана')

    return HTTPException(status_code=500,
                         detail='Возникла ошибка, попробуйте позже')


@methodical_book_router.get('/sections/{section_id}', tags=['methodical_book'])
async def get_chapters_by_section(section_id: int) -> list[mb_schemes.MethodicalChaptersResponse]:

    return await BaseCruds.get_data_by_filter(model=models.ChaptersMethodologicalBook,
                                              section_id=section_id,
                                              schema=mb_schemes.MethodicalChaptersResponse)


@methodical_book_router.post('/chapters/', tags=['methodical_book'])
async def create_chapter_methodical_book(title_chapter: Annotated[str, Form()],
                                         section_id: Annotated[int, Form()],
                                         file: Annotated[UploadFile, File()]):

    if file_work.save_file(path='database/files_data/methodical_data/',
                           file=file):

        data = {
            'title': title_chapter,
            'section_id': section_id,
            'file_path': f'database/files_data/methodical_data/{file.filename}'
        }

        if await BaseCruds.insert_data(model=models.ChaptersMethodologicalBook, **data):
            return 'Сохранил'

        return 'Кабзда'

    else:
        return 'Ошибка сохранения'


@methodical_book_router.get('/chapters/file/{chapter_id}', tags=['methodical_book'])
async def get_chapter_file(chapter_id: int) -> FileResponse:

    chapter = await BaseCruds.get_data_by_id(model=models.ChaptersMethodologicalBook,
                                             model_id=chapter_id,
                                             schema=mb_schemes.MethodicalChaptersResponse)

    file = chapter.file_path

    headers_data = {
        'file_type': '.pdf'
    }

    return FileResponse(path=file, filename='avc.pdf',
                        headers=headers_data)
