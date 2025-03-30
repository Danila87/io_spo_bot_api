import urllib.parse

from fastapi import APIRouter, UploadFile, Form, File, HTTPException

from starlette.responses import JSONResponse, Response

from common_lib.file_storage.file_manager import file_manager
from schemas import methodical_book as mb_schemes

from database import models
from database.cruds import CRUDManagerSQL

from typing import Annotated, List, Optional

from schemas.methodical_book import MethodicalChapterCreate
from schemas.service import AdditionalPath

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

@methodical_book_router.get('/chapters/')
async def get_chapter(
        id_chapter: int
) -> mb_schemes.MethodicalChaptersResponse:
    if not (data := await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_id=id_chapter
    )):
        raise HTTPException(
            status_code=404,
            detail={'message': 'Данный раздел не найден'}
        )

    return mb_schemes.MethodicalChaptersResponse(**data[0].to_dict())

@methodical_book_router.get('/chapters/get_children/', tags=['methodical_book'])
async def get_child_chapters(
        id_chapter: Optional[int] = None
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
        chapter_data: MethodicalChapterCreate,
) -> JSONResponse:

    if await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'title': chapter_data.title,
            'parent_id': chapter_data.parent_id
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данная глава уже существует в БД'
        )

    if not await CRUDManagerSQL.insert_data(
            model=models.MethodicalBookChapters,
            body={
                'title': chapter_data.title,
                'parent_id': chapter_data.parent_id,
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

@methodical_book_router.put('/chapters/upload_file')
async def chapter_upload_file(
        chapter_id: int,
        file: Annotated[UploadFile, File()]
):
    if not await file_manager.save_file(
            file=file,
            additional_path=AdditionalPath.METHODICAL_BOOKS_PATH
    ):
        raise HTTPException(
            status_code=500,
            detail='Возникла ошибка при сохранении файла'
        )

    if not await CRUDManagerSQL.update_data(
        model=models.MethodicalBookChapters,
        row_id=chapter_id,
        body={
            'file_path':  f'{AdditionalPath.METHODICAL_BOOKS_PATH.value}/{file.filename}',
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
) -> Response:

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

    file = await file_manager.get_file(filepath)

    headers_data = {
        'file_type': file.suffix,
        'filename': urllib.parse.quote(file.filename.encode('utf-8'))
    }

    return Response(
        content=file.file_data,
        media_type=file.content_type,
        headers=headers_data
    )