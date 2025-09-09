from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime, date
import uuid
from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel


class BookModel(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    created_at: datetime
    updated_at: datetime


class BookDetailModel(BookModel):
    reviews: List[ReviewModel]
    tags: List[TagModel]


class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    language: str


class BookUpdateModel(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: Optional[str] = None
