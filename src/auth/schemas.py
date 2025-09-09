from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date
import uuid
from src.books.schemas import BookModel
from src.reviews.schemas import ReviewModel


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserBooksModel(UserModel):
    books: List[BookModel]
    reviews: List[ReviewModel]


class UserCreateModel(BaseModel):
    first_name: str = Field(max_length=25)
    last_name: str = Field(max_length=25)
    username: str = Field(max_length=25)
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class UserLoginModel(BaseModel):
    email: str = Field(max_length=40)
    password: str = Field(min_length=6)


class EmailModel(BaseModel):
    addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
    confirm_new_password: str
