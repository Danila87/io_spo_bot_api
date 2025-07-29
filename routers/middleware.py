from functools import wraps

from database import models
from database.cruds import CRUDManagerSQL
from schemas.service import RequestCreate


def insert_user_request(func):
    @wraps(func)
    async def wrapper(**kwargs):
        result = await func(**kwargs)

        if kwargs.get('is_create_user_request'):
            user_id = await CRUDManagerSQL.get_data(
                model=models.TelegramUsers,
                row_filter={
                    'telegram_id': kwargs
                }
            )
            await CRUDManagerSQL.insert_request(
                request_type_title='Игра',
                body=[
                    RequestCreate(
                        id_content=row.id,
                        id_user=user_id[0].id,
                        content_display_value=row.title
                    ) for row in result.data
                ]
            )

        return result
    return wrapperну