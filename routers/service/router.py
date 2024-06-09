from fastapi import APIRouter, HTTPException

from pydantic_schemes import schemes
from pydantic_schemes.SongSchemes import schemes as song_schemes

from database import models
from database.cruds import BaseCruds

import datetime

router_service = APIRouter(
    prefix='/service',
    tags=['service']
)


@router_service.post('/check_user', response_model=schemes.User)
async def check_user(user: schemes.User):

    if await BaseCruds.get_data_by_filter(model=models.Users, verify=True, telegram_id=user.telegram_id):
        raise HTTPException(status_code=400, detail='Пользователь существует')

    await BaseCruds.insert_data(model=models.Users,
                                telegram_id=user.telegram_id,
                                first_name=user.first_name,
                                last_name=user.last_name,
                                nickname=user.nickname)

    raise HTTPException(status_code=201, detail='Пользователь создан')


@router_service.post('/refactor_text_song')
def refactor_text_song(text_song: str):

    lines = text_song.split('\n')
    formatted_text = '\\n'.join(lines)

    return formatted_text
