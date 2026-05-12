"""Seed system company-scoped permission role templates.

Seeds three tenant-level roles that company admins can assign:
  - "Company Manager"  — full company-user CRUD + module write access
  - "Company Member"   — read-only access (default for new company users)

These roles have scope="company" but company_id=NULL, making them tenant-wide
templates. Company-specific custom roles are created at runtime via the API.

Revision ID: 004_seed_company_roles
Revises: 003_add_companies
Create Date: 2026-05-11
"""

import json
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

revision = "004_seed_company_roles"
down_revision = "003_add_companies"
branch_labels = None
depends_on = None

_MANAGER_PERMISSIONS = [
    "company:read",
    "company_user:read",
    "company_user:write",
    "company_user:delete",
    "role:read",
    "role:write",
    "audit:read",
    "document:read", "document:write", "document:approve", "document:delete",
    "quality_event:read", "quality_event:write",
    "capa:read", "capa:write", "capa:approve",
    "training:read", "training:write", "training:assign",
    "equipment:read", "equipment:write",
    "plate:read", "plate:write",
    "job:read", "job:write",
    "qa_review:read", "qa_review:write", "qa_review:approve",
    "crm:read", "crm:write",
    "contract:read", "contract:write",
    "workorder:read", "workorder:write", "workorder:execute",
    "certificate:read", "certificate:write", "certificate:issue",
    "billing:read",
    "report:read", "report:generate",
    "analytics:read",
]

_MEMBER_PERMISSIONS = [
    "document:read",
    "quality_event:read",
    "capa:read",
    "training:read",
    "equipment:read",
    "plate:read",
    "job:read",
    "qa_review:read",
    "crm:read",
    "contract:read",
    "workorder:read",
    "certificate:read",
    "report:read",
    "analytics:read",
]

_ROLES = [
    {
        "name": "Company Manager",
        "description": "Full company user management and module write access",
        "permissions": _MANAGER_PERMISSIONS,
    },
    {
        "name": "Company Member",
        "description": "Read-only access to all modules (default for company users)",
        "permissions": _MEMBER_PERMISSIONS,
    },
]


def upgrade() -> None:
    conn = op.get_bind()
    now = datetime.now(timezone.utc)
    for role_def in _ROLES:
        exists = conn.execute(
            sa.text("SELECT 1 FROM roles WHERE name = :name AND company_id IS NULL AND scope = 'company'"),
            {"name": role_def["name"]},
        ).scalar()
        if exists:
            continue
        conn.execute(
            sa.text("""
                INSERT INTO roles
                    (id, name, description, permissions, is_system_role, product,
                     scope, company_id, created_at, updated_at)
                VALUES
                    (:id, :name, :description, CAST(:perms AS JSONB), true, NULL,
                     'company', NULL, :created_at, :updated_at)
            """),
            {
                "id": _uuid7(),
                "name": role_def["name"],
                "description": role_def["description"],
                "perms": json.dumps(role_def["permissions"]),
                "created_at": now,
                "updated_at": now,
            },
        )


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM roles WHERE name IN ('Company Manager', 'Company Member')"
            " AND is_system_role = true AND scope = 'company' AND company_id IS NULL"
        )
    )
