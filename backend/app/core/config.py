from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Study Hub"
    environment: Literal["local", "development", "production", "test"] = "development"
    debug: bool = True
    secret_key: str = Field(min_length=32)
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    share_link_expire_days: int = 7
    database_url: str = "sqlite+aiosqlite:///./studyhub.db"
    test_database_url: str = "sqlite+aiosqlite:///:memory:"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    upload_dir: str = "uploads"
    static_url_prefix: str = "/uploads"
    log_level: str = "DEBUG"
    rate_limit_login: str = "5/minute"
    redis_url: str | None = None
    api_base_url: str = "http://localhost:8000"
    public_app_url: str = "http://localhost:5173"
    mail_from: str = "noreply@study-hub.local"

    @property
    def async_database_url(self) -> str:
        if self.database_url.startswith("sqlite://"):
            return self.database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        if self.database_url.startswith("postgresql://"):
            return self.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.database_url

    @property
    def async_test_database_url(self) -> str:
        if self.test_database_url.startswith("sqlite://"):
            return self.test_database_url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        if self.test_database_url.startswith("postgresql://"):
            return self.test_database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self.test_database_url


@lru_cache
def get_settings() -> Settings:
    return Settings()
