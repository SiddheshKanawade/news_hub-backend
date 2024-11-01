from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from aggregator.config import config
from aggregator.core import (
    BadRequestException,
    DuplicateValueException,
    InsufficientDataException,
    InternalServerException,
    NotFoundException,
    UnauthorizedException,
    logger,
)
from aggregator.core.db import db_conn
from aggregator.crud import user_crud
from aggregator.models.news import Article
from aggregator.paginate import Paginate
from aggregator.schemas import Token, User, UserCreate
from aggregator.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from aggregator.utils.helper import fix_feed_articles

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


@router.post(
    "/register", response_model=User, status_code=status.HTTP_201_CREATED
)
async def register_user(user_data: UserCreate):
    user = user_crud.get_by_email(user_data.email)
    if user:
        logger.info(f"User with email {user.email} already exists")
        raise DuplicateValueException(
            message=f"User with email {user.email} already exists"
        )

    user = user_crud.create(user_data)

    return user


@router.post("/login", response_model=User)
async def read_user_me(user: User = Depends(get_current_active_user)):
    return user


@router.post("/feed-sources", status_code=status.HTTP_201_CREATED)
def add_user_feed_sources(
    current_user: User = Depends(get_current_active_user),
    sources: list[str] = None,  # list of code of sources
    page: int = 1,
    perPage: int = 10,
) -> Any:
    if not sources:
        raise InsufficientDataException(message="Sources are required")

    try:
        user_crud.add_feed_sources(current_user.email, sources)
        return {"message": "Feed sources added successfully"}
    except Exception as e:
        raise InternalServerException(message=str(e))


@router.post(
    "/feed", response_model=Paginate[Article], status_code=status.HTTP_200_OK
)
def get_user_feed_news(
    category: str = None,
    current_user: User = Depends(get_current_active_user),
    page: int = 1,
    perPage: int = 10,
) -> Any:
    """Get category based category news

    Params:
        Category: str = general, politics, sports, business, health, science, technology, entertainment
        Sources: list[str] = List of sources to get news from

    Returns:
        Any: _description_
    """
    if not current_user.feedSources:
        logger.info(f"No feed sources found for {current_user.email}")
        raise BadRequestException("No feed sources found")

    try:
        logger.info(f"Fetching feed news for {current_user.email}")
        data = db_conn.get_feed_news(
            current_user.feedSources, category=category
        )
        data = fix_feed_articles(data)
        return Paginate[Article](
            results=data,
            total=len(data),
            page=page,
            perPage=perPage,
        )
    except Exception as e:
        raise NotFoundException(message=f"Error fetching feed news: {e}")
