from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import UploadFile

from app.core.config import Settings
from app.core.exceptions import GoneError, NotFoundError, UnauthorizedError
from app.core.security import create_token, decode_token
from app.models.course import Course, Topic
from app.models.material import Material
from app.models.user import User
from app.db.repositories.course_repository import CourseRepository
from app.db.repositories.material_repository import MaterialRepository
from app.db.repositories.topic_repository import TopicRepository
from app.services.storage_service import StorageService


class CourseService:
    def __init__(
        self,
        course_repo: CourseRepository,
        topic_repo: TopicRepository,
        material_repo: MaterialRepository,
        settings: Settings,
    ) -> None:
        self.course_repo = course_repo
        self.topic_repo = topic_repo
        self.material_repo = material_repo
        self.settings = settings
        self.storage = StorageService(settings.upload_dir)

    async def list_courses(
        self,
        *,
        user: User | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict], str | None]:
        owner_id = None
        published_only = user is None
        if user is not None and user.role.name != "admin":
            owner_id = user.id
        items, next_cursor = await self.course_repo.list_courses(
            owner_id=owner_id,
            cursor=cursor,
            limit=limit,
            published_only=published_only,
        )
        payload: list[dict] = []
        for course in items:
            payload.append(await self._serialize_course(course, user=user))
        return payload, next_cursor

    async def create_course(
        self,
        *,
        owner: User,
        title: str,
        description: str | None,
        icon: str,
        color: str,
        is_published: bool,
    ) -> dict:
        course = await self.course_repo.create_course(
            owner_id=owner.id,
            title=title,
            description=description,
            icon=icon,
            color=color,
            is_published=is_published,
        )
        await self.course_repo.session.commit()
        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "icon": course.icon,
            "color": course.color,
            "is_published": course.is_published,
            "topic_count": 0,
            "material_count": 0,
            "is_enrolled": False,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
        }

    async def get_course(self, *, course_id: UUID, user: User | None) -> dict:
        course = await self.course_repo.get_course(course_id)
        await self._ensure_can_read_course(course, user)
        return await self._serialize_course(course, user=user)

    async def update_course(self, *, course_id: UUID, user: User, data: dict) -> dict:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot edit this course")
        for key, value in data.items():
            setattr(course, key, value)
        await self.course_repo.session.commit()
        return await self._serialize_course(course, user=user)

    async def delete_course(self, *, course_id: UUID, user: User) -> None:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot delete this course")
        await self.course_repo.delete_course(course)
        await self.course_repo.session.commit()

    async def list_topics(
        self,
        *,
        course_id: UUID,
        user: User | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict], str | None]:
        course = await self.course_repo.get_course(course_id)
        await self._ensure_can_read_course(course, user)
        topics, next_cursor = await self.topic_repo.list_topics(
            course_id=course_id,
            cursor=cursor,
            limit=limit,
        )
        payload = [await self._serialize_topic(topic) for topic in topics]
        return payload, next_cursor

    async def create_topic(
        self,
        *,
        course_id: UUID,
        user: User,
        title: str,
        position: int,
        status,
    ) -> dict:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot edit this course")
        topic = await self.topic_repo.create_topic(
            course_id=course_id,
            title=title,
            position=position,
            status=status,
        )
        await self.topic_repo.session.commit()
        return {
            "id": topic.id,
            "course_id": topic.course_id,
            "title": topic.title,
            "position": topic.position,
            "status": topic.status,
            "material_count": 0,
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
        }

    async def update_topic(
        self,
        *,
        course_id: UUID,
        topic_id: UUID,
        user: User,
        data: dict,
    ) -> dict:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot edit this course")
        topic = await self.topic_repo.get_topic(topic_id, course_id=course_id)
        for key, value in data.items():
            setattr(topic, key, value)
        await self.topic_repo.session.commit()
        return await self._serialize_topic(topic)

    async def delete_topic(self, *, course_id: UUID, topic_id: UUID, user: User) -> None:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot delete this topic")
        topic = await self.topic_repo.get_topic(topic_id, course_id=course_id)
        await self.topic_repo.delete_topic(topic)
        await self.topic_repo.session.commit()

    async def list_materials(
        self,
        *,
        topic_id: UUID,
        user: User | None,
        cursor: str | None,
        limit: int,
    ) -> tuple[list[dict], str | None]:
        topic = await self.topic_repo.get_topic(topic_id)
        course = await self.course_repo.get_course(topic.course_id)
        await self._ensure_can_read_course(course, user)
        materials, next_cursor = await self.material_repo.list_materials(
            topic_id=topic_id,
            cursor=cursor,
            limit=limit,
        )
        return [await self._serialize_material(material) for material in materials], next_cursor

    async def create_material(
        self,
        *,
        topic_id: UUID,
        user: User,
        title: str,
        material_type,
        content: str | None,
    ) -> dict:
        topic = await self.topic_repo.get_topic(topic_id)
        course = await self.course_repo.get_course(topic.course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot edit this course")
        material = await self.material_repo.create_material(
            topic_id=topic_id,
            title=title,
            material_type=material_type,
            content=content,
        )
        await self.material_repo.session.commit()
        return await self._serialize_material(material)

    async def upload_material_file(
        self,
        *,
        topic_id: UUID,
        user: User,
        title: str,
        material_type,
        file: UploadFile,
    ) -> dict:
        topic = await self.topic_repo.get_topic(topic_id)
        course = await self.course_repo.get_course(topic.course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot edit this course")
        file_path, file_name = await self.storage.save_upload(file, prefix="material")
        material = await self.material_repo.create_material(
            topic_id=topic_id,
            title=title,
            material_type=material_type,
            file_path=file_path,
            file_name=file_name,
        )
        await self.material_repo.session.commit()
        return await self._serialize_material(material)

    async def update_material(
        self,
        *,
        topic_id: UUID,
        material_id: UUID,
        user: User,
        data: dict,
    ) -> dict:
        topic = await self.topic_repo.get_topic(topic_id)
        course = await self.course_repo.get_course(topic.course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot edit this course")
        material = await self.material_repo.get_material(material_id, topic_id=topic_id)
        for key, value in data.items():
            setattr(material, key, value)
        await self.material_repo.session.commit()
        return await self._serialize_material(material)

    async def delete_material(self, *, topic_id: UUID, material_id: UUID, user: User) -> None:
        topic = await self.topic_repo.get_topic(topic_id)
        course = await self.course_repo.get_course(topic.course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot delete this material")
        material = await self.material_repo.get_material(material_id, topic_id=topic_id)
        await self.material_repo.delete_material(material)
        await self.material_repo.session.commit()

    async def enroll(self, *, course_id: UUID, user: User) -> None:
        await self.course_repo.get_course(course_id)
        await self.course_repo.enroll_user(user_id=user.id, course_id=course_id)
        await self.course_repo.session.commit()

    async def create_share_link(self, *, course_id: UUID, user: User) -> dict:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot share this course")
        existing = await self.course_repo.get_latest_active_share_link(course_id=course_id)
        if existing is not None:
            return {
                "course_id": course_id,
                "token": existing.token,
                "share_url": f"{self.settings.public_app_url}/shared/course/{existing.token}",
                "expires_at": existing.expires_at,
                "access_count": existing.access_count,
            }
        expires_delta = timedelta(days=self.settings.share_link_expire_days)
        expires_at = datetime.now(timezone.utc) + expires_delta
        token = create_token(
            settings=self.settings,
            subject=str(course_id),
            expires_delta=expires_delta,
            token_type="share",
            extra_claims={"created_by": str(user.id)},
        )
        share_link = await self.course_repo.create_share_link(
            course_id=course_id,
            token=token,
            created_by=user.id,
            expires_at=expires_at,
        )
        await self.course_repo.session.commit()
        return {
            "course_id": course_id,
            "token": token,
            "share_url": f"{self.settings.public_app_url}/shared/course/{token}",
            "expires_at": share_link.expires_at,
            "access_count": share_link.access_count,
        }

    async def list_share_links(self, *, course_id: UUID, user: User) -> dict:
        course = await self.course_repo.get_course(course_id)
        if course.owner_id != user.id and user.role.name != "admin":
            raise UnauthorizedError("You cannot view share analytics for this course")
        share_links = await self.course_repo.list_share_links(course_id=course_id)
        items = [
            {
                "id": share_link.id,
                "course_id": share_link.course_id,
                "share_url": f"{self.settings.public_app_url}/shared/course/{share_link.token}",
                "expires_at": share_link.expires_at,
                "access_count": share_link.access_count,
                "created_at": share_link.created_at,
            }
            for share_link in share_links
        ]
        return {
            "items": items,
            "total_access_count": sum(item["access_count"] for item in items),
        }

    async def resolve_share_link(self, token: str, user: User | None) -> dict:
        try:
            payload = decode_token(self.settings, token)
        except Exception as exc:
            raise UnauthorizedError("Invalid share link") from exc
        if payload.get("type") != "share":
            raise UnauthorizedError("Invalid share link")
        share_link = await self.course_repo.get_share_link(token)
        if not share_link:
            raise NotFoundError("Share link not found")
        if str(share_link.course_id) != payload.get("sub"):
            raise UnauthorizedError("Invalid share link")
        if share_link.expires_at < datetime.now(timezone.utc):
            raise GoneError("Share link expired")
        course = await self.course_repo.get_course(share_link.course_id)
        await self.course_repo.increment_share_access(share_link)
        await self.course_repo.session.commit()
        is_enrolled = False
        if user is not None:
            enrollment = await self.course_repo.get_enrollment(user_id=user.id, course_id=course.id)
            is_enrolled = enrollment is not None
        topics = [await self._serialize_topic(topic) for topic in course.topics]
        return {
            "course": await self._serialize_course(course, user=user),
            "topics": topics,
            "is_enrolled": is_enrolled,
            "can_enroll": user is not None and not is_enrolled,
            "logged_in": user is not None,
        }

    async def _serialize_course(self, course: Course, user: User | None) -> dict:
        topic_count = len(course.topics)
        material_count = sum(len(topic.materials) for topic in course.topics)
        is_enrolled = False
        if user is not None:
            enrollment = await self.course_repo.get_enrollment(user_id=user.id, course_id=course.id)
            is_enrolled = enrollment is not None
        return {
            "id": course.id,
            "title": course.title,
            "description": course.description,
            "icon": course.icon,
            "color": course.color,
            "is_published": course.is_published,
            "topic_count": topic_count,
            "material_count": material_count,
            "is_enrolled": is_enrolled,
            "created_at": course.created_at,
            "updated_at": course.updated_at,
        }

    async def _ensure_can_read_course(self, course: Course, user: User | None) -> None:
        if course.is_published:
            return
        if user is None:
            raise UnauthorizedError("You cannot access this course")
        if course.owner_id == user.id or user.role.name == "admin":
            return
        enrollment = await self.course_repo.get_enrollment(user_id=user.id, course_id=course.id)
        if enrollment is None:
            raise UnauthorizedError("You cannot access this course")

    async def _serialize_topic(self, topic: Topic) -> dict:
        return {
            "id": topic.id,
            "course_id": topic.course_id,
            "title": topic.title,
            "position": topic.position,
            "status": topic.status,
            "material_count": len(topic.materials),
            "created_at": topic.created_at,
            "updated_at": topic.updated_at,
        }

    async def _serialize_material(self, material: Material) -> dict:
        return {
            "id": material.id,
            "topic_id": material.topic_id,
            "title": material.title,
            "material_type": material.material_type,
            "content": material.content,
            "file_path": material.file_path,
            "file_name": material.file_name,
            "created_at": material.created_at,
            "updated_at": material.updated_at,
        }
