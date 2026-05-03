from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def build_engine(database_url: str):
    connect_args = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_async_engine(database_url, echo=False, connect_args=connect_args)


def build_session_factory(engine):
    return async_sessionmaker(engine, expire_on_commit=False)


# Module-level singletons; overridden in tests via dependency injection
from app.config import get_settings as _get_settings

_settings = _get_settings()
engine = build_engine(_settings.database_url)
AsyncSessionLocal = build_session_factory(engine)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
