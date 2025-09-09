from typing import List
from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession
from src.auth.dependencies import RoleChecker
from src.books.schemas import BookDetailModel
from src.db.main import get_session
from src.errors import TagNotFound
from .schemas import TagAddModel, TagCreateModel, TagModel
from .service import TagService

tags_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@tags_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    """
    Retrieve all tags from the database.

    This endpoint returns a list of all available tags in the system,
    ordered by creation date (newest first). Requires user authentication.

    Returns:
        List[TagModel]: A list of all tags with their details

    Raises:
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view tags
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    tags = await tag_service.get_tags(session)
    return tags


@tags_router.post(
    "/",
    response_model=TagModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[user_role_checker],
)
async def add_tag(
    tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
) -> TagModel:
    """
    Create a new tag.

    This endpoint allows authenticated users to create a new tag.
    The tag name must be unique in the system.

    Args:
        tag_data (TagCreateModel): The tag data containing name and other properties

    Returns:
        TagModel: The newly created tag with generated UID and timestamps

    Raises:
        403: If a tag with the same name already exists
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to add a tag
        500: If there is an internal server error during the creation (e.g., database issues, etc)
    """
    tag_added = await tag_service.add_tag(tag_data=tag_data, session=session)
    return tag_added


@tags_router.get(
    "/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker]
)
async def get_tag_by_uid(
    tag_uid: str, session: AsyncSession = Depends(get_session)
) -> TagModel:
    """
    Retrieve a specific tag by its unique identifier.

    This endpoint allows authenticated users to get details of a specific tag
    using its unique identifier.

    Args:
        tag_uid (str): The unique identifier of the tag

    Returns:
        TagModel: The requested tag details

    Raises:
        404: If the tag with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to view tags
        500: If there is an internal server error during the retrieval (e.g., database issues, etc)
    """
    tag = await tag_service.get_tag_by_uid(tag_uid, session)
    return tag


@tags_router.post(
    "/book/{book_uid}/tags",
    response_model=BookDetailModel,
    dependencies=[user_role_checker],
)
async def add_tags_to_book(
    book_uid: str, tag_data: TagAddModel, session: AsyncSession = Depends(get_session)
) -> BookDetailModel:
    """
    Add multiple tags to a specific book.

    This endpoint allows authenticated users to add one or more tags to a book.
    If a tag doesn't exist, it will be created automatically.

    Args:
        book_uid (str): The unique identifier of the book to add tags to
        tag_data (TagAddModel): Contains a list of tags to add to the book

    Returns:
        BookDetailModel: The updated book with its associated tags

    Raises:
        404: If the book with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to add tags to books
        500: If there is an internal server error during the addition (e.g., database issues, etc)
    """
    book_with_tag = await tag_service.add_tags_to_book(
        book_uid=book_uid, tag_data=tag_data, session=session
    )
    return book_with_tag


@tags_router.put(
    "/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker]
)
async def update_tag(
    tag_uid: str,
    tag_update_data: TagCreateModel,
    session: AsyncSession = Depends(get_session),
) -> TagModel:
    """
    Update an existing tag's information.

    This endpoint allows authenticated users to update tag details.
    All fields in the request body will be updated.

    Args:
        tag_uid (str): The unique identifier of the tag to update
        tag_update_data (TagCreateModel): The updated tag data

    Returns:
        TagModel: The updated tag with new information

    Raises:
        404: If the tag with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to update tags
        500: If there is an internal server error during the update (e.g., database issues, etc)
    """
    updated_tag = await tag_service.update_tag(tag_uid, tag_update_data, session)
    return updated_tag


@tags_router.delete(
    "/{tag_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_role_checker],
)
async def delete_tag(
    tag_uid: str, session: AsyncSession = Depends(get_session)
) -> None:
    """
    Delete a tag from the database.

    This endpoint allows authenticated users to permanently delete a tag.
    This action cannot be undone.

    Args:
        tag_uid (str): The unique identifier of the tag to delete

    Returns:
        None: Returns 204 No Content on successful deletion

    Raises:
        404: If the tag with the specified UID is not found
        401: If the access token is invalid or expired / if the token is not an access token / if the user does not have permission to delete tags
        500: If there is an internal server error during the deletion (e.g., database issues, etc)
    """
    await tag_service.delete_tag(tag_uid, session)
