from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class APIMessage(BaseModel):
    message: str


class IDModel(BaseModel):
    id: UUID


class TimestampedModel(BaseModel):
    created_at: datetime
    updated_at: datetime


class PaginatedResponse(BaseModel):
    next_cursor: str | None = None


class RoleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str


class UserPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    display_name: str
    bio: str | None = None
    avatar_url: str | None = None
    is_verified: bool
    role: RoleRead | None = None


class MeResponse(UserPublic):
    preferences: "PreferenceRead | None" = None


class PreferenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    theme_mode: str
    prefers_reduced_motion: bool = False


MeResponse.model_rebuild()
