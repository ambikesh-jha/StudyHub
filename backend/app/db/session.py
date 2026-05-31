from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.core.config import get_settings


settings = get_settings()

engine_kwargs: dict[str, object] = {
    "pool_pre_ping": True,
}

if not settings.async_database_url.startswith("sqlite+aiosqlite"):
    engine_kwargs.update({"pool_size": 20, "max_overflow": 40})
else:
    engine_kwargs.update({"connect_args": {"check_same_thread": False}})
    if ":memory:" in settings.async_database_url:
        engine_kwargs["poolclass"] = StaticPool

engine = create_async_engine(settings.async_database_url, **engine_kwargs)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with async_session_factory() as session:
        yield session

