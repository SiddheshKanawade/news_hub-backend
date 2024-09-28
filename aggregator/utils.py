import io

import pandas as pd
import requests

from aggregator.constants import NSE_COMPANIES_URL


def fix_live_response(data):
    data = [
        {
            "source": article["source"],
            "author": article["author"],
            "title": article["title"],
            "description": article["description"],
            "url": article["url"],
            "urlToImage": article["image"],
            "publishedAt": article["published_at"],
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
            "publishedAt": article["publishedAt"],
            "content": article["content"],
            "category": None,
            "language": None,
            "country": None,
        }
        for article in data
    ]
    return data


def get_nse_companies():
    # create Session from 'real' browser
    headers = {"User-Agent": "Mozilla/5.0"}

    s = requests.Session()
    s.headers.update(headers)

    r = s.get(NSE_COMPANIES_URL)
    s.close()

    df_nse = pd.read_csv(io.BytesIO(r.content))

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
