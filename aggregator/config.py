import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv(dotenv_path="./.env")

LOG_FILE_NAME = "aggregator-api"


class Config(BaseSettings):
    DEBUG: bool = True
    TESTING: bool = os.getenv("TESTING", "False").lower() == "true"
    APP_NAME: str = "Aggregator"
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY")
    MEDIASTACK_API_KEY: str = os.getenv("MEDIASTACK_API_KEY")
    MONGO_DB_URL: str = os.getenv("MONGO_DB_URL")
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = os.getenv(
        "ACCESS_TOKEN_EXPIRE_MINUTES", 120
    )
    GENERAL_FEED_URL: str = os.getenv("GENERAL_FEED_URL")
    POLITICS_FEED_URL: str = os.getenv("POLITICS_FEED_URL")
    BUSINESS_FEED_URL: str = os.getenv("BUSINESS_FEED_URL")


class LocalConfig(Config):
    pass


class ProductionConfig(Config):
    pass


def get_config():
    env = os.getenv("FAST_ENV", "local")
    config_type = {
        "local": LocalConfig(),
        "production": ProductionConfig(),
    }
    return config_type[env]


config: Config = get_config()
