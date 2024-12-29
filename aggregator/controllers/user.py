from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import MessageSchema, MessageType

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
    create_url_safe_token,
    get_current_active_user,
    verify_url_safe_token,
)
from aggregator.utils.helper import fix_feed_articles
from aggregator.utils.mail import EmailUtils

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

    # Add user to DB
    user = user_crud.create(user_data)

    # Generate verification token
    url_token = create_url_safe_token(
        {"email": user.email, "username": user.username}
    )
    verification_link = f"{config.PRAZO_DOMAIN}/verify/{url_token}"

    # Send verification email, might be async.
    html = f"""<p>Hi {user.username}, <br> 
        Please click on <a href="{verification_link}">link</a> to verify your email address.</p><br> {verification_link} """

    message = MessageSchema(
        subject="Prazo - Verify your email",
        recipients=[user.email],
        body=html,
        subtype=MessageType.html,
    )

    try:
        await EmailUtils().send_email(message)
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        raise InternalServerException(
            message="Error sending verification email"
        )

    # Why am I returning user? just return success message
    return user


@router.post("/me", response_model=User)
async def read_user_me(user: User = Depends(get_current_active_user)):
    logger.info(f"User {user.email} fetched successfully")
    return user


@router.post("/feed-sources", status_code=status.HTTP_201_CREATED)
async def add_user_feed_sources(
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
async def get_user_feed_news(
    category: str = "general",
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
        logger.info(f"Fetching feed news for {category}")
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


@router.get("/verify/{token}")
async def verify_user_email(token: str):
    """Add condition to expire token after 7 days"""
    try:
        data = verify_url_safe_token(token)
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        raise BadRequestException(message="Invalid token")

    email = data.get("email")
    user = user_crud.get_by_email(email)
    if not user:
        raise NotFoundException(message="User not found")

    user_crud.update(email, {"isVerified": True})
    logger.info(f"User {email} verified successfully")

    return {"message": "User verified successfully"}


@router.post("/send-verification-email")
async def send_verification_email(
    current_user: User = Depends(get_current_active_user),
):
    url_token = create_url_safe_token(
        {"email": current_user.email, "username": current_user.username}
    )
    verification_link = f"{config.PRAZO_DOMAIN}/verify/{url_token}"

    # Send verification email, might be async.
    html = f"""<p>Hi {current_user.username}, <br> 
        Please click on <a href="{verification_link}">link</a> to verify your email address.</p><br> {verification_link} """

    message = MessageSchema(
        subject="Prazo - Verify your email",
        recipients=[current_user.email],
        body=html,
        subtype=MessageType.html,
    )

    try:
        logger.info(f"Sending verification email to {current_user.email}")
        await EmailUtils().send_email(message)
    except Exception as e:
        logger.error(f"Error sending verification email: {str(e)}")
        raise InternalServerException(
            message="Error sending verification email"
        )

    return {"message": "Verification email sent successfully"}
