from sqlmodel import desc, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.service import UserService
from src.books.service import BookService
from src.db.models import Review
from src.errors import UserNotFound, ReviewNotFound, ReviewAccessDenied
from .schemas import ReviewCreateModel

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def get_review(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        review = result.first()
        if not review:
            raise ReviewNotFound()
        return review

    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        return result.all()

    async def add_review_to_book(
        self,
        user_email: str,
        book_uid: str,
        review_create_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        book = await book_service.get_book(book_uid=book_uid, session=session)
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFound()
        review_data_dict = review_create_data.model_dump()
        new_review = Review(**review_data_dict, user=user, book=book)
        session.add(new_review)
        await session.commit()
        return new_review

    async def delete_review_to_from_book(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(user_email, session)
        review = await self.get_review(review_uid, session)
        if review.user != user:
            raise ReviewAccessDenied()
        await session.delete(review)
        await session.commit()
