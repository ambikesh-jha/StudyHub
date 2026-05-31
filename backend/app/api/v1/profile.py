from fastapi import Response, APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_current_user
from app.db.session import get_session
from app.models.user import User
from app.db.repositories.course_repository import CourseRepository
from app.db.repositories.material_repository import MaterialRepository
from app.db.repositories.topic_repository import TopicRepository
from app.db.repositories.user_repository import UserRepository
from app.schemas.preferences import PreferenceResponse, PreferenceUpdate
from app.schemas.profile import AccountStats, ChangePasswordRequest, ProfileResponse, ProfileUpdate
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/users", tags=["users"])


def _service(session: AsyncSession, settings: Settings) -> ProfileService:
    return ProfileService(UserRepository(session), CourseRepository(session), settings)


@router.get("/me", response_model=ProfileResponse)
async def get_me(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ProfileResponse:
    service = _service(session, settings)
    return await service.get_profile(user)


@router.patch("/me", response_model=ProfileResponse)
async def update_me(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ProfileResponse:
    service = _service(session, settings)
    return await service.update_profile(user, display_name=payload.display_name, email=payload.email, bio=payload.bio)


@router.post("/me/avatar", response_model=dict)
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> dict:
    service = _service(session, settings)
    avatar_url = await service.update_avatar(user, file)
    return {"avatar_url": avatar_url}


@router.post("/me/change-password", status_code=204, response_class=Response)
async def change_password(
    payload: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    service = _service(session, settings)
    await service.change_password(
        user,
        current_password=payload.current_password,
        new_password=payload.new_password,
        confirm_password=payload.confirm_password,
    )


@router.get("/me/preferences", response_model=PreferenceResponse)
async def get_preferences(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> PreferenceResponse:
    service = _service(session, settings)
    return await service.get_preferences(user)


@router.patch("/me/preferences", response_model=PreferenceResponse)
async def update_preferences(
    payload: PreferenceUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> PreferenceResponse:
    service = _service(session, settings)
    return await service.update_preferences(user, theme_mode=payload.theme_mode, prefers_reduced_motion=payload.prefers_reduced_motion)


@router.get("/me/stats", response_model=AccountStats)
async def get_stats(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> AccountStats:
    service = _service(session, settings)
    return await service.get_stats(user)


@router.delete("/me", status_code=204, response_class=Response)
async def delete_account(
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    service = _service(session, settings)
    await service.delete_account(user)

