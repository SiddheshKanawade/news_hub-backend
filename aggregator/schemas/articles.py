from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Author(BaseModel):
    name: str


class Attachment(BaseModel):
    url: str


class NewsArticle(BaseModel):
    url: str = Field(..., description="URL of the article")
    title: str = Field(..., description="Title of the article")
    description: Optional[str] = Field(
        "", description="Text content of the article"
    )
    contentHtml: Optional[str] = Field(
        "", description="HTML content of the article"
    )
    imageUrl: Optional[str] = Field(None, description="URL of the image")
    datePublished: Optional[datetime] = Field(
        None, description="Publication date of the article"
    )
    source: Optional[List[Author]] = Field([], description="List of authors")
    attachments: Optional[List[Attachment]] = Field(
        [], description="List of attachments"
    )

    class Config:
        schema_extra = {
            "example": {
                "url": "https://timesofindia.indiatimes.com/videos/international/iraqi-resistance-rains-drone-barrage-on-vital-idf-sites-flaunt-attack-video-watch/videoshow/114834888.cms",
                "title": "Iraqi Resistance Rains Drone-Barrage On Vital IDF Sites, Flaunt Attack Video",
                "description": "",
                "contentHtml": "<div>...</div>",
                "imageUrl": "https://static.toiimg.com/photo/114834888.cms",
                "datePublished": "2024-11-01T09:30:36.000Z",
                "source": [{"name": "TIMESOFINDIA.COM"}],
                "attachments": [
                    {"url": "https://static.toiimg.com/photo/114834888.cms"}
                ],
            }
        }
