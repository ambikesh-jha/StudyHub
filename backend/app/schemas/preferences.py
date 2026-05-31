from __future__ import annotations

from pydantic import BaseModel

from app.schemas.common import PreferenceRead


class PreferenceUpdate(BaseModel):
    theme_mode: str | None = None
    prefers_reduced_motion: bool | None = None


class PreferenceResponse(PreferenceRead):
    pass

