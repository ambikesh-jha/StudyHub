from __future__ import annotations

import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("SECRET_KEY", "study-hub-test-secret-key-change-me-1234")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("PUBLIC_APP_URL", "http://localhost:5173")
os.environ.setdefault("API_BASE_URL", "http://localhost:8000")

import app.models  # noqa: F401
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.db.base import Base
from app.db.session import async_session_factory, engine, get_session
from app.main import app
from app.models.role import Role

get_settings.cache_clear()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def prepare_database() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with async_session_factory() as session:
        session.add_all([Role(name="admin"), Role(name="user")])
        await session.commit()


@pytest_asyncio.fixture()
async def session() -> AsyncSession:
    async with async_session_factory() as test_session:
        yield test_session


@pytest_asyncio.fixture()
async def client(session: AsyncSession) -> AsyncClient:
    async def override_session():
        yield session

    app.dependency_overrides[get_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as test_client:
        yield test_client
    app.dependency_overrides.clear()

