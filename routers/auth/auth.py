import jwt
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict

from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer

from config import SECRET_KEY, SECRET_KEY_REFRESH

from database.cruds import CRUDManagerSQL
from database import models

from schemas.auth import SubjectData, TokenData, UserResponse

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_jwt_token(
        key: str,
        data: Optional[SubjectData] = None,
        exp_duration: int = 60
) -> str:
    duration_time_jwt = timedelta(minutes=exp_duration)
    exp_time = datetime.now(tz=timezone.utc) + duration_time_jwt

    payload = TokenData(
        exp=exp_time,
        subject=data
    )

    token = jwt.encode(
        payload=payload.model_dump(),
        key=key,
        algorithm="HS256"
    )

    return token


def verify_jwt_token(
        jwt_token: str,
        key: str
) -> TokenData:
    try:
        data = jwt.decode(
            jwt=jwt_token,
            key=key,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return TokenData(**data)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail={'message': 'Истекло время действия токена'}
        )

    except jwt.PyJWTError:
        raise HTTPException(
            status_code=401,
            detail={'message': 'Ошибка декодирования токена'}
        )


def hash_password(
        password: str
) -> bytes:
    pass_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()

    return bcrypt.hashpw(
        password=pass_bytes,
        salt=salt
    )


def verify_password(
        hashed_pass: Union[str, bytes],
        current_pass: Union[str, bytes]
) -> bool:
    hashed_pass = hashed_pass.encode('utf-8') if isinstance(hashed_pass, str) else hashed_pass
    current_pass = current_pass.encode('utf-8') if isinstance(current_pass, str) else current_pass

    return bcrypt.checkpw(
        password=current_pass,
        hashed_password=hashed_pass
    )

async def verify_user(
        token: str = Depends(oauth2_scheme)
) -> UserResponse:
    token_data = verify_jwt_token(token, SECRET_KEY)
    subject = token_data.subject

    if user := await CRUDManagerSQL.get_data(
        model=models.Users,
            row_filter={
                'login': subject.login,
            }
    ):
        return UserResponse(
            **user[0].to_dict()
        )

    raise HTTPException(
        status_code=401,
        detail={'message': 'Пользователь, указанный в токене, не найден'}
    )