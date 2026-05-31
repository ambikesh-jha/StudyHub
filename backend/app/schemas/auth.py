from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

from app.schemas.common import MeResponse, UserPublic


class RegisterRequest(BaseModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8)
    display_name: str = Field(min_length=2, max_length=120)


class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserPublic | None = None


class AuthResponse(BaseModel):
    user: MeResponse
    tokens: TokenPair

