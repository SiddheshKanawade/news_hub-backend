import os
from datetime import datetime
from typing import Any

import dotenv
import requests
from fastapi import APIRouter

from aggregator.exceptions import NotFoundException
from aggregator.model import Article, Source
from aggregator.paginate import Paginate

dotenv.load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
URL = "https://newsapi.org/v2/"

router = APIRouter()


@router.get("/sources/")
def get_news_sources(
    country: str = None,
    page: int = 1,
    perPage: int = 10,
):
    url = f"{URL}/top-headlines/sources"
    params = {
        "apiKey": NEWS_API_KEY,
        "language": "en",
    }
    if country:
        params["country"] = country

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise NotFoundException(f"Error fetching news: {response.json()}")

    return Paginate[Source](
        results=response.json()["sources"],
        total=len(response.json()["sources"]),
        page=page,
        perPage=perPage,
    )


@router.post("/news/", response_model=Paginate[Article])
def get_news(
    startDate: datetime = None,
    endDate: datetime = None,
    keyWords: list[str] = None,
    endPoint: str = "everything",
    language: str = "en",
    sources: list[str] = None,
    threshold: int = 10,
    page: int = 1,
    perPage: int = 10,
) -> Any:
    """Retrieve hailstorm details

    Args:
        startDate (datetime): start date in format YYYY-MM-DD
        endDate (datetime): end date in format YYYY-MM-DD
        keyWords (list[str]): List of keywords to search
        endPoint (str, optional): Defaults to "everything".
        language (str, optional): Defaults to "en".
        threshold (int, optional): Total Number of news articles to return. Defaults to 10.
        page (int, optional): Defaults to 1.
        perPage (int, optional): Defaults to 10.

    Raises:
        NotFoundException: Raise when no news found
        BadRequestException: Raise when no address or coordinates or polygon provided
        InternalServerException: Raise when error fetching coordinates from address or polygon or processing entries from DB

    Returns:
        Paginate[NoaaV1]: Returns list of paginated hailstorm details for given location and time frame
    """
    params = {
        "apiKey": NEWS_API_KEY,
        "language": language,
        "sortBy": "relevancy",
        "searcgIn": "title",
        "pageSize": 10,
        "page": 1,
    }

    if not startDate:
        params["sortBy"] = "publishedAt"

    if startDate:
        start_date = startDate.strftime("%Y-%m-%d")
        params["from"] = start_date
    if endDate:
        end_date = endDate.strftime("%Y-%m-%d")
        params["to"] = end_date

    if keyWords:
        query = " OR ".join(keyWords)
        params["q"] = query

    if sources:
        params["sources"] = ",".join(sources)

    url = f"{URL}/{endPoint}"

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise NotFoundException(f"Error fetching news: {response.json()}")

    if response.json()["totalResults"] == 0:
        raise NotFoundException("No news found")
    elif response.json()["totalResults"] < threshold:
        return Paginate[Article](
            results=response.json()["articles"],
            total=len(response.json()["articles"]),
            page=page,
            perPage=perPage,
        )
    else:
        return Paginate[Article](
            results=response.json()["articles"][:threshold],
            total=len(response.json()["articles"][:threshold]),
            page=page,
            perPage=perPage,
        )


@router.get("/items/")
def read_items(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}
