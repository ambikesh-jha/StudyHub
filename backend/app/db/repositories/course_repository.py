from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.core.pagination import CursorPage
from app.models.course import Course, Enrollment, ShareLink, Topic
from app.models.material import Material
from app.db.repositories.base import BaseRepository, CursorRepository


class CourseRepository(CursorRepository):
    async def list_courses(
        self,
        *,
        owner_id: UUID | None = None,
        cursor: str | None = None,
        limit: int = 20,
        published_only: bool = False,
    ) -> tuple[list[Course], str | None]:
        query = (
            select(Course)
            .options(selectinload(Course.topics).selectinload(Topic.materials), selectinload(Course.enrollments))
            .order_by(Course.created_at.desc(), Course.id.desc())
            .limit(limit + 1)
        )
        if owner_id is not None:
            query = query.where(Course.owner_id == owner_id)
        if published_only:
            query = query.where(Course.is_published.is_(True))
        if cursor:
            query = self._apply_cursor(query, Course, cursor)
        result = await self.session.execute(query)
        items = list(result.scalars().unique().all())
        next_cursor = None
        if len(items) > limit:
            next_cursor = self._build_next_cursor(items[:limit])
            items = items[:limit]
        return items, next_cursor

    async def get_course(self, course_id: UUID) -> Course:
        result = await self.session.execute(
            select(Course)
            .options(selectinload(Course.topics).selectinload(Topic.materials), selectinload(Course.enrollments))
            .where(Course.id == course_id)
        )
        course = result.scalar_one_or_none()
        if not course:
            raise NotFoundError("Course not found")
        return course

    async def create_course(self, *, owner_id: UUID, title: str, description: str | None, icon: str, color: str, is_published: bool) -> Course:
        course = Course(owner_id=owner_id, title=title, description=description, icon=icon, color=color, is_published=is_published)
        self.session.add(course)
        await self.session.flush()
        return course

    async def delete_course(self, course: Course) -> None:
        await self.session.delete(course)

    async def get_enrollment(self, *, user_id: UUID, course_id: UUID) -> Enrollment | None:
        result = await self.session.execute(select(Enrollment).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id))
        return result.scalar_one_or_none()

    async def enroll_user(self, *, user_id: UUID, course_id: UUID) -> Enrollment:
        existing = await self.get_enrollment(user_id=user_id, course_id=course_id)
        if existing:
            return existing
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        self.session.add(enrollment)
        await self.session.flush()
        return enrollment

    async def get_share_link(self, token: str) -> ShareLink | None:
        result = await self.session.execute(select(ShareLink).where(ShareLink.token == token))
        return result.scalar_one_or_none()

    async def create_share_link(self, *, course_id: UUID, token: str, created_by: UUID, expires_at) -> ShareLink:
        share_link = ShareLink(course_id=course_id, token=token, created_by=created_by, expires_at=expires_at)
        self.session.add(share_link)
        await self.session.flush()
        return share_link

    async def get_latest_active_share_link(self, *, course_id: UUID) -> ShareLink | None:
        result = await self.session.execute(
            select(ShareLink)
            .where(ShareLink.course_id == course_id, ShareLink.expires_at > func.now())
            .order_by(ShareLink.created_at.desc(), ShareLink.id.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def list_share_links(self, *, course_id: UUID) -> list[ShareLink]:
        result = await self.session.execute(
            select(ShareLink)
            .where(ShareLink.course_id == course_id)
            .order_by(ShareLink.created_at.desc(), ShareLink.id.desc())
        )
        return list(result.scalars().all())

    async def increment_share_access(self, share_link: ShareLink) -> None:
        share_link.access_count += 1
        await self.session.flush()

    async def count_materials_for_course(self, course: Course) -> int:
        return sum(len(topic.materials) for topic in course.topics)

    async def count_owned_content(self, *, owner_id: UUID) -> tuple[int, int, int]:
        courses_result = await self.session.execute(select(func.count(Course.id)).where(Course.owner_id == owner_id))
        topics_result = await self.session.execute(
            select(func.count(Topic.id))
            .join(Course, Topic.course_id == Course.id)
            .where(Course.owner_id == owner_id)
        )
        materials_result = await self.session.execute(
            select(func.count(Material.id))
            .join(Topic, Material.topic_id == Topic.id)
            .join(Course, Topic.course_id == Course.id)
            .where(Course.owner_id == owner_id)
        )
        return (
            int(courses_result.scalar_one()),
            int(topics_result.scalar_one()),
            int(materials_result.scalar_one()),
        )
