from datetime import datetime, timedelta
from typing import Any

import requests
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from aggregator.config import config
from aggregator.constants import LIVE_LANGUAGES, MEDIASTACK_URL
from aggregator.core import (
    BadRequestException,
    DuplicateValueException,
    InsufficientDataException,
    InternalServerException,
    NotFoundException,
    UnauthorizedException,
    logger,
)
from aggregator.crud import user_crud
from aggregator.paginate import Paginate
from aggregator.schemas import Token, User, UserCreate
from aggregator.schemas.news import Article
from aggregator.utils.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from aggregator.utils.helper import fix_live_response

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


@router.post(
    "/feed", response_model=Paginate[Article], status_code=status.HTTP_200_OK
)
def get_user_feed_news(
    startDate: datetime = None,
    endDate: datetime = None,
    keyWords: list[str] = None,
    endPoint: str = "news",
    language: str = "en",
    categories: list[str] = None,
    retries: int = 3,
    current_user: User = Depends(get_current_active_user),
    page: int = 1,
    perPage: int = 10,
) -> Any:
    if not current_user.feedSources:
        logger.info(f"No feed sources found for {current_user.email}")
        raise BadRequestException("No feed sources found")

    if language not in LIVE_LANGUAGES.keys():
        raise NotFoundException(f"Language {language} not supported")

    params = {
        "access_key": config.MEDIASTACK_API_KEY,
        "languages": language,
        "limit": 100,
    }

    if startDate:
        start_date = startDate.strftime("%Y-%m-%d")
    else:
        start_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    if endDate:
        end_date = endDate.strftime("%Y-%m-%d")
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")

    params["date"] = f"{start_date},{end_date}"

    if keyWords:
        query = " +".join(keyWords)
        params["keywords"] = query

    if categories:
        params["categories"] = ",".join(categories)

    params["sources"] = ",".join(current_user.feedSources)

    url = f"{MEDIASTACK_URL}/{endPoint}"

    attempts = 0
    while attempts < retries:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            break
        attempts += 1

    if response.status_code == 404:
        logger.info(f"No news found for {current_user.feedSources}")
        raise NotFoundException(f"Error fetching news: {response.json()}")
    elif response.status_code != 200:
        logger.info(f"Error fetching news: {response.json()}")
        raise NotFoundException(f"Error fetching news: {response.json()}")

    if response.json()["pagination"]["total"] == 0:
        raise NotFoundException("No news found")
    else:
        data = fix_live_response(response.json()["data"])
        return Paginate[Article](
            results=data,
            total=len(data),
            page=page,
            perPage=perPage,
        )


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
