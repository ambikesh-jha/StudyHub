from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import BackgroundTasks

from app.core.config import Settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    token_hash,
    verify_password,
)
from app.models.user import User
from app.db.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, repo: UserRepository, settings: Settings) -> None:
        self.repo = repo
        self.settings = settings

    async def register(self, *, email: str, password: str, display_name: str, background_tasks: BackgroundTasks | None = None) -> tuple[User, str, str]:
        existing_user = await self.repo.get_by_email(email)
        if existing_user:
            raise ConflictError("Email already registered")
        user = await self.repo.create_user(
            email=email,
            hashed_password=hash_password(password),
            display_name=display_name,
        )
        await self.repo.save()
        if background_tasks is not None:
            background_tasks.add_task(self._queue_verification_email, user.email)
        user = await self.repo.get_by_id(user.id)
        access_token = create_access_token(self.settings, str(user.id))
        refresh_token = create_refresh_token(self.settings, str(user.id))
        await self._store_refresh_token(user.id, refresh_token)
        await self.repo.save()
        return user, access_token, refresh_token

    async def login(self, *, email: str, password: str) -> tuple[User, str, str]:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        if not user.is_active or user.deleted_at is not None:
            raise UnauthorizedError("Account disabled")
        user = await self.repo.get_by_id(user.id)
        access_token = create_access_token(self.settings, str(user.id))
        refresh_token = create_refresh_token(self.settings, str(user.id))
        await self._store_refresh_token(user.id, refresh_token)
        await self.repo.save()
        return user, access_token, refresh_token

    async def refresh(self, refresh_token: str) -> tuple[User, str, str]:
        payload = decode_token(self.settings, refresh_token)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        user = await self.repo.get_by_id(UUID(payload["sub"]))
        stored = await self.repo.refresh_token_get(token_hash(refresh_token))
        if not stored or stored.revoked_at is not None or stored.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedError("Refresh token expired")
        await self.repo.refresh_token_revoke(stored)
        new_access = create_access_token(self.settings, str(user.id))
        new_refresh = create_refresh_token(self.settings, str(user.id))
        await self._store_refresh_token(user.id, new_refresh)
        await self.repo.save()
        return user, new_access, new_refresh

    async def logout(self, refresh_token: str) -> None:
        stored = await self.repo.refresh_token_get(token_hash(refresh_token))
        if stored:
            await self.repo.refresh_token_revoke(stored)
            await self.repo.save()

    async def _store_refresh_token(self, user_id: UUID, refresh_token: str) -> None:
        payload = decode_token(self.settings, refresh_token)
        expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        await self.repo.refresh_token_create(user_id=user_id, token_hash=token_hash(refresh_token), expires_at=expires_at)

    async def _queue_verification_email(self, email: str) -> None:
        # The real deployment would enqueue a message to an email worker;
        # logging keeps the interface async-ready without blocking the request.
        return None
