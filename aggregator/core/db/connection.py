from pymongo import MongoClient

from aggregator.config import config
from aggregator.core import GatewayTimeout
from aggregator.core.logger import logger


def get_user_db():
    try:
        db_conn = MongoClient(config.MONGO_DB_URL)
        db = db_conn.prazo
    except Exception as e:
        logger.info(f"Error connecting to Weather DB: {e}.")
        db = None

    return db


class UserDBConnection:
    def __init__(self):
        self.db = get_user_db()
        if self.db is None:
            raise GatewayTimeout(
                "The connection to User DB could not be established."
            )

    def insert_user(self, user):
        return self.db.users.insert_one(user.dict())

    def get_user_by_email(self, email: str):
        return self.db.users.find_one({"email": email})

    def add_feed_sources(self, email: str, sources: list[str]):
        return self.db.users.update_one(
            {"email": email},
            {
                "$set": {"feedSources": []},  # Clear the array
                "$push": {
                    "feedSources": {"$each": sources}
                },  # Push new sources
            },
        )


user_conn = UserDBConnection()
