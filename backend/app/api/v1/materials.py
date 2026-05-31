from uuid import UUID

from fastapi import Response, APIRouter, Depends, File, Form, Query, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.dependencies import get_current_user, get_optional_user
from app.db.session import get_session
from app.models.material import MaterialType
from app.models.user import User
from app.db.repositories.course_repository import CourseRepository
from app.db.repositories.material_repository import MaterialRepository
from app.db.repositories.topic_repository import TopicRepository
from app.schemas.course import MaterialCreate, MaterialListResponse, MaterialRead, MaterialUpdate
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses/topics", tags=["materials"])


def _service(session: AsyncSession, settings: Settings) -> CourseService:
    return CourseService(CourseRepository(session), TopicRepository(session), MaterialRepository(session), settings)


@router.get("/{topic_id}/materials", response_model=MaterialListResponse)
async def list_materials(
    topic_id: UUID,
    cursor: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    user: User | None = Depends(get_optional_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MaterialListResponse:
    service = _service(session, settings)
    items, next_cursor = await service.list_materials(topic_id=topic_id, user=user, cursor=cursor, limit=limit)
    return MaterialListResponse(items=items, next_cursor=next_cursor)


@router.post("/{topic_id}/materials", response_model=MaterialRead, status_code=201)
async def create_material(
    topic_id: UUID,
    payload: MaterialCreate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MaterialRead:
    service = _service(session, settings)
    return await service.create_material(topic_id=topic_id, user=user, title=payload.title, material_type=payload.material_type, content=payload.content)


@router.post("/{topic_id}/materials/upload", response_model=MaterialRead, status_code=201)
async def upload_material(
    topic_id: UUID,
    title: str = Form(...),
    material_type: MaterialType = Form(...),
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MaterialRead:
    service = _service(session, settings)
    return await service.upload_material_file(topic_id=topic_id, user=user, title=title, material_type=material_type, file=file)


@router.put("/{topic_id}/materials/{material_id}", response_model=MaterialRead)
async def update_material(
    topic_id: UUID,
    material_id: UUID,
    payload: MaterialUpdate,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> MaterialRead:
    service = _service(session, settings)
    return await service.update_material(topic_id=topic_id, material_id=material_id, user=user, data=payload.model_dump(exclude_unset=True))


@router.delete("/{topic_id}/materials/{material_id}", status_code=204, response_class=Response)
async def delete_material(
    topic_id: UUID,
    material_id: UUID,
    user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
    settings: Settings = Depends(get_settings),
) -> None:
    service = _service(session, settings)
    await service.delete_material(topic_id=topic_id, material_id=material_id, user=user)
