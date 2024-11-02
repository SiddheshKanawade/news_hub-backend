import pytz
from pymongo import MongoClient
from datetime import datetime, timedelta

from aggregator.config import config
from aggregator.core import GatewayTimeout
from aggregator.core.logger import logger
from aggregator.utils.articles import get_articles


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
    
    def _is_news_updated(self):
        metadata = self.db.metadata.find_one()
        
        last_updated = metadata.get("lastUpdated").replace(tzinfo=pytz.UTC) if metadata else None
        current_time = datetime.now(tz=pytz.UTC)
        
        if current_time - last_updated > timedelta(minutes=15):
            return True
        return False

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
    
    def _insert_articles(self, articles, category):
        if len(articles) == 0:
                logger.info(f"No {category} news found from Feed")
                
        for article in articles:
            article = article.dict()
            self.db[category].update_one(
                {"url": article["url"]},  # Filter for existing URL
                {
                    "$setOnInsert": article
                },  # Insert only if `url` is not found
                upsert=True,  # Creates a new document if no match is found
            )
            
    def _add_general_news(self):
        logger.info("Adding general news")
        general_articles = get_articles("general")
        self._insert_articles(general_articles, "general")
        return
    
    def _add_politics_news(self):
        logger.info("Adding politics news")
        politics_articles = get_articles("politics")
        self._insert_articles(politics_articles, "politics")
        return

    def add_news(self):
        try:
            if not self._is_news_updated():
                logger.info("News is already updated")
                return

            self._add_general_news()
            self._add_politics_news()
            
            # Update metadata
            self.db.metadata.update_one(
                {},
                {
                    "$set": {"lastUpdated": datetime.now(tz=pytz.UTC)}
                },
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error adding general news: {e}")
            raise e

    def get_news(self, category=None):
        return list(
            self.db[category].find({}).limit(100).sort("datePublished", -1)
        )

    def get_feed_news(self, sources, category):
        return list(
            self.db[category].find({"source.name": {"$in": sources}})
            .limit(100)
            .sort("datePublished", -1)
        )


db_conn = DBConnection()
