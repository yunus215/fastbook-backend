from typing import List, Optional
from sqlmodel import Relationship, SQLModel, Column, Field
import sqlalchemy.dialects.postgresql as pg
from datetime import datetime, date
import uuid


class User(SQLModel, table=True):
    __tablename__ = "users"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    username: str
    email: str
    password_hash: str = Field(exclude=True)
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )
    reviews: List["Review"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<User(username={self.username}, email={self.email}, first_name={self.first_name}, last_name={self.last_name}, role={self.role}, is_verified={self.is_verified}, created_at={self.created_at}, updated_at={self.updated_at}, books={self.books}, reviews={self.reviews})>"


class BookTag(SQLModel, table=True):
    book_id: uuid.UUID = Field(default=None, foreign_key="books.uid", primary_key=True)
    tag_id: uuid.UUID = Field(default=None, foreign_key="tags.uid", primary_key=True)

    def __repr__(self):
        return f"<BookTag(book_id={self.book_id}, tag_id={self.tag_id})>"


class Tag(SQLModel, table=True):
    __tablename__ = "tags"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    name: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(
        link_model=BookTag,
        back_populates="tags",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<Tag(name={self.name}, created_at={self.created_at})>"


class Book(SQLModel, table=True):
    __tablename__ = "books"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, primary_key=True, nullable=False, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    language: str
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(back_populates="books")
    reviews: List["Review"] = Relationship(
        back_populates="book", sa_relationship_kwargs={"lazy": "selectin"}
    )
    tags: List["Tag"] = Relationship(
        link_model=BookTag,
        back_populates="books",
        sa_relationship_kwargs={"lazy": "selectin"},
    )

    def __repr__(self):
        return f"<Book(title={self.title}, author={self.author}, publisher={self.publisher}, published_date={self.published_date}, page_count={self.page_count}, language={self.language}, created_at={self.created_at}, updated_at={self.updated_at}, user={self.user}, reviews={self.reviews}, tags={self.tags})>"


class Review(SQLModel, table=True):
    __tablename__ = "reviews"
    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    rating: int = Field(lt=5)
    review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    update_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional["User"] = Relationship(back_populates="reviews")
    book: Optional["Book"] = Relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review for book {self.book_uid} by user {self.user_uid}>"
