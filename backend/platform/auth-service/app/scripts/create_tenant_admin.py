"""One-off script to create or update a tenant admin user in the master DB.

Usage (from repo root, with docker-compose stack running):

    # 1) Pick an existing tenant id (UUID) from tenant-service (or create one)
    # 2) Set desired credentials (dev-only; do NOT use in production)
    export AUTH_TENANTADMIN_EMAIL="<email>"
    export AUTH_TENANTADMIN_PASSWORD="<strong-password>"
    export AUTH_TENANTADMIN_TENANT_ID="<tenant-uuid>"
    export AUTH_TENANTADMIN_ROLE="<role>"

    # Run inside the auth-service container
    docker-compose exec auth-service python -m app.scripts.create_tenant_admin
"""

import asyncio
import os

import structlog
from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password, is_strong_password
from app.infra.db.models import Tenant
from app.infra.db.repositories import UserRepository

logger = structlog.get_logger(__name__)


async def _create_or_update_tenant_admin() -> None:
    email = os.environ.get("AUTH_TENANTADMIN_EMAIL")
    password = os.environ.get("AUTH_TENANTADMIN_PASSWORD")
    tenant_id = os.environ.get("AUTH_TENANTADMIN_TENANT_ID")
    role = os.environ.get("AUTH_TENANTADMIN_ROLE")

    if not email or not password or not tenant_id or not role:
        logger.error(
            "tenant_admin_env_missing",
            message=(
                "AUTH_TENANTADMIN_EMAIL, AUTH_TENANTADMIN_PASSWORD, and "
                "AUTH_TENANTADMIN_TENANT_ID, and AUTH_TENANTADMIN_ROLE must be set "
                "before running this script."
            ),
        )
        raise SystemExit(1)

    if not is_strong_password(password):
        logger.error(
            "tenant_admin_weak_password",
            message=(
                "Provided AUTH_TENANTADMIN_PASSWORD does not meet strength policy. "
                "Use at least 8 chars with upper/lower/digit/special."
            ),
        )
        raise SystemExit(1)

    async with AsyncSessionLocal() as session:
        # Ensure tenant exists
        tenant = (await session.execute(select(Tenant).where(Tenant.id == tenant_id))).scalar_one_or_none()
        if not tenant:
            logger.error("tenant_not_found", tenant_id=tenant_id)
            raise SystemExit(1)

        repo = UserRepository(session)
        existing = await repo.get_by_email(email)
        password_hash = hash_password(password)

        if existing:
            existing.tenant_id = tenant_id
            existing.role = role
            existing.password_hash = password_hash
            logger.info(
                "tenant_admin_updated",
                user_id=existing.id,
                email=existing.email,
                tenant_id=tenant_id,
                role=role,
            )
        else:
            user = await repo.create(
                email=email,
                password_hash=password_hash,
                tenant_id=tenant_id,
                role=role,
            )
            logger.info(
                "tenant_admin_created",
                user_id=user.id,
                email=user.email,
                tenant_id=tenant_id,
                role=role,
            )

        await session.commit()


def main() -> None:
    asyncio.run(_create_or_update_tenant_admin())


if __name__ == "__main__":
    main()

