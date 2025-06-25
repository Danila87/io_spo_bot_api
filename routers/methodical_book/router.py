import urllib.parse

from fastapi import APIRouter, UploadFile, Form, File, HTTPException
from fastapi.params import Query, Body

from starlette.responses import JSONResponse, Response

from common_lib.file_storage.file_manager import file_manager
from schemas import methodical_book as mb_schemes

from database import models
from database.cruds import CRUDManagerSQL

from typing import Annotated, List, Optional

from schemas.service import AdditionalPath
from schemas.responses import ResponseData, Meta, ResponseDelete

methodical_book_router = APIRouter(prefix='/methodical_book', tags=['methodical_book'])


@methodical_book_router.get(
    path='/chapters',
    tags=['methodical_book'],
    response_model=ResponseData[mb_schemes.MethodicalChaptersResponse]
)
async def get_chapter(
    id_chapter: Annotated[List[int], Query(
        description="Список id категорий"
    )] = None,
    only_parents: Annotated[bool, Query(
        description="Вернуть главы у которых нет родителя."
    )] = False
):
    row_filter = {"parent_id": None} if only_parents else {}

    chapters = await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_id=id_chapter,
        row_filter=row_filter
    )

    return ResponseData(
        data=chapters,
        meta=Meta(total=len(chapters))
    )


@methodical_book_router.get(
    path='/chapters/childrens',
    tags=['methodical_book'],
    response_model=ResponseData[mb_schemes.MethodicalChaptersResponse]
)
async def get_child_chapters(
        id_chapter: Annotated[int, Query(
            description="Id главы, детей которой нужно получить"
        )]
):

    chapters = await CRUDManagerSQL.get_data(
        model=models.MethodicalBookChapters,
        row_filter={
            'parent_id': id_chapter
        }
    )

    return ResponseData(
        data=chapters,
        meta=Meta(total=len(chapters))
    )


@methodical_book_router.post(
    path='/chapters',
    tags=['methodical_book']
)
async def create_chapter_methodical_book(
    chapter_data: Annotated[mb_schemes.MethodicalChapterCreate, Body(
        description="Тело главы",
    )],
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


@methodical_book_router.put(
    path='/chapters/file',
    tags=['methodical_book']
)
async def chapter_upload_file(
        chapter_id: Annotated[int, Query(
            description="Id главы"
        )],
        file: Annotated[UploadFile, File(
            description="Файл для главы"
        )]
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

@methodical_book_router.get(
    path='/chapters/file',
    tags=['methodical_book']
)
async def get_chapter_file(
        chapter_id: Annotated[int, Query(
            description="Id главы"
        )]
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