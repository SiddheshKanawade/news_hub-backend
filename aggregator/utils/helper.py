from datetime import datetime, timedelta

import pandas as pd
import pytz

from aggregator.constants import NSE_COMPANIES_CSV


# Have all datetimes in UTC while storing in the database
def get_relative_time(published_at):
    # Assuming publishedAt is an ISO 8601 string (e.g., "2023-10-24T14:00:00Z")
    if isinstance(published_at, str):
        article_time = datetime.fromisoformat(
            published_at.replace("Z", "+00:00")
        ).replace(tzinfo=pytz.UTC)
    else:
        article_time = published_at.replace(tzinfo=pytz.UTC)
    current_time = datetime.now(tz=pytz.UTC)

    # Calculate the time difference
    time_difference = current_time - article_time

    # Format the time difference
    if time_difference < timedelta(minutes=1):
        return "just now"
    elif time_difference < timedelta(hours=1):
        minutes = int(time_difference.total_seconds() // 60)
        return f"{minutes} mins ago"
    elif time_difference < timedelta(days=1):
        hours = int(time_difference.total_seconds() // 3600)
        return f"{hours} hours ago"
    else:
        days = time_difference.days
        return f"{days} days ago"


def fix_live_response(data):
    data = [
        {
            "source": article["source"],
            "author": article["author"],
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "urlToImage": article["image"],
            "publishedAt": get_relative_time(article["published_at"]),
            "country": article["country"],
            "language": article["language"],
            "content": None,
            "category": article["category"],
        }
        for article in data
    ]
    return data


def fix_response(data):
    data = [
        {
            "source": article["source"],
            "author": article["author"],
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "urlToImage": article["urlToImage"],
            "publishedAt": get_relative_time(article["publishedAt"]),
            "content": article["content"],
            "category": None,
            "language": None,
            "country": None,
        }
        for article in data
    ]
    return data


def fix_feed_articles(data):
    data = [
        {
            "source": article["source"][0]["name"]
            if article["source"]
            else None,
            "author": None,
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "urlToImage": article["imageUrl"],
            "publishedAt": get_relative_time(article["datePublished"]),
            "content": article["contentHtml"],
            "category": "general",
            "language": None,
            "country": None,
        }
        for article in data
    ]

    return data


def get_nse_companies():
    df_nse = pd.read_csv(NSE_COMPANIES_CSV)

    # Create NSECompany instances for each row
    companies = []
    for _, row in df_nse.iterrows():
        company = {
            "symbol": row["SYMBOL"],
            "name": row["NAME OF COMPANY"],
            "series": row[" SERIES"],
            "dateOfListing": row[" DATE OF LISTING"],
            "paidUpValue": int(row[" PAID UP VALUE"]),
            "marketLot": int(row[" MARKET LOT"]),
            "isinNumber": row[" ISIN NUMBER"],
            "faceValue": int(row[" FACE VALUE"]),
        }
        companies.append(company)

    return companies


def get_acronym(name):
    return "".join([word[0] for word in name.split(" ")])


def remove_limited_from_name(name):
    if "Limited" in name or "Ltd" in name:
        return name.replace("Limited", "").replace("Ltd", "").strip()


def get_nse_ticker(name):
    # Get ticker
    df_nse = pd.read_csv(NSE_COMPANIES_CSV)
    company_row = df_nse[df_nse["NAME OF COMPANY"] == name]
    return company_row["SYMBOL"].values[0] if not company_row.empty else None


def remove_duplicates(data):
    unique_data = []
    for article in data:
        if article not in unique_data:
            unique_data.append(article)
    return unique_data
