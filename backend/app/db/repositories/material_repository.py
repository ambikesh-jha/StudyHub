from __future__ import annotations

from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.material import Material
from app.db.repositories.base import CursorRepository


class MaterialRepository(CursorRepository):
    async def list_materials(self, *, topic_id: UUID, cursor: str | None = None, limit: int = 20) -> tuple[list[Material], str | None]:
        query = (
            select(Material)
            .where(Material.topic_id == topic_id)
            .order_by(Material.created_at.desc(), Material.id.desc())
            .limit(limit + 1)
        )
        if cursor:
            query = self._apply_cursor(query, Material, cursor)
        result = await self.session.execute(query)
        materials = list(result.scalars().all())
        next_cursor = None
        if len(materials) > limit:
            next_cursor = self._build_next_cursor(materials[:limit])
            materials = materials[:limit]
        return materials, next_cursor

    async def get_material(self, material_id: UUID, topic_id: UUID | None = None) -> Material:
        query = select(Material).where(Material.id == material_id)
        if topic_id is not None:
            query = query.where(Material.topic_id == topic_id)
        result = await self.session.execute(query)
        material = result.scalar_one_or_none()
        if not material:
            raise NotFoundError("Material not found")
        return material

    async def create_material(self, *, topic_id: UUID, title: str, material_type, content: str | None = None, file_path: str | None = None, file_name: str | None = None) -> Material:
        material = Material(topic_id=topic_id, title=title, material_type=material_type, content=content, file_path=file_path, file_name=file_name)
        self.session.add(material)
        await self.session.flush()
        return material

    async def delete_material(self, material: Material) -> None:
        await self.session.delete(material)

