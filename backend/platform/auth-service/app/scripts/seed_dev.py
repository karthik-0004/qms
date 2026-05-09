"""Dev seed entrypoint for auth-service (idempotent).

This script is intentionally **env-driven** so credentials are never hardcoded in code.

Runs (if corresponding env vars are provided):
- Super admin seed (AUTH_SUPERADMIN_EMAIL / AUTH_SUPERADMIN_PASSWORD)
- Tenant admin seed (AUTH_TENANTADMIN_EMAIL / AUTH_TENANTADMIN_PASSWORD / AUTH_TENANTADMIN_TENANT_ID / AUTH_TENANTADMIN_ROLE)

Usage (inside container):
  python -m app.scripts.seed_dev
"""

import asyncio

import structlog

from app.scripts.create_super_admin import _create_or_update_super_admin
from app.scripts.create_tenant_admin import _create_or_update_tenant_admin

logger = structlog.get_logger(__name__)


async def _run() -> None:
    errors: list[str] = []

    for name, fn in (
        ("super_admin", _create_or_update_super_admin),
        ("tenant_admin", _create_or_update_tenant_admin),
    ):
        try:
            await fn()
        except SystemExit:
            # Underlying scripts are strict (missing env / weak password / missing tenant).
            # We keep seed_dev idempotent and allow partial seeding.
            errors.append(name)
        except Exception:
            logger.exception("seed_failed", seed=name)
            errors.append(name)

    if errors:
        logger.warning(
            "seed_completed_with_warnings",
            message="Some seed steps were skipped or failed. See logs above.",
            failed_or_skipped=errors,
        )
    else:
        logger.info("seed_completed", message="All configured seed steps completed successfully.")


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()

