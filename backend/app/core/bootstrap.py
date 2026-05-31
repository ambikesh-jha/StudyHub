from __future__ import annotations

from sqlalchemy import select

from app.db.session import async_session_factory
from app.models.role import Role


async def seed_roles() -> None:
    async with async_session_factory() as session:
        existing = await session.execute(select(Role.name))
        current_names = set(existing.scalars().all())
        required = {"admin", "user"}
        for name in sorted(required - current_names):
            session.add(Role(name=name))
        if required - current_names:
            await session.commit()

