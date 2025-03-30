from fastapi.params import Depends
from starlette.responses import JSONResponse

from . import auth

from fastapi import APIRouter, HTTPException

from schemas.auth import UserCreate, UserLogin, UserResponse, TokenPair, SubjectData

from database.cruds import CRUDManagerSQL
from database import models

from config import SECRET_KEY_REFRESH, SECRET_KEY

auth_router = APIRouter(
    prefix='/auth',
    tags=['auth']
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

@auth_router.post('/register')
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

@auth_router.post('/login')
async def login(
        user: UserResponse = Depends(get_user)
):
    return {
        'access_token': auth.create_jwt_token(
            key=SECRET_KEY,
            data=SubjectData(
                login=user.login,
                email=user.email
            )
        ),
        'refresh_token': auth.create_jwt_token(
            key=SECRET_KEY_REFRESH,
            exp_duration=240
        )
    }

@auth_router.post('/update_token')
async def update_login(
        tokens: TokenPair
) -> TokenPair:

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
