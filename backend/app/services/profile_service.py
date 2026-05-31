from __future__ import annotations

from uuid import UUID

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import ConflictError, UnauthorizedError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.db.repositories.course_repository import CourseRepository
from app.db.repositories.user_repository import UserRepository
from app.services.storage_service import StorageService


class ProfileService:
    def __init__(self, user_repo: UserRepository, course_repo: CourseRepository, settings: Settings) -> None:
        self.user_repo = user_repo
        self.course_repo = course_repo
        self.settings = settings
        self.storage = StorageService(settings.upload_dir)

    async def get_profile(self, user: User) -> dict:
        preferences = await self.user_repo.get_preferences(user.id)
        enrolled, completed, streak = await self.user_repo.count_enrollments(user.id)
        owned_courses, owned_topics, owned_materials = await self.course_repo.count_owned_content(owner_id=user.id)
        return {
            "id": user.id,
            "email": user.email,
            "display_name": user.display_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "is_verified": user.is_verified,
            "role": user.role,
            "preferences": preferences,
            "stats": {
                "courses_enrolled": enrolled,
                "courses_completed": completed,
                "streak_days": streak,
                "owned_courses": owned_courses,
                "owned_topics": owned_topics,
                "owned_materials": owned_materials,
            },
        }

    async def update_profile(self, user: User, *, display_name: str | None, email: str | None, bio: str | None) -> dict:
        await self.user_repo.update_profile(user, display_name=display_name, email=email, bio=bio)
        await self.user_repo.save()
        return await self.get_profile(user)

    async def update_avatar(self, user: User, file: UploadFile) -> str:
        _, file_name = await self.storage.save_avatar(file)
        await self.user_repo.update_avatar(user, f"{self.settings.api_base_url.rstrip('/')}{self.settings.static_url_prefix}/{file_name}")
        await self.user_repo.save()
        return user.avatar_url or ""

    async def change_password(self, user: User, *, current_password: str, new_password: str, confirm_password: str) -> None:
        if new_password != confirm_password:
            raise ConflictError("Password confirmation does not match")
        if not verify_password(current_password, user.hashed_password):
            raise UnauthorizedError("Current password is incorrect")
        await self.user_repo.change_password(user, hash_password(new_password))
        await self.user_repo.save()

    async def get_preferences(self, user: User) -> dict:
        preference = await self.user_repo.get_preferences(user.id)
        return {"theme_mode": preference.theme_mode, "prefers_reduced_motion": preference.prefers_reduced_motion}

    async def update_preferences(self, user: User, *, theme_mode: str | None, prefers_reduced_motion: bool | None) -> dict:
        preference = await self.user_repo.update_preferences(user.id, theme_mode=theme_mode, prefers_reduced_motion=prefers_reduced_motion)
        await self.user_repo.save()
        return {"theme_mode": preference.theme_mode, "prefers_reduced_motion": preference.prefers_reduced_motion}

    async def delete_account(self, user: User) -> None:
        await self.user_repo.deactivate_user(user)
        await self.user_repo.save()

    async def get_stats(self, user: User) -> dict:
        enrolled, completed, streak = await self.user_repo.count_enrollments(user.id)
        owned_courses, owned_topics, owned_materials = await self.course_repo.count_owned_content(owner_id=user.id)
        return {
            "courses_enrolled": enrolled,
            "courses_completed": completed,
            "streak_days": streak,
            "owned_courses": owned_courses,
            "owned_topics": owned_topics,
            "owned_materials": owned_materials,
        }
