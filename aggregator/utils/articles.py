from datetime import datetime

import pytz
import requests

from aggregator.config import config
from aggregator.core import logger
from aggregator.schemas import Attachment, Author, NewsArticle


def convert_ist_to_utc(date: str):
    ist_datetime = datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ")
    ist_timezone = pytz.timezone("Asia/Kolkata")
    ist_aware_datetime = ist_timezone.localize(ist_datetime)
    utc_datetime = ist_aware_datetime.astimezone(pytz.utc)
    utc_datetime_str = utc_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    return utc_datetime_str


def get_articles(category: str):
    articles = []
    headers = {
        "authority": "rss.app",
        "method": "GET",
        "scheme": "https",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Sec-Ch-Ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?1",
        "Sec-Ch-Ua-Platform": '"Android"',
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36",
    }

    if category == "general":
        feed_url = config.GENERAL_FEED_URL
    elif category == "politics":
        feed_url = config.POLITICS_FEED_URL
    elif category == "business":
        feed_url = config.BUSINESS_FEED_URL
    elif category == "scienceandtechnology":
        feed_url = config.SCIENCE_TECHNOLOGY_FEED_URL
    elif category == "sports":
        feed_url = config.SPORTS_FEED_URL
    elif category == "entertainment":
        feed_url = config.ENTERTAINMENT_FEED_URL

    try:
        response = requests.get(feed_url, headers=headers)
        response.raise_for_status()  # Check if the request was successful

        for article in response.json().get("items", []):
            if "The Times of India" in article["authors"][0]["name"]:
                article["date_published"] = convert_ist_to_utc(
                    article["date_published"]
                )

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
                        for author in article.get("authors", [])
                    ],
                    attachments=[
                        Attachment(url=attachment["url"])
                        for attachment in article.get("attachments", [])
                    ],
                )
            )
        return articles
    except Exception as e:
        logger.error(f"Error fetching general articles: {str(e)}")
        return articles
