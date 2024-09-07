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
