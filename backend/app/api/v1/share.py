from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_current_user, get_optional_user
from app.db.session import get_session
from app.models.user import User
from app.db.repositories.course_repository import CourseRepository
from app.db.repositories.material_repository import MaterialRepository
from app.db.repositories.topic_repository import TopicRepository
from app.schemas.course import ShareLinkAnalyticsResponse, ShareLinkCreateResponse, SharedCoursePreview
from app.services.course_service import CourseService

router = APIRouter(tags=["share"])


def _service(session: AsyncSession, settings: Settings) -> CourseService:
    return CourseService(CourseRepository(session), TopicRepository(session), MaterialRepository(session), settings)


@router.get("/courses/{course_id}/share-link", response_model=ShareLinkCreateResponse)
async def create_share_link(
    course_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ShareLinkCreateResponse:
    service = _service(session, settings)
    return await service.create_share_link(course_id=course_id, user=user)


@router.get("/courses/{course_id}/share-links", response_model=ShareLinkAnalyticsResponse)
async def list_share_links(
    course_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> ShareLinkAnalyticsResponse:
    service = _service(session, settings)
    return await service.list_share_links(course_id=course_id, user=user)


@router.get("/shared/course/{token}", response_model=SharedCoursePreview)
async def preview_shared_course(
    token: str,
    user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> SharedCoursePreview:
    service = _service(session, settings)
    return await service.resolve_share_link(token, user)
