from typing import List, Dict, Annotated

from fastapi import APIRouter, HTTPException
from fastapi.params import Body, Query
from starlette.responses import JSONResponse

from database.models import Reviews
from schemas import service as sc_schemes

from database import models
from database.cruds import CRUDManagerSQL
from schemas.responses import ResponseData, Meta
from schemas.service import ReviewCreate, ReviewResponse

router_service = APIRouter(
    prefix='/service',
    tags=['service']
)


@router_service.post(
    path='/check_user/',
    summary='Проверка пользователя на существование',
)
async def check_user(
        user: Annotated[sc_schemes.TelegramUser, Body(
            description="Тело пользователя"
        )]
) -> JSONResponse:

    if len(await CRUDManagerSQL.get_data(
            model=models.TelegramUsers,
            row_filter={
                'telegram_id':user.telegram_id
            }
    )) > 0:
        return JSONResponse(
            status_code=400,
            content={'message': 'Пользователь существует'}
        )

    await CRUDManagerSQL.insert_data(
        model=models.TelegramUsers,
        body={
            'telegram_id':user.telegram_id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'nickname': user.nickname
        }
    )

    return JSONResponse(
        status_code=201,
        content={'message': 'Пользователь создан'}
    )


@router_service.post(
    path='/refactor_text_song/',
    summary='Перевод строки в слэшн',
)
def refactor_text_song(
        text_song: Annotated[str, Query(
            description="Текст песни"
        )]
) -> str:

    lines = text_song.split('\n')
    formatted_text = '\\n'.join(lines)

    return formatted_text


@router_service.get(
    path='/search_by_title/',
    summary='Поиск данных по названию',
)
async def search_by_title(
        title: Annotated[str, Query(
            description="Текст для поиска"
        )]
) -> Dict[str, List[sc_schemes.SearchData]]:

        data = await CRUDManagerSQL.search_by_title(title_search=title)

        return {
            key: [
                sc_schemes.SearchData(**row.to_dict()) for row in items
            ] for key, items in data.items()
        }


@router_service.post(
    path='/reviews/',
    tags=['reviews'],
    summary='Создание отзыва'
)
async def insert_review(
        review: Annotated[ReviewCreate, Body(
            description="Тело отзыва"
        )]
):
    if not await CRUDManagerSQL.insert_data(
        model=Reviews,
        body=review.model_dump()
    ):
        raise HTTPException(
            status_code=500,
            detail=f'Не удалось создать отзыв.'
        )

    return JSONResponse(
        status_code=201,
        content={'message': 'Отзыв успешно создан.'}
    )


@router_service.get(
    path='/reviews/',
    tags=['reviews'],
    response_model=ResponseData[ReviewResponse],
    summary='Получение отзывов'
)
async def get_all_reviews(
        is_only_new: Annotated[bool, Query(
            description="Получить только новые отзывы."
        )] = False
):

    row_filter = {
        'looked_status': 0
    } if not is_only_new else None

    reviews = await CRUDManagerSQL.get_data(
        model=Reviews,
        row_filter=row_filter
    )

    if is_only_new:
        for review in reviews:
            await CRUDManagerSQL.update_data(
                model=Reviews,
                row_id=review.id,
                body={
                    'looked_status': 1
                }
            )

    return ResponseData(
        data=reviews,
        meta=Meta(total=len(reviews))
    )
