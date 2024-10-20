from fastapi import APIRouter

from . import news, user

v1_router = APIRouter()

v1_router.include_router(news.router)
v1_router.include_router(user.router)
