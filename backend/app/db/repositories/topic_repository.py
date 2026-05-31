from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundError
from app.models.course import Course, Topic
from app.db.repositories.base import CursorRepository


class TopicRepository(CursorRepository):
    async def list_topics(self, *, course_id: UUID, cursor: str | None = None, limit: int = 20) -> tuple[list[Topic], str | None]:
        query = (
            select(Topic)
            .options(selectinload(Topic.materials))
            .where(Topic.course_id == course_id)
            .order_by(Topic.position.asc(), Topic.created_at.desc(), Topic.id.desc())
            .limit(limit + 1)
        )
        if cursor:
            query = self._apply_cursor(query, Topic, cursor)
        result = await self.session.execute(query)
        topics = list(result.scalars().unique().all())
        next_cursor = None
        if len(topics) > limit:
            next_cursor = self._build_next_cursor(topics[:limit])
            topics = topics[:limit]
        return topics, next_cursor

    async def get_topic(self, topic_id: UUID, course_id: UUID | None = None) -> Topic:
        query = select(Topic).options(selectinload(Topic.materials)).where(Topic.id == topic_id)
        if course_id is not None:
            query = query.where(Topic.course_id == course_id)
        result = await self.session.execute(query)
        topic = result.scalar_one_or_none()
        if not topic:
            raise NotFoundError("Topic not found")
        return topic

    async def create_topic(self, *, course_id: UUID, title: str, position: int, status) -> Topic:
        existing_position = await self.session.execute(
            select(Topic.id).where(Topic.course_id == course_id, Topic.position == position).limit(1)
        )
        if existing_position.scalar_one_or_none() is not None:
            max_position = await self.session.execute(select(func.max(Topic.position)).where(Topic.course_id == course_id))
            position = (max_position.scalar_one_or_none() or -1) + 1
        topic = Topic(course_id=course_id, title=title, position=position, status=status)
        self.session.add(topic)
        await self.session.flush()
        return topic

    async def delete_topic(self, topic: Topic) -> None:
        await self.session.delete(topic)
