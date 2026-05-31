from __future__ import annotations

from collections.abc import Callable
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.exceptions import UnauthorizedError
from app.core.security import decode_token
from app.db.session import get_session
from app.models.user import User
from app.db.repositories.user_repository import UserRepository

bearer_scheme = HTTPBearer(auto_error=False)


async def get_db(session: Annotated[AsyncSession, Depends(get_session)]) -> AsyncSession:
    return session


def get_settings_dependency() -> Settings:
    return get_settings()


async def get_current_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings_dependency)],
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise UnauthorizedError("Missing access token")
    try:
        payload = decode_token(settings, credentials.credentials)
    except (JWTError, ValueError, KeyError) as exc:
        raise UnauthorizedError("Invalid access token") from exc
    if payload.get("type") != "access":
        raise UnauthorizedError("Invalid access token")
    repo = UserRepository(session)
    user = await repo.get_by_id(UUID(payload["sub"]))
    if not user.is_active or user.deleted_at is not None:
        raise UnauthorizedError("Account disabled")
    request.state.user_id = str(user.id)
    return user


async def get_optional_user(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: Annotated[AsyncSession, Depends(get_session)],
    settings: Annotated[Settings, Depends(get_settings_dependency)],
) -> User | None:
    if credentials is None:
        return None
    try:
        return await get_current_user(request, credentials, session, settings)
    except Exception:
        return None


def require_roles(*roles: str) -> Callable[[User], User]:
    async def dependency(user: Annotated[User, Depends(get_current_user)]) -> User:
        if user.role.name not in roles:
            raise UnauthorizedError("Insufficient permissions")
        return user

    return dependency
