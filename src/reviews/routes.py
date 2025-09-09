from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import RoleChecker, get_current_user
from src.db.main import get_session
from src.auth.schemas import UserModel
from .schemas import ReviewCreateModel, ReviewModel
from .service import ReviewService

review_router = APIRouter()
review_service = ReviewService()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@review_router.get(
    "/", response_model=List[ReviewModel], dependencies=[admin_role_checker]
)
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all reviews in the system.

    This endpoint is restricted to administrators only and returns
    all reviews across all books in the system.

    Returns:
        List[ReviewModel]: A list of all reviews ordered by creation date (newest first)

    Raises:
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view all reviews
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    reviews = await review_service.get_all_reviews(session)
    return reviews


@review_router.get(
    "/{review_uid}", response_model=ReviewModel, dependencies=[user_role_checker]
)
async def get_review(review_uid: str, session: AsyncSession = Depends(get_session)):
    """
    Retrieve a specific review by its unique identifier.

    This endpoint allows authenticated users to get details of a specific review
    using its unique identifier.

    Args:
        review_uid (str): The unique identifier of the review

    Returns:
        ReviewModel: The requested review details

    Raises:
        404: If the review with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view the review
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    review = await review_service.get_review(review_uid, session)
    return review


@review_router.post(
    "/book/{book_uid}", response_model=ReviewModel, dependencies=[user_role_checker]
)
async def add_review_to_book(
    book_uid: str,
    review_create_data: ReviewCreateModel,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Add a review to a specific book.

    This endpoint allows authenticated users to create a review for a book.
    Each user can review a book, providing rating and optional text feedback.

    Args:
        book_uid (str): The unique identifier of the book to review
        review_create_data (ReviewCreateModel): The review data including rating and content

    Returns:
        ReviewModel: The newly created review

    Raises:
        404: If the book with the specified UID is not found / if the user is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to add a review
        500: If there is an internal server error during the creation (e.g., database issues, etc)
    """
    new_review = await review_service.add_review_to_book(
        user_email=current_user.email,
        review_create_data=review_create_data,
        book_uid=book_uid,
        session=session,
    )
    return new_review


@review_router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    """
    Delete a review.

    This endpoint allows authenticated users to delete their own reviews.
    Users can only delete reviews they have created.

    Args:
        review_uid (str): The unique identifier of the review to delete

    Returns:
        None: Returns 204 No Content on successful deletion

    Raises:
        404: If the review with the specified UID is not found
        403: If the user attempts to delete a review they didn't create
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to delete the review
        500: If there is an internal server error during the deletion (e.g., database issues, etc)
    """
    await review_service.delete_review_to_from_book(
        review_uid=review_uid, user_email=current_user.email, session=session
    )
