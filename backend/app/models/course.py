from __future__ import annotations

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.audit import TimestampMixin


class TopicStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    done = "done"


class Course(TimestampMixin, Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(50), default="book", nullable=False)
    color: Mapped[str] = mapped_column(String(30), default="purple", nullable=False)
    is_published: Mapped[bool] = mapped_column(default=False, nullable=False)

    owner = relationship("User", back_populates="owned_courses")
    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="course", cascade="all, delete-orphan")


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    position: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    status: Mapped[TopicStatus] = mapped_column(
        SQLEnum(TopicStatus, name="topic_status", create_type=False, native_enum=True),
        default=TopicStatus.todo,
        nullable=False,
    )
    course = relationship("Course", back_populates="topics")
    materials = relationship("Material", back_populates="topic", cascade="all, delete-orphan")

    __table_args__ = (UniqueConstraint("course_id", "position", name="uq_topic_position_per_course"),)


class Enrollment(TimestampMixin, Base):
    __tablename__ = "enrollments"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), nullable=False)
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)
    streak_days: Mapped[int] = mapped_column(default=0, nullable=False)

    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_user_course_enrollment"),)


class ShareLink(TimestampMixin, Base):
    __tablename__ = "share_links"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(ForeignKey("courses.id"), nullable=False)
    token: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    course = relationship("Course", back_populates="share_links")
