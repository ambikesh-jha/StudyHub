from uuid import UUID

from fastapi import Response, APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_current_user, get_optional_user
from app.db.session import get_session
from app.models.user import User
from app.db.repositories.course_repository import CourseRepository
from app.db.repositories.material_repository import MaterialRepository
from app.db.repositories.topic_repository import TopicRepository
from app.schemas.course import (
    CourseCreate,
    CourseListResponse,
    CourseRead,
    CourseUpdate,
)
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


def _service(session: AsyncSession, settings: Settings) -> CourseService:
    return CourseService(CourseRepository(session), TopicRepository(session), MaterialRepository(session), settings)


@router.get("", response_model=CourseListResponse)
async def list_courses(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CourseListResponse:
    service = _service(session, settings)
    items, next_cursor = await service.list_courses(user=user, cursor=cursor, limit=limit)
    return CourseListResponse(items=items, next_cursor=next_cursor)


@router.post("", response_model=CourseRead, status_code=201)
async def create_course(
    payload: CourseCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CourseRead:
    service = _service(session, settings)
    return await service.create_course(
        owner=user,
        title=payload.title,
        description=payload.description,
        icon=payload.icon,
        color=payload.color,
        is_published=payload.is_published,
    )


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: UUID,
    user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CourseRead:
    service = _service(session, settings)
    return await service.get_course(course_id=course_id, user=user)


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: UUID,
    payload: CourseUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> CourseRead:
    service = _service(session, settings)
    return await service.update_course(course_id=course_id, user=user, data=payload.model_dump(exclude_unset=True))


@router.delete("/{course_id}", status_code=204, response_class=Response)
async def delete_course(
    course_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    service = _service(session, settings)
    await service.delete_course(course_id=course_id, user=user)


@router.post("/{course_id}/enroll", status_code=204, response_class=Response)
async def enroll_course(
    course_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    service = _service(session, settings)
    await service.enroll(course_id=course_id, user=user)
