from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class User(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    disabled: Optional[bool] = None
    isVerified: Optional[bool] = None
    feedSources: Optional[list[str]] = None
    createdAt: datetime
    updatedAt: datetime


class UserCreate(BaseModel):
    username: Optional[str] = None
    email: EmailStr
    password: Optional[str] = None


class UserInDB(User):
    hashedPassword: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
