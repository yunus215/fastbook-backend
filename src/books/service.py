from sqlmodel.ext.asyncio.session import AsyncSession
from .schemas import BookCreateModel, BookUpdateModel
from sqlmodel import select, desc
from src.db.models import Book
from src.errors import BookNotFound
from datetime import datetime


class BookService:
    async def get_all_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        results = await session.exec(statement)
        return results.all()

    async def get_user_books(self, user_uid: str, session: AsyncSession):
        statement = (
            select(Book)
            .where(Book.user_uid == user_uid)
            .order_by(desc(Book.created_at))
        )
        result = await session.exec(statement)
        return result.all()

    async def get_book(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        if not book:
            raise BookNotFound()
        return book

    async def create_book(
        self, book_create_data: BookCreateModel, user_uid: str, session: AsyncSession
    ):
        book_data_dict = book_create_data.model_dump()
        new_book = Book(**book_data_dict)
        new_book.published_date = datetime.strptime(
            book_create_data.published_date, "%Y-%m-%d"
        )
        new_book.user_uid = user_uid
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_uid: str, book_update_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book(book_uid, session)
        book_data_dict = book_update_data.model_dump(exclude_unset=True)
        for key, value in book_data_dict.items():
            setattr(book_to_update, key, value)
        session.add(book_to_update)
        await session.commit()
        await session.refresh(book_to_update)
        return book_to_update

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book(book_uid, session)
        await session.delete(book_to_delete)
        await session.commit()
