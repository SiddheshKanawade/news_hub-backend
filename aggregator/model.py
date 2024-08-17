from typing import Optional

from pydantic import BaseModel, HttpUrl


class Source(BaseModel):
    id: Optional[str]
    name: str


class Article(BaseModel):
    source: Source
    author: Optional[str]
    title: str
    description: Optional[str]
    url: HttpUrl
    urlToImage: Optional[HttpUrl]
    publishedAt: str
    content: Optional[str]
