from __future__ import annotations

import base64
from datetime import datetime, timezone
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None


class CursorState(BaseModel):
    sort_key: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    id: UUID


def encode_cursor(sort_key: datetime, item_id: UUID) -> str:
    payload = f"{sort_key.isoformat()}|{item_id}"
    return base64.urlsafe_b64encode(payload.encode("utf-8")).decode("utf-8")


def decode_cursor(cursor: str) -> tuple[datetime, UUID]:
    raw = base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8")
    sort_key_value, item_id_value = raw.split("|", 1)
    return datetime.fromisoformat(sort_key_value), UUID(item_id_value)

