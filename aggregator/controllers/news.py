"""TODO
1. Code duplication in news endpoints
"""

from datetime import datetime, timedelta
from typing import Any

import dotenv
import requests
from fastapi import APIRouter

from aggregator.config import config
from aggregator.constants import LIVE_LANGUAGES, MEDIASTACK_URL, NEWS_API_URL
from aggregator.core import NotFoundException, logger
from aggregator.paginate import Paginate
from aggregator.schemas.news import Article, NSECompany, Source
from aggregator.utils.helper import (
    fix_live_response,
    fix_response,
    get_acronym,
    get_nse_companies,
    get_nse_ticker,
    remove_duplicates,
    remove_limited_from_name,
)

dotenv.load_dotenv()

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/sources/", response_model=Paginate[Source])
def get_news_sources(
    country: str = None,
    page: int = 1,
    perPage: int = 10,
):
    url = f"{NEWS_API_URL}/top-headlines/sources"
    params = {
        "apiKey": config.NEWS_API_KEY,
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


@router.post("/", response_model=Paginate[Article])
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
        "apiKey": config.NEWS_API_KEY,
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

    url = f"{NEWS_API_URL}/{endPoint}"

    response = requests.get(url, params=params)

    if response.status_code != 200:
        raise NotFoundException(f"Error fetching news: {response.json()}")

    if response.json()["totalResults"] == 0:
        raise NotFoundException("No news found")
    elif response.json()["totalResults"] < threshold:
        data = fix_response(response.json()["articles"])
        return Paginate[Article](
            results=data,
            total=len(data),
            page=page,
            perPage=perPage,
        )
    else:
        data = fix_response(response.json()["articles"])
        return Paginate[Article](
            results=data[:threshold],
            total=len(data[:threshold]),
            page=page,
            perPage=perPage,
        )


@router.post("/live", response_model=Paginate[Article])
def get_live_news(
    startDate: datetime = None,
    endDate: datetime = None,
    keyWords: list[str] = None,
    sources: list[str] = None,
    endPoint: str = "news",
    language: str = "en",
    categories: list[str] = None,
    retries: int = 3,
    page: int = 1,
    perPage: int = 10,
) -> Any:
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
        start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

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

    if sources:
        params["sources"] = ",".join(sources)

    url = f"{MEDIASTACK_URL}/{endPoint}"

    attempts = 0
    while attempts < retries:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            break
        attempts += 1

    if response.status_code == 404:
        logger.info(f"No news found for {keyWords}")
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


@router.post("/ticker", response_model=Paginate[Article])
def get_ticker_news(
    startDate: datetime = None,
    endDate: datetime = None,
    keyWords: list[str] = None,
    endPoint: str = "news",
    language: str = "en",
    sources: list[str] = None,
    threshold: int = 1000,
    categories: list[str] = None,
    page: int = 1,
    perPage: int = 10,
) -> Any:
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
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    if endDate:
        end_date = endDate.strftime("%Y-%m-%d")
    else:
        end_date = datetime.now().strftime("%Y-%m-%d")

    params["date"] = f"{start_date},{end_date}"

    # Get other company acronyms
    if keyWords:
        modified_keywords = []
        for keyword in keyWords:
            acronym = get_acronym(keyword)
            company_name = remove_limited_from_name(keyword)
            ticker = get_nse_ticker(keyword)
            modified_keywords.append(acronym)
            modified_keywords.append(company_name)
            modified_keywords.append(ticker)

    if sources:
        params["sources"] = ",".join(sources)

    if categories:
        params["categories"] = ",".join(categories)

    url = f"{MEDIASTACK_URL}/{endPoint}"

    if keyWords:
        accumulated_data = []
        for keyword in modified_keywords:
            params["keywords"] = keyword
            response = requests.get(url, params=params)
            if response.status_code != 200:
                print(f"Error fetching news: {response.json()} for {keyword}")
                continue
            if response.json()["pagination"]["total"] == 0:
                print(f"No news found for {keyword}")
                continue
            accumulated_data += response.json()["data"]

        if len(accumulated_data) == 0:
            raise NotFoundException("No news found")

        unique_data = remove_duplicates(accumulated_data)
        data = fix_live_response(unique_data)

        return Paginate[Article](
            results=data,
            total=len(data),
            page=page,
            perPage=perPage,
        )

    else:
        response = requests.get(url, params=params)
        if response.status_code != 200:
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


@router.get("/nse-companies", response_model=Paginate[NSECompany])
def get_nse_news(
    page: int = 1,
    perPage: int = 10,
):
    ## IMPLEMENT WEB SOCKETS FOR CONTINUOUS UPDATES
    try:
        data = get_nse_companies()
    except Exception as e:
        raise NotFoundException(f"Error fetching NSE companies: {e}")
    return Paginate[NSECompany](
        results=data,
        total=len(data),
        page=page,
        perPage=perPage,
    )
