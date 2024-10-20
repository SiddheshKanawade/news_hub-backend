from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from aggregator.config import config
from aggregator.core import NotFoundException, UnauthorizedException
from aggregator.core.db import user_conn
from aggregator.schemas import TokenData, UserInDB

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token"
)  # listen to /token endpoint to generate token


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(email: str):
    return user_conn.get_user_by_email(email)


def authenticate_user(email: str, password: str):
    user = get_user(email)
    user = UserInDB(**user)
    if not user:
        return False
    if not verify_password(password, user.hashedPassword):
        return False

    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM
    )
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):  # listen to /token endpoint to generate token
    try:
        payload = jwt.decode(
            token, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
        print(payload)
        username: str = payload.get("sub")
        if username is None:
            raise InvalidCredentialsException

        token_data = TokenData(username=username)
    except JWTError:
        raise UnauthorizedException

    user = get_user(username=token_data.username)
    if user is None:
        raise UnauthorizedException

    return user


async def get_current_active_user(
    current_user: UserInDB = Depends(get_current_user),
):
    if current_user.disabled:
        raise NotFoundException(message="Inactive user")

    return current_user
