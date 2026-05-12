"""Seed default Admin role for directory RBAC.

Revision ID: 002_seed_system_roles
Revises: 001_initial_schema
Create Date: 2026-05-11
"""

import os
import time
import uuid as _uuid_mod
from datetime import datetime, timezone

import sqlalchemy as sa
from alembic import op


def _uuid7() -> str:
    ts_ms = int(time.time() * 1000) & 0xFFFF_FFFF_FFFF
    rand = int.from_bytes(os.urandom(10), "big")
    upper = (ts_ms << 16) | (0x7 << 12) | ((rand >> 68) & 0xFFF)
    lower = 0x8000_0000_0000_0000 | (rand & 0x3FFF_FFFF_FFFF_FFFF)
    return str(_uuid_mod.UUID(int=(upper << 64) | lower))

revision = "002_seed_system_roles"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    exists = conn.execute(sa.text("SELECT 1 FROM roles WHERE name = 'Admin'")).scalar()
    if exists:
        return
    rid = _uuid7()
    now = datetime.now(timezone.utc)
    conn.execute(
        sa.text("""
            INSERT INTO roles (id, name, description, permissions, is_system_role, product, created_at, updated_at)
            VALUES (:id, 'Admin', 'Full tenant access', CAST(:perms AS JSONB), true, NULL, :created_at, :updated_at)
        """),
        {
            "id": rid,
            "perms": '["*"]',
            "created_at": now,
            "updated_at": now,
        },
    )


def downgrade() -> None:
    op.execute(sa.text("DELETE FROM roles WHERE name = 'Admin' AND is_system_role = true"))
