from __future__ import annotations

from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.audit import TimestampMixin


class MaterialType(str, Enum):
    note = "note"
    code = "code"
    image = "image"
    html = "html"
    file = "file"


class Material(TimestampMixin, Base):
    __tablename__ = "materials"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    topic_id: Mapped[UUID] = mapped_column(ForeignKey("topics.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    material_type: Mapped[MaterialType] = mapped_column(String(20), nullable=False)
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    topic = relationship("Topic", back_populates="materials")

