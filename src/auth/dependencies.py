from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException, status, Depends
from fastapi.security.http import HTTPAuthorizationCredentials
from src.auth.utils import decode_token
from src.db.redis import token_in_blacklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.service import UserService
from typing import List
from src.errors import (
    InvalidToken,
    RefreshTokenRequired,
    AccessTokenRequired,
    InsufficientPermission,
    AccountNotVerified,
    UserNotFound,
)

user_service = UserService()


class TokenBearer(HTTPBearer):

    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        creds = await super().__call__(request)
        # print(creds.scheme)
        # print(creds.credentials)
        token = creds.credentials
        token_data = decode_token(token)
        if not token_data:
            raise InvalidToken()
        if await token_in_blacklist(token_data["jti"]):
            raise InvalidToken()
        self.verify_token_data(token_data)
        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return True if token_data else False

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Please override this method in subclasses.")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    user_email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(user_email, session)
    if user:
        return user
    raise UserNotFound()


class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(self, current_user=Depends(get_current_user)) -> bool:
        if not current_user.is_verified:
            raise AccountNotVerified()
        if current_user.role in self.allowed_roles:
            return True
        raise InsufficientPermission()
