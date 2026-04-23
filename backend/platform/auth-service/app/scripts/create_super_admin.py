"""One-off script to create or update a super admin user in the master DB.

Usage (from repo root, with docker-compose stack running):

    # Set desired credentials (dev-only; do NOT use in production)
    export AUTH_SUPERADMIN_EMAIL="superadmin@rainer.local"
    export AUTH_SUPERADMIN_PASSWORD="SuperAdmin123!"

    # Run inside the auth-service container
    docker-compose exec auth-service python -m app.scripts.create_super_admin
"""

import asyncio
import os

import structlog

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password, is_strong_password
from app.infra.db.repositories import UserRepository


logger = structlog.get_logger(__name__)


async def _create_or_update_super_admin() -> None:
    email = os.environ.get("AUTH_SUPERADMIN_EMAIL")
    password = os.environ.get("AUTH_SUPERADMIN_PASSWORD")

    if not email or not password:
        logger.error(
            "super_admin_env_missing",
            message=(
                "AUTH_SUPERADMIN_EMAIL and AUTH_SUPERADMIN_PASSWORD must be set "
                "before running this script."
            ),
        )
        raise SystemExit(1)

    if not is_strong_password(password):
        logger.error(
            "super_admin_weak_password",
            message=(
                "Provided AUTH_SUPERADMIN_PASSWORD does not meet strength policy. "
                "Use at least 8 chars with upper/lower/digit/special."
            ),
        )
        raise SystemExit(1)

    async with AsyncSessionLocal() as session:
        repo = UserRepository(session)

        existing = await repo.get_by_email(email)
        password_hash = hash_password(password)

        if existing:
            # Ensure role + password are up to date
            existing.role = "super_admin"
            existing.password_hash = password_hash
            logger.info(
                "super_admin_updated",
                user_id=existing.id,
                email=existing.email,
            )
        else:
            user = await repo.create(
                email=email,
                password_hash=password_hash,
                tenant_id=None,
                role="super_admin",
            )
            logger.info(
                "super_admin_created",
                user_id=user.id,
                email=user.email,
            )

        await session.commit()


def main() -> None:
    asyncio.run(_create_or_update_super_admin())


if __name__ == "__main__":
    main()

