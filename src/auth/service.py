from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.db.models import User
from src.errors import UserNotFound, UserAlreadyExists, InvalidCredentials
from .schemas import UserCreateModel, UserLoginModel
from datetime import datetime
from .utils import hash_password, verify_password


class UserService:
    async def get_user_by_email(self, email: str, session: AsyncSession):
        statement = select(User).where(User.email == email)
        result = await session.exec(statement)
        return result.first()

    async def user_exists(self, email: str, session: AsyncSession):
        user = await self.get_user_by_email(email, session)
        return True if user is not None else False

    async def create_user(
        self, user_create_data: UserCreateModel, session: AsyncSession
    ):
        user_exists = await self.user_exists(user_create_data.email, session)
        if user_exists:
            raise UserAlreadyExists()
        user_data_dict = user_create_data.model_dump()
        new_user = User(**user_data_dict)
        new_user.password_hash = hash_password(user_data_dict["password"])
        new_user.role = "user"
        session.add(new_user)
        await session.commit()
        return new_user

    async def authenticate_user(
        self, login_data: UserLoginModel, session: AsyncSession
    ):
        user = await self.get_user_by_email(login_data.email, session)
        if not user:
            raise InvalidCredentials()
        if not verify_password(login_data.password, user.password_hash):
            raise InvalidCredentials()
        return user

    async def update_user(self, user: User, user_data: dict, session: AsyncSession):
        for k, v in user_data.items():
            setattr(user, k, v)
        await session.commit()
        return user
