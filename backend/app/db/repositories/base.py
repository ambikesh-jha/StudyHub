from __future__ import annotations

from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import Select, and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.pagination import decode_cursor, encode_cursor
from app.models.audit import TimestampMixin


class BaseRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session


class CursorRepository(BaseRepository):
    sort_field_name = "created_at"

    @staticmethod
    def _apply_cursor(query: Select, model: type[TimestampMixin], cursor: str | None) -> Select:
        if not cursor:
            return query
        cursor_created_at, cursor_id = decode_cursor(cursor)
        created_at = getattr(model, "created_at")
        identifier = getattr(model, "id")
        return query.where(or_(created_at < cursor_created_at, and_(created_at == cursor_created_at, identifier < cursor_id)))

    @staticmethod
    def _build_next_cursor(items: Sequence[TimestampMixin]) -> str | None:
        if not items:
            return None
        last_item = items[-1]
        return encode_cursor(last_item.created_at, last_item.id)

