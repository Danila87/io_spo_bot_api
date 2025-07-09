from typing import Annotated

from fastapi.params import Depends, Body
from starlette.responses import JSONResponse

from . import auth

from fastapi import APIRouter, HTTPException

from schemas.auth import UserCreate, UserLogin, UserResponse, TokenPair, SubjectData

from database.cruds import CRUDManagerSQL
from database import models

from config import SECRET_KEY_REFRESH, SECRET_KEY

auth_router = APIRouter(
    prefix='/auth',
    tags=['authentication']
)

async def get_user(
        user: UserLogin
) -> UserResponse:
    if not (user_db := await CRUDManagerSQL.get_data(
        model=models.Users,
        row_filter={
            'login': user.login
        }
    )):
        raise HTTPException(
            status_code=404,
            detail={'message': 'Пользователь с данным логином не найден'}
        )

    if not auth.verify_password(
        current_pass=user.password,
        hashed_pass=user_db[0].password
    ):
        raise HTTPException(
            status_code=500,
            detail={'message': 'Введен неверный пароль'}
        )

    return UserResponse(
        **user_db[0].to_dict()
    )

@auth_router.post(
    path='/register/',
)
async def registration(
        user: UserCreate
):
    if await CRUDManagerSQL.get_data(
        model=models.Users,
        row_filter={
            'login': user.login,
        }
    ):
        raise HTTPException(
            status_code=500,
            detail='Данный логин занят'
        )

    hash_pass = auth.hash_password(
        password=user.password
    )

    user.password = hash_pass

    if await CRUDManagerSQL.insert_data(
        model=models.Users,
        body=user.model_dump()
    ):
        return JSONResponse(
            status_code=201,
            content={'message': 'Пользователь создан'}
        )

@auth_router.post(
    path='/login/',
    response_model=TokenPair
)
async def login(
        user: UserResponse = Depends(get_user)
):
    access_token = auth.create_jwt_token(
            key=SECRET_KEY,
            data=SubjectData(
                login=user.login,
                email=user.email
            )
    )

    refresh_token = auth.create_jwt_token(
            key=SECRET_KEY_REFRESH,
            exp_duration=240
        )

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token
    )

@auth_router.post(
    path='/update_token/',
    response_model=TokenPair
)
async def update_login(
        tokens: Annotated[TokenPair, Body(
            description="Пара токенов"
        )]
):

    if auth.verify_jwt_token(tokens.refresh_token, SECRET_KEY_REFRESH):
        new_access_token = auth.create_jwt_token(
            key=SECRET_KEY,
            data=SubjectData(
                login='asdasd',
                email='asd'
            )
        )
        new_refresh_token = auth.create_jwt_token(
            key=SECRET_KEY_REFRESH,
            exp_duration=240
        )

        return TokenPair(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
