from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.db_conf import settings

engine = create_async_engine(settings.asyncpg_url, echo=True)
AsyncSessionMaker = async_sessionmaker(
    engine,
    autoflush=False,
    expire_on_commit=False
)


async def get_db_session() -> AsyncGenerator:
    async with AsyncSessionMaker() as session:
        yield session
