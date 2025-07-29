from typing import Any

from database import models
from database.cruds import CRUDManagerSQL
from schemas.service import RequestCreate


async def insert_user_requests(
    tg_user_id: int,
    data: Any
):
    user_id = await CRUDManagerSQL.get_data(
        model=models.TelegramUsers,
        row_filter={
            'telegram_id': tg_user_id
        }
    )
    await CRUDManagerSQL.insert_request(
        request_type_title='Игра',
        body=[
            RequestCreate(
                id_content=row.id,
                id_user=user_id[0].id,
                content_display_value=row.title
            ) for row in data
        ]
    )
