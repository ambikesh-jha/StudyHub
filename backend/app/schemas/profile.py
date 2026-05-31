from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.common import PreferenceRead, UserPublic


class ProfileUpdate(BaseModel):
    display_name: str | None = Field(default=None, min_length=2, max_length=120)
    email: EmailStr | None = None
    bio: str | None = Field(default=None, max_length=1000)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8)
    confirm_password: str = Field(min_length=8)


class AvatarUploadResponse(BaseModel):
    avatar_url: str


class AccountStats(BaseModel):
    courses_enrolled: int
    courses_completed: int
    streak_days: int
    owned_courses: int = 0
    owned_topics: int = 0
    owned_materials: int = 0


class ProfileResponse(UserPublic):
    preferences: PreferenceRead | None = None
    stats: AccountStats | None = None
