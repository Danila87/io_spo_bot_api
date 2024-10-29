from pathlib import Path

from fastapi import APIRouter, UploadFile, Form, File, HTTPException
from fastapi.responses import FileResponse

from starlette.responses import JSONResponse

from pydantic_schemes.MethodicalBook import schemes as mb_schemes

from database import models
from database.cruds import CRUDManagerSQL

from typing import Annotated, List, Union
from misc import file_work


methodical_book_router = APIRouter(prefix='/methodical_book', tags=['methodical_book'])

@methodical_book_router.get('/chapters/mains', tags=['methodical_book'], )
async def get_main_chapters() -> List[mb_schemes.MethodicalChaptersResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'parent_id':None
        }
    )

    return [
        mb_schemes.MethodicalChaptersResponse(**row.to_dict()) for row in data
    ]

@methodical_book_router.get('/chapters/get_childs/', tags=['methodical_book'])
async def get_child_chapters(
        id_chapter: int
) -> List[mb_schemes.MethodicalChaptersResponse]:

    data = await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'parent_id': id_chapter
        }
    )

    return [
        mb_schemes.MethodicalChaptersResponse(**row.to_dict()) for row in data
    ]


@methodical_book_router.post('/chapters/', tags=['methodical_book'])
async def create_chapter_methodical_book(
        title: Annotated[str, Form()],
        parent_id: Annotated[int, Form()],
        file: Annotated[UploadFile, File()]
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'title': title,
            'parent_id': parent_id
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная глава уже существует в БД'
        )

    if not (filepath := file_work.save_file(path='database/files_data/methodical_data/',
                           file=file)):
        raise HTTPException(
            status_code=500,
            detail='Возникла ошибка при сохранении файла'
        )

    if not await CRUDManagerSQL.insert_data(
            model=models.MethodicalBookChapters,
            body={
                'title': title,
                'parent_id': parent_id,
                'file_path': filepath
            }
    ):
        raise HTTPException(
            status_code=500,
            detail={'message': 'Ошибка сохранения'}
        )

    return JSONResponse(
        status_code=201,
        content={'message': 'Запись сохранена'}
    )


@methodical_book_router.get('/chapters/file/', tags=['methodical_book'], response_model=None)
async def get_chapter_file(
        chapter_id: int
) -> FileResponse:

    if not (chapter := await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_id=chapter_id
    )):
        raise HTTPException(
            status_code=404,
            detail='Не найдена глава с указанным id'
        )

    if (filepath := chapter[0].file_path) is None:
        raise HTTPException(
            status_code=404,
            detail=f'Не найден связанный файл по пути {filepath}'
        )

    file = Path(filepath)

    headers_data = {
        'file_type': file.suffix
    }

    return FileResponse(
        path=file.resolve(),
        filename=file.name,
        headers=headers_data
    )