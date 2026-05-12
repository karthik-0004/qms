"""Dev-only: upsert canonical Acme tenant + tenant admin login (parity across machines).

This does **not** enforce `is_strong_password` so documented dev passwords like
``TenantAdmin1`` remain usable locally. Disabled when SKIP_DEV_TENANTADMIN_BOOTSTRAP=1.

Run after auth + tenant alembic migrations on rainer_master (see docker-compose).
"""

from __future__ import annotations

import asyncio
import os
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy import select, text

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.infra.db.models import Tenant
from app.infra.db.repositories import UserRepository

logger = structlog.get_logger(__name__)


def _skip() -> bool:
    raw = os.getenv("SKIP_DEV_TENANTADMIN_BOOTSTRAP", "").strip().lower()
    return raw in ("1", "true", "yes", "on")


async def _ensure_tenant_id(session, *, slug: str, name: str) -> str:
    res = await session.execute(
        select(Tenant.id).where(Tenant.slug == slug, Tenant.deleted_at.is_(None))
    )
    row = res.scalar_one_or_none()
    if row:
        return str(row)

    tid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    slug_db = slug.replace("-", "_")
    db_name = f"rainer_tenant_{slug_db}"
    db_user = f"rainer_{slug_db}"

    # Raw insert avoids ORM drift if some profile columns are missing before tenant migrations.
    await session.execute(
        text(
            """
            INSERT INTO tenants (
                id, tenant_name, slug, db_name, db_user, db_host, db_port,
                status, tier, products, region, created_at, updated_at
            )
            VALUES (
                CAST(:id AS uuid), :tenant_name, :slug, :db_name, :db_user,
                'postgres', 5432, 'active', 'starter', '[]'::jsonb,
                'us-east-1', :now, :now
            )
            ON CONFLICT (slug) DO NOTHING
            """
        ),
        {
            "id": tid,
            "tenant_name": name,
            "slug": slug,
            "db_name": db_name,
            "db_user": db_user,
            "now": now,
        },
    )

    await session.flush()

    res2 = await session.execute(
        select(Tenant.id).where(Tenant.slug == slug, Tenant.deleted_at.is_(None))
    )
    resolved = res2.scalar_one_or_none()
    if not resolved:
        raise RuntimeError(f"bootstrap: could not resolve tenant slug={slug}")
    return str(resolved)


async def _bootstrap() -> None:
    email = os.getenv(
        "DEV_TENANTADMIN_EMAIL", "tenantadmin@acme.com"
    ).strip().lower()
    password = os.getenv("DEV_TENANTADMIN_PASSWORD", "TenantAdmin1")
    slug = os.getenv("DEV_BOOTSTRAP_TENANT_SLUG", "acme").strip().lower()
    tenant_name = os.getenv(
        "DEV_BOOTSTRAP_TENANT_NAME", "Acme Corporation"
    ).strip()
    role = os.getenv("DEV_TENANTADMIN_ROLE", "tenant_admin").strip()

    if _skip():
        logger.info("bootstrap_dev_tenant_admin_skipped")
        return

    async with AsyncSessionLocal() as session:
        tenant_id = await _ensure_tenant_id(session, slug=slug, name=tenant_name)
        repo = UserRepository(session)
        password_hash = hash_password(password)
        existing = await repo.get_by_email(email)

        if existing:
            existing.tenant_id = tenant_id
            existing.role = role
            existing.password_hash = password_hash
            existing.status = "active"
            existing.failed_attempts = 0
            existing.locked_until = None
            existing.updated_at = datetime.now(timezone.utc)
            logger.info(
                "bootstrap_dev_tenant_admin_updated",
                email=email,
                tenant_id=tenant_id,
            )
        else:
            await repo.create(
                email=email,
                password_hash=password_hash,
                tenant_id=tenant_id,
                role=role,
            )
            logger.info(
                "bootstrap_dev_tenant_admin_created",
                email=email,
                tenant_id=tenant_id,
            )

        await session.commit()


def main() -> None:
    asyncio.run(_bootstrap())


if __name__ == "__main__":
    main()
