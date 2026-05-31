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
from app.schemas.course import TopicCreate, TopicListResponse, TopicRead, TopicUpdate
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["topics"])


def _service(session: AsyncSession, settings: Settings) -> CourseService:
    return CourseService(CourseRepository(session), TopicRepository(session), MaterialRepository(session), settings)


@router.get("/{course_id}/topics", response_model=TopicListResponse)
async def list_topics(
    course_id: UUID,
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> TopicListResponse:
    service = _service(session, settings)
    items, next_cursor = await service.list_topics(course_id=course_id, user=user, cursor=cursor, limit=limit)
    return TopicListResponse(items=items, next_cursor=next_cursor)


@router.post("/{course_id}/topics", response_model=TopicRead, status_code=201)
async def create_topic(
    course_id: UUID,
    payload: TopicCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> TopicRead:
    service = _service(session, settings)
    return await service.create_topic(course_id=course_id, user=user, title=payload.title, position=payload.position, status=payload.status)


@router.put("/{course_id}/topics/{topic_id}", response_model=TopicRead)
async def update_topic(
    course_id: UUID,
    topic_id: UUID,
    payload: TopicUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> TopicRead:
    service = _service(session, settings)
    return await service.update_topic(course_id=course_id, topic_id=topic_id, user=user, data=payload.model_dump(exclude_unset=True))


@router.delete("/{course_id}/topics/{topic_id}", status_code=204, response_class=Response)
async def delete_topic(
    course_id: UUID,
    topic_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    service = _service(session, settings)
    await service.delete_topic(course_id=course_id, topic_id=topic_id, user=user)
