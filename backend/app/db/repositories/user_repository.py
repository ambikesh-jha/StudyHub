from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError, NotFoundError
from app.models.course import Enrollment
from app.models.role import Role
from app.models.token import RefreshToken
from app.models.user import ThemeMode, User, UserPreference
from app.db.repositories.base import BaseRepository


class UserRepository(BaseRepository):
    async def get_by_id(self, user_id: UUID) -> User:
        result = await self.session.execute(
            select(User).options(selectinload(User.preferences), selectinload(User.role)).where(User.id == user_id, User.deleted_at.is_(None))
        )
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundError("User not found")
        return user

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(
            select(User).options(selectinload(User.preferences), selectinload(User.role)).where(User.email == email, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def create_user(self, *, email: str, hashed_password: str, display_name: str, role_name: str = "user") -> User:
        role_result = await self.session.execute(select(Role).where(Role.name == role_name))
        role = role_result.scalar_one_or_none()
        if role is None:
            raise NotFoundError("Role not found")
        if await self.get_by_email(email):
            raise ConflictError("Email already registered")
        user = User(email=email.lower(), hashed_password=hashed_password, display_name=display_name, role_id=role.id)
        self.session.add(user)
        await self.session.flush()
        preference = UserPreference(user_id=user.id, theme_mode=ThemeMode.system.value)
        self.session.add(preference)
        return user

    async def save(self) -> None:
        await self.session.commit()

    async def update_profile(self, user: User, *, display_name: str | None = None, email: str | None = None, bio: str | None = None) -> User:
        if email and email.lower() != user.email and await self.get_by_email(email):
            raise ConflictError("Email already registered")
        if display_name is not None:
            user.display_name = display_name
        if email is not None:
            user.email = email.lower()
            user.is_verified = False
        if bio is not None:
            user.bio = bio
        await self.session.flush()
        return user

    async def update_avatar(self, user: User, avatar_url: str) -> User:
        user.avatar_url = avatar_url
        await self.session.flush()
        return user

    async def change_password(self, user: User, hashed_password: str) -> None:
        user.hashed_password = hashed_password
        await self.session.flush()

    async def get_preferences(self, user_id: UUID) -> UserPreference:
        result = await self.session.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        preference = result.scalar_one_or_none()
        if not preference:
            preference = UserPreference(user_id=user_id)
            self.session.add(preference)
            await self.session.flush()
        return preference

    async def update_preferences(self, user_id: UUID, *, theme_mode: str | None = None, prefers_reduced_motion: bool | None = None) -> UserPreference:
        preference = await self.get_preferences(user_id)
        if theme_mode is not None:
            preference.theme_mode = theme_mode
        if prefers_reduced_motion is not None:
            preference.prefers_reduced_motion = prefers_reduced_motion
        await self.session.flush()
        return preference

    async def deactivate_user(self, user: User) -> None:
        user.is_active = False
        user.deleted_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def get_role(self, name: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def refresh_token_create(self, *, user_id: UUID, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()
        return token

    async def refresh_token_get(self, token_hash: str) -> RefreshToken | None:
        result = await self.session.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
        return result.scalar_one_or_none()

    async def refresh_token_revoke(self, token: RefreshToken) -> None:
        token.revoked_at = datetime.now(timezone.utc)
        await self.session.flush()

    async def count_enrollments(self, user_id: UUID) -> tuple[int, int, int]:
        enrolled_result = await self.session.execute(select(Enrollment).where(Enrollment.user_id == user_id))
        enrollments = enrolled_result.scalars().all()
        completed = sum(1 for enrollment in enrollments if enrollment.completed)
        streak = max((enrollment.streak_days for enrollment in enrollments), default=0)
        return len(enrollments), completed, streak

