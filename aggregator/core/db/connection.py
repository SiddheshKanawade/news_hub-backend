from pymongo import MongoClient

from aggregator.config import config
from aggregator.core import GatewayTimeout
from aggregator.core.logger import logger
from aggregator.utils.articles import get_general_articles


def get_user_db():
    try:
        db_conn = MongoClient(config.MONGO_DB_URL)
        db = db_conn.prazo
    except Exception as e:
        logger.info(f"Error connecting to Weather DB: {e}.")
        db = None

    return db


class DBConnection:
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
        try:
            # First, clear the array
            self.db.users.update_one(
                {"email": email},
                {"$set": {"feedSources": []}},  # Clear the array
            )

            # Then, push new sources into the now-empty array
            self.db.users.update_one(
                {"email": email},
                {
                    "$push": {"feedSources": {"$each": sources}}
                },  # Push new sources
            )
        except Exception as e:
            logger.error(f"Error adding feed sources: {e}")
            raise e
        return

    def add_general_news(self):
        try:
            articles = get_general_articles()

            if len(articles) == 0:
                logger.info("No general news found from Feed")
                
            for article in articles:
                article = article.dict()
                self.db.general.update_one(
                    {"url": article["url"]},  # Filter for existing URL
                    {
                        "$setOnInsert": article
                    },  # Insert only if `url` is not found
                    upsert=True,  # Creates a new document if no match is found
                )
        except Exception as e:
            logger.error(f"Error adding general news: {e}")
            raise e
        
    def get_general_news(self):
        return list(self.db.general.find({}).sort("datePublished", -1))


db_conn = DBConnection()
