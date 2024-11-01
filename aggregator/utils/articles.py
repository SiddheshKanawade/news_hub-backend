import requests

from aggregator.config import config
from aggregator.core import logger
from aggregator.schemas import Attachment, Author, NewsArticle


def get_general_articles():

    articles = []
    try:
        response = requests.get(config.GENERAL_FEED_URL)

        for article in response.json()["items"]:
            articles.append(
                NewsArticle(
                    url=article["url"],
                    title=article["title"],
                    description=article["content_text"],
                    contentHtml=article["content_html"],
                    imageUrl=article["image"],
                    datePublished=article["date_published"],
                    source=[
                        Author(name=author["name"])
                        for author in article["authors"]
                    ]
                    if "authors" in article.keys() and article["authors"]
                    else [],
                    attachments=[
                        Attachment(url=attachment["url"])
                        for attachment in article["attachments"]
                    ]
                    if "attachements" in article.keys()
                    and article["attachments"]
                    else [],
                )
            )
        return articles
    except Exception as e:
        logger.error(f"Error fetching general articles: {str(e)}")
        return articles
