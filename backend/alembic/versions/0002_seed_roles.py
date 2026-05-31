"""Seed default roles.

Revision ID: 0002_seed_roles
Revises: 0001_initial
Create Date: 2026-05-31 00:10:00.000000
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from alembic import op
import sqlalchemy as sa

revision = "0002_seed_roles"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


roles_table = sa.table(
    "roles",
    sa.column("id", sa.Uuid()),
    sa.column("name", sa.String()),
    sa.column("created_at", sa.DateTime(timezone=True)),
    sa.column("updated_at", sa.DateTime(timezone=True)),
)


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            """
            INSERT INTO roles (id, name, created_at, updated_at)
            VALUES
                ('00000000-0000-0000-0000-000000000001', 'admin', now(), now()),
                ('00000000-0000-0000-0000-000000000002', 'user', now(), now())
            ON CONFLICT (name) DO NOTHING
            """
        )
        return

    now = datetime.now(timezone.utc)
    existing = {row[0] for row in bind.execute(sa.text("SELECT name FROM roles")).all()}
    rows = []
    if "admin" not in existing:
        rows.append(
            {
                "id": UUID("00000000-0000-0000-0000-000000000001"),
                "name": "admin",
                "created_at": now,
                "updated_at": now,
            }
        )
    if "user" not in existing:
        rows.append(
            {
                "id": UUID("00000000-0000-0000-0000-000000000002"),
                "name": "user",
                "created_at": now,
                "updated_at": now,
            }
        )
    if rows:
        op.bulk_insert(roles_table, rows)


def downgrade() -> None:
    op.execute("DELETE FROM roles WHERE name IN ('admin', 'user')")
