from sqlmodel import SQLModel, create_engine, text
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import sessionmaker

from src.config import Config

async_engine = AsyncEngine(create_engine(url=Config.DATABASE_URL, echo=False))


async def init_db():
    async with async_engine.begin() as conn:
        # statement = text("SELECT 'HELLO';")
        # result = await conn.execute(statement)
        # print(result.all())
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:  # type: ignore
    Session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with Session() as session:
        yield session
