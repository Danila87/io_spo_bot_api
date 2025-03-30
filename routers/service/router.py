from typing import List, Dict

from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

from database.models import Reviews
from schemas import schemes

from database import models
from database.cruds import CRUDManagerSQL
from schemas.service import ReviewCreate, ReviewResponse
from schemas.schemes import SearchData

router_service = APIRouter(
    prefix='/service',
    tags=['service']
)


@router_service.post('/check_user', response_model=schemes.User)
async def check_user(
        user: schemes.User
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


@router_service.post('/refactor_text_song')
def refactor_text_song(
        text_song: str
) -> str:

    lines = text_song.split('\n')
    formatted_text = '\\n'.join(lines)

    return formatted_text

@router_service.get('/search_by_title', tags=['service'])
async def search_by_title(
        title: str
) -> Dict[str, List[SearchData]]:

        data = await CRUDManagerSQL.search_by_title(title_search=title)

        return {
            key: [
                SearchData(**row.to_dict()) for row in items
            ] for key, items in data.items()
        }

@router_service.post('/reviews/', tags=['reviews', 'service'])
async def insert_review(
        review: ReviewCreate
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

@router_service.get('/reviews/', tags=['reviews', 'service'])
async def get_all_reviews(
        only_new: int = 0
) -> List[ReviewResponse]:
    """
    only_new - Получить только новые отзывы. 1-да, 0-нет. По умолчанию 0
    """

    row_filter = {
        'looked_status': 0
    } if only_new == 1 else None

    data = await CRUDManagerSQL.get_data(
        model=Reviews,
        row_filter=row_filter
    )

    if only_new == 1:
        for review in data:
            await CRUDManagerSQL.update_data(
                model=Reviews,
                row_id=review.id,
                body={
                    'looked_status': 1
                }
            )

    return [ReviewResponse(**item.to_dict()) for item in data]
