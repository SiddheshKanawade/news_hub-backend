from typing import Optional, Union

from pydantic import BaseModel, HttpUrl


class NewsSource(BaseModel):
    id: Optional[str]
    name: str


class Article(BaseModel):
    source: Union[NewsSource, str]
    author: Optional[str]
    title: str
    description: Optional[str]
    url: HttpUrl
    urlToImage: Optional[HttpUrl]
    publishedAt: str
    content: Optional[str]
    category: Optional[str]
    language: Optional[str]
    country: Optional[str]


class Source(BaseModel):
    id: Optional[str]
    name: str
    url: Optional[HttpUrl]
    description: Optional[str]
    category: Optional[str]
    language: Optional[str]
    country: Optional[str]
