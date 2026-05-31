from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4

import bcrypt
from jose import JWTError, jwt

from app.core.config import Settings


def _password_bytes(password: str) -> bytes:
    # bcrypt 5 rejects inputs over 72 bytes. Pre-hashing keeps all password
    # entropy while giving bcrypt a fixed-length input.
    return sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(_password_bytes(password), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(_password_bytes(password), hashed_password.encode("utf-8"))


def _encode_datetime(value: datetime) -> int:
    return int(value.replace(tzinfo=timezone.utc).timestamp())


def create_token(
    *,
    settings: Settings,
    subject: str,
    expires_delta: timedelta,
    token_type: str,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": _encode_datetime(now),
        "exp": _encode_datetime(now + expires_delta),
        "jti": str(uuid4()),
        "type": token_type,
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def create_access_token(settings: Settings, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    return create_token(
        settings=settings,
        subject=subject,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
        token_type="access",
        extra_claims=extra_claims,
    )


def create_refresh_token(settings: Settings, subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    return create_token(
        settings=settings,
        subject=subject,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
        token_type="refresh",
        extra_claims=extra_claims,
    )


def decode_token(settings: Settings, token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])


def token_hash(token: str) -> str:
    return sha256(token.encode("utf-8")).hexdigest()


def uuid_from_subject(subject: str) -> UUID:
    return UUID(subject)
