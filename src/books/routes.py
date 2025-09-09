from fastapi import APIRouter, status, Depends
from src.books.schemas import (
    BookModel,
    BookCreateModel,
    BookUpdateModel,
    BookDetailModel,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.service import BookService
from src.db.main import get_session
from typing import List
from src.auth.dependencies import AccessTokenBearer, RoleChecker
from src.errors import BookNotFound

book_router = APIRouter()
book_service = BookService()
access_token_bearer = AccessTokenBearer()
role_checker = Depends(RoleChecker(allowed_roles=["admin", "user"]))


@book_router.get("/", response_model=List[BookModel], dependencies=[role_checker])
async def get_all_books(
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    Retrieve all books from the database.

    This endpoint returns a list of all books in the system, ordered by
    creation date (newest first). Requires user authentication.

    Args:
        token_details (dict): Access token details from the Authorization header

    Returns:
        List[BookModel]: A list of all books with their basic information

    Raises:
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view books
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    books = await book_service.get_all_books(session)
    return books


@book_router.get(
    "/user/{user_uid}", response_model=List[BookModel], dependencies=[role_checker]
)
async def get_user_book_submissions(
    user_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    Retrieve all books submitted by a specific user.

    This endpoint returns a list of books created by the specified user,
    ordered by creation date (newest first). Requires user authentication.

    Args:
        user_uid (str): The unique identifier of the user whose books to retrieve
        token_details (dict): Access token details from the Authorization header

    Returns:
        List[BookModel]: A list of books created by the specified user

    Raises:
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view books
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    books = await book_service.get_user_books(user_uid, session)
    return books


@book_router.get(
    "/{book_uid}", response_model=BookDetailModel, dependencies=[role_checker]
)
async def get_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    Retrieve a specific book by its unique identifier.

    This endpoint returns detailed information about a book including
    its reviews and tags. Requires user authentication.

    Args:
        book_uid (str): The unique identifier of the book to retrieve
        token_details (dict): Access token details from the Authorization header

    Returns:
        BookDetailModel: Detailed book information including reviews and tags

    Raises:
        404: If the book with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view books
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    book = await book_service.get_book(book_uid, session)
    return book


@book_router.post(
    "/",
    response_model=BookModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[role_checker],
)
async def create_book(
    book_create_data: BookCreateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    Create a new book entry.

    This endpoint allows authenticated users to create a new book in the system.
    The book will be associated with the currently authenticated user.

    Args:
        book_create_data (BookCreateModel): The book data including title, author, description, etc.
        token_details (dict): Access token details from the Authorization header

    Returns:
        BookModel: The newly created book with generated UID and timestamps

    Raises:
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to create books
        500: If there is an internal server error during the creation (e.g., database issues, etc)
    """
    user_uid = token_details["user"]["user_uid"]
    new_book = await book_service.create_book(book_create_data, user_uid, session)
    return new_book


@book_router.patch("/{book_uid}", response_model=BookModel, dependencies=[role_checker])
async def update_book(
    book_uid: str,
    book_update_data: BookUpdateModel,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    Update an existing book's information.

    This endpoint allows authenticated users to update book details.
    Only the fields provided in the request body will be updated.

    Args:
        book_uid (str): The unique identifier of the book to update
        book_update_data (BookUpdateModel): The updated book data (partial update supported)
        token_details (dict): Access token details from the Authorization header

    Returns:
        BookModel: The updated book with new information

    Raises:
        404: If the book with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to update books
        500: If there is an internal server error during the update (e.g., database issues, etc)
    """
    updated_book = await book_service.update_book(book_uid, book_update_data, session)
    return updated_book


@book_router.delete(
    "/{book_uid}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[role_checker]
)
async def delete_book(
    book_uid: str,
    session: AsyncSession = Depends(get_session),
    token_details: dict = Depends(access_token_bearer),
):
    """
    Delete a book from the database.

    This endpoint allows authenticated users to permanently delete a book.
    This action cannot be undone and will also remove associated reviews and tags.

    Args:
        book_uid (str): The unique identifier of the book to delete
        token_details (dict): Access token details from the Authorization header

    Returns:
        None: Returns 204 No Content on successful deletion

    Raises:
        404: If the book with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to delete books
        500: If there is an internal server error during deletion (e.g., database issues, etc)
    """
    await book_service.delete_book(book_uid, session)
