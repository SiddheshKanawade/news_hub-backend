# /token endpoint to generate token
from datetime import timedelta

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from aggregator.config import config
from aggregator.core import UnauthorizedException
from aggregator.crud import user_crud
from aggregator.schemas import Token, User, UserCreate
from aggregator.utils.auth import authenticate_user, create_access_token

router = APIRouter(prefix="/user", tags=["user"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise UnauthorizedException()
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/", response_model=User)
async def register_user(user_data: UserCreate):
    user = user_crud.get_by_email(user_data.email)
    if user:
        raise UnauthorizedException(
            message=f"User with email {user.email} already exists"
        )

    user = user_crud.create(user_data)

    return user


# login endpoint

# register user endpoint

# insert list of news sources for particular user endpoint

# get list of news sources for particular user endpoint
