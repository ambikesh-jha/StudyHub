from __future__ import annotations

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.models.course import TopicStatus
from app.models.material import MaterialType
from app.schemas.common import PaginatedResponse


class CourseCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str | None = None
    icon: str = "book"
    color: str = "purple"
    is_published: bool = False


class CourseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    description: str | None = None
    icon: str | None = None
    color: str | None = None
    is_published: bool | None = None


class CourseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    description: str | None = None
    icon: str
    color: str
    is_published: bool
    topic_count: int = 0
    material_count: int = 0
    is_enrolled: bool = False
    created_at: datetime
    updated_at: datetime


class CourseListResponse(PaginatedResponse):
    items: list[CourseRead]


class TopicCreate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    position: int = 0
    status: TopicStatus = TopicStatus.todo


class TopicUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=150)
    position: int | None = None
    status: TopicStatus | None = None


class TopicRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    course_id: UUID
    title: str
    position: int
    status: TopicStatus
    material_count: int = 0
    created_at: datetime
    updated_at: datetime


class TopicListResponse(PaginatedResponse):
    items: list[TopicRead]


class MaterialCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    material_type: MaterialType
    content: str | None = None


class MaterialUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    content: str | None = None
    material_type: MaterialType | None = None


class MaterialRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    topic_id: UUID
    title: str
    material_type: MaterialType
    content: str | None = None
    file_path: str | None = None
    file_name: str | None = None
    created_at: datetime
    updated_at: datetime


class MaterialListResponse(PaginatedResponse):
    items: list[MaterialRead]


class ShareLinkCreateResponse(BaseModel):
    course_id: UUID
    token: str
    share_url: str
    expires_at: datetime
    access_count: int = 0


class ShareLinkAnalytics(BaseModel):
    id: UUID
    course_id: UUID
    share_url: str
    expires_at: datetime
    access_count: int
    created_at: datetime


class ShareLinkAnalyticsResponse(BaseModel):
    items: list[ShareLinkAnalytics]
    total_access_count: int = 0


class SharedCoursePreview(BaseModel):
    course: CourseRead
    topics: list[TopicRead]
    is_enrolled: bool = False
    can_enroll: bool = False
    logged_in: bool = False
