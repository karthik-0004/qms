#!/usr/bin/env python3
"""
Bootstrap seed script — creates an initial tenant and platform admin user (master DB).

Usage:
    python backend/scripts/seed_database.py

Requires:
    DATABASE_URL env var pointing to the master DB.
"""
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure backend packages are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH")
SEED_TENANT_NAME = os.getenv("SEED_TENANT_NAME")
SEED_TENANT_SLUG = os.getenv("SEED_TENANT_SLUG")


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _get_admin_password_hash() -> str:
    if ADMIN_PASSWORD_HASH:
        return ADMIN_PASSWORD_HASH
    if not ADMIN_PASSWORD:
        raise RuntimeError("Missing required env var: ADMIN_PASSWORD or ADMIN_PASSWORD_HASH")
    try:
        import bcrypt  # type: ignore
    except ImportError as exc:
        raise RuntimeError("bcrypt is required when using ADMIN_PASSWORD") from exc
    return bcrypt.hashpw(ADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def main():
    global DATABASE_URL, ADMIN_EMAIL
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
    except ImportError:
        print("ERROR: sqlalchemy[asyncio] + asyncpg not installed.")
        print("  pip install sqlalchemy[asyncio] asyncpg")
        sys.exit(1)

    try:
        DATABASE_URL = DATABASE_URL or _require_env("DATABASE_URL")
        ADMIN_EMAIL = ADMIN_EMAIL or _require_env("ADMIN_EMAIL")
        admin_password_hash = _get_admin_password_hash()
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        sys.exit(1)

    engine = create_async_engine(DATABASE_URL, echo=False)

    now = datetime.now(timezone.utc)
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    tenant_slug = (SEED_TENANT_SLUG or "rainertek-default").strip()
    tenant_name = (SEED_TENANT_NAME or "RainerTek (Default)").strip()
    tenant_db_name = f"rainer_tenant_{tenant_slug.replace('-', '_')}"
    tenant_db_user = f"rainer_{tenant_slug.replace('-', '_')}"

    async with engine.begin() as conn:
        # ── 1. Seed admin tenant ─────────────────────────────────────────
        existing = await conn.execute(
            text("SELECT id FROM tenants WHERE slug = :slug"), {"slug": tenant_slug}
        )
        if existing.fetchone():
            print(f"  ⏭️  Tenant '{tenant_slug}' already exists")
        else:
            await conn.execute(
                text("""
                    INSERT INTO tenants (id, tenant_name, slug, db_name, db_user, db_host, db_port, status, tier, products, region, created_at, updated_at)
                    VALUES (:id, :tenant_name, :slug, :db_name, :db_user, :db_host, :db_port, :status, :tier, :products, :region, :now, :now)
                """),
                {
                    "id": tenant_id,
                    "tenant_name": tenant_name,
                    "slug": tenant_slug,
                    "db_name": tenant_db_name,
                    "db_user": tenant_db_user,
                    "db_host": "postgres",
                    "db_port": 5432,
                    "status": "active",
                    "tier": "starter",
                    "products": "[]",
                    "region": "us-east-1",
                    "now": now,
                },
            )
            print(f"  ✅ Created tenant: {tenant_slug} (id={tenant_id})")

        # ── 2. Seed platform admin user ──────────────────────────────────
        existing_user = await conn.execute(
            text("SELECT id FROM platform_users WHERE email = :email"),
            {"email": ADMIN_EMAIL},
        )
        if existing_user.fetchone():
            print(f"  ⏭️  User '{ADMIN_EMAIL}' already exists")
        else:
            await conn.execute(
                text("""
                    INSERT INTO platform_users (id, tenant_id, email, password_hash, role, status, mfa_enabled, failed_attempts, created_at, updated_at)
                    VALUES (:id, :tenant_id, :email, :password_hash, :role, :status, :mfa_enabled, :failed_attempts, :now, :now)
                """),
                {
                    "id": user_id,
                    "tenant_id": tenant_id,
                    "email": ADMIN_EMAIL,
                    "password_hash": admin_password_hash,
                    "role": "admin",
                    "status": "active",
                    "mfa_enabled": False,
                    "failed_attempts": 0,
                    "now": now,
                },
            )
            print(f"  ✅ Created admin user: {ADMIN_EMAIL} (id={user_id})")

    await engine.dispose()
    print("\n✅ Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
