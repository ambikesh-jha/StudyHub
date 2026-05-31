from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.repositories.user_repository import UserRepository
from app.db.session import get_session
from app.middleware.rate_limit import create_limiter
from app.schemas.auth import (
    AuthResponse,
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
)
from app.schemas.common import MeResponse, UserPublic
from app.services.auth_service import AuthService

router = APIRouter(prefix="", tags=["auth"])
limiter = create_limiter(get_settings())


def _auth_service(session: AsyncSession, settings: Settings) -> AuthService:
    return AuthService(UserRepository(session), settings)


@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    service = _auth_service(session, settings)
    user, access_token, refresh_token = await service.register(
        email=payload.email,
        password=payload.password.get_secret_value(),
        display_name=payload.display_name,
        background_tasks=background_tasks,
    )
    return AuthResponse(
        user=MeResponse.model_validate(user, from_attributes=True),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserPublic.model_validate(user, from_attributes=True),
        ),
    )


@router.post("/login", response_model=AuthResponse)
@limiter.limit(get_settings().rate_limit_login)
async def login(
    request: Request,
    payload: LoginRequest,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    service = _auth_service(session, settings)
    user, access_token, refresh_token = await service.login(
        email=payload.email,
        password=payload.password.get_secret_value(),
    )
    return AuthResponse(
        user=MeResponse.model_validate(user, from_attributes=True),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserPublic.model_validate(user, from_attributes=True),
        ),
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    payload: RefreshRequest,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AuthResponse:
    service = _auth_service(session, settings)
    user, access_token, refresh_token = await service.refresh(payload.refresh_token)
    return AuthResponse(
        user=MeResponse.model_validate(user, from_attributes=True),
        tokens=TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserPublic.model_validate(user, from_attributes=True),
        ),
    )


@router.post("/logout")
async def logout(
    payload: LogoutRequest,
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict[str, str]:
    service = _auth_service(session, settings)
    await service.logout(payload.refresh_token)
    return {"message": "Logged out"}
