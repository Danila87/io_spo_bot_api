from datetime import datetime
from typing import Optional

from pydantic import BaseModel

class UserLogin(BaseModel):
    login: str
    password: str

class UserCreate(UserLogin):
    email: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    login: str
    email: Optional[str] = None

class Token(BaseModel):
    token: str
    token_type: str

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class SubjectData(BaseModel):
    login: str
    email: Optional[str] = None

class TokenData(BaseModel):
    exp: datetime
    subject: Optional[SubjectData] = None
