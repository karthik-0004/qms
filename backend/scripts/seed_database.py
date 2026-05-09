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
SEED_TENANT_DB_HOST = os.getenv("SEED_TENANT_DB_HOST")
SEED_TENANT_DB_PORT = os.getenv("SEED_TENANT_DB_PORT")
SEED_TENANT_STATUS = os.getenv("SEED_TENANT_STATUS")
SEED_TENANT_TIER = os.getenv("SEED_TENANT_TIER")
SEED_TENANT_PRODUCTS = os.getenv("SEED_TENANT_PRODUCTS")
SEED_TENANT_REGION = os.getenv("SEED_TENANT_REGION")
SEED_PLATFORM_ADMIN_ROLE = os.getenv("SEED_PLATFORM_ADMIN_ROLE")
SEED_PLATFORM_ADMIN_STATUS = os.getenv("SEED_PLATFORM_ADMIN_STATUS")
SEED_PLATFORM_ADMIN_MFA_ENABLED = os.getenv("SEED_PLATFORM_ADMIN_MFA_ENABLED")
SEED_PLATFORM_ADMIN_FAILED_ATTEMPTS = os.getenv("SEED_PLATFORM_ADMIN_FAILED_ATTEMPTS")

# Optional: seed tenant admin user (dev convenience).
# Keep values env-driven (never hardcode credentials).
TENANTADMIN_EMAIL = os.getenv("TENANTADMIN_EMAIL")
TENANTADMIN_PASSWORD = os.getenv("TENANTADMIN_PASSWORD")
TENANTADMIN_PASSWORD_HASH = os.getenv("TENANTADMIN_PASSWORD_HASH")
TENANTADMIN_ROLE = (os.getenv("TENANTADMIN_ROLE") or "tenant_admin").strip()


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


def _parse_int(value: str, *, name: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"Invalid int for {name}") from exc


def _parse_bool(value: str, *, name: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise RuntimeError(f"Invalid bool for {name}")


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


def _get_tenantadmin_password_hash() -> str:
    if TENANTADMIN_PASSWORD_HASH:
        return TENANTADMIN_PASSWORD_HASH
    if not TENANTADMIN_PASSWORD:
        raise RuntimeError(
            "Missing required env var: TENANTADMIN_PASSWORD or TENANTADMIN_PASSWORD_HASH"
        )
    try:
        import bcrypt  # type: ignore
    except ImportError as exc:
        raise RuntimeError("bcrypt is required when using TENANTADMIN_PASSWORD") from exc
    return bcrypt.hashpw(
        TENANTADMIN_PASSWORD.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")


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

    tenant_slug = (SEED_TENANT_SLUG or _require_env("SEED_TENANT_SLUG")).strip()
    tenant_name = (SEED_TENANT_NAME or _require_env("SEED_TENANT_NAME")).strip()
    tenant_db_name = f"rainer_tenant_{tenant_slug.replace('-', '_')}"
    tenant_db_user = f"rainer_{tenant_slug.replace('-', '_')}"

    tenant_db_host = (SEED_TENANT_DB_HOST or _require_env("SEED_TENANT_DB_HOST")).strip()
    tenant_db_port = _parse_int((SEED_TENANT_DB_PORT or _require_env("SEED_TENANT_DB_PORT")).strip(), name="SEED_TENANT_DB_PORT")
    tenant_status = (SEED_TENANT_STATUS or _require_env("SEED_TENANT_STATUS")).strip()
    tenant_tier = (SEED_TENANT_TIER or _require_env("SEED_TENANT_TIER")).strip()
    tenant_products = (SEED_TENANT_PRODUCTS or _require_env("SEED_TENANT_PRODUCTS")).strip()
    tenant_region = (SEED_TENANT_REGION or _require_env("SEED_TENANT_REGION")).strip()

    platform_admin_role = (SEED_PLATFORM_ADMIN_ROLE or _require_env("SEED_PLATFORM_ADMIN_ROLE")).strip()
    platform_admin_status = (SEED_PLATFORM_ADMIN_STATUS or _require_env("SEED_PLATFORM_ADMIN_STATUS")).strip()
    platform_admin_mfa_enabled = _parse_bool(
        (SEED_PLATFORM_ADMIN_MFA_ENABLED or _require_env("SEED_PLATFORM_ADMIN_MFA_ENABLED")).strip(),
        name="SEED_PLATFORM_ADMIN_MFA_ENABLED",
    )
    platform_admin_failed_attempts = _parse_int(
        (SEED_PLATFORM_ADMIN_FAILED_ATTEMPTS or _require_env("SEED_PLATFORM_ADMIN_FAILED_ATTEMPTS")).strip(),
        name="SEED_PLATFORM_ADMIN_FAILED_ATTEMPTS",
    )

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
                    "db_host": tenant_db_host,
                    "db_port": tenant_db_port,
                    "status": tenant_status,
                    "tier": tenant_tier,
                    "products": tenant_products,
                    "region": tenant_region,
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
                    "role": platform_admin_role,
                    "status": platform_admin_status,
                    "mfa_enabled": platform_admin_mfa_enabled,
                    "failed_attempts": platform_admin_failed_attempts,
                    "now": now,
                },
            )
            print(f"  ✅ Created admin user: {ADMIN_EMAIL} (id={user_id})")

        # ── 3. Seed tenant admin user (optional) ─────────────────────────
        # Only runs when TENANTADMIN_EMAIL is provided.
        if TENANTADMIN_EMAIL:
            try:
                tenantadmin_password_hash = _get_tenantadmin_password_hash()
            except RuntimeError as exc:
                print(f"  ⚠️  Skipping tenant admin seed: {exc}")
            else:
                existing_tenantadmin = await conn.execute(
                    text("SELECT id FROM platform_users WHERE email = :email"),
                    {"email": TENANTADMIN_EMAIL},
                )
                row = existing_tenantadmin.fetchone()
                if row:
                    await conn.execute(
                        text("""
                            UPDATE platform_users
                               SET tenant_id = :tenant_id,
                                   password_hash = :password_hash,
                                   role = :role,
                                   status = 'active',
                                   updated_at = :now
                             WHERE email = :email
                        """),
                        {
                            "tenant_id": tenant_id,
                            "password_hash": tenantadmin_password_hash,
                            "role": TENANTADMIN_ROLE,
                            "now": now,
                            "email": TENANTADMIN_EMAIL,
                        },
                    )
                    print(f"  ✅ Updated tenant admin user: {TENANTADMIN_EMAIL}")
                else:
                    tenantadmin_user_id = str(uuid.uuid4())
                    await conn.execute(
                        text("""
                            INSERT INTO platform_users (id, tenant_id, email, password_hash, role, status, mfa_enabled, failed_attempts, created_at, updated_at)
                            VALUES (:id, :tenant_id, :email, :password_hash, :role, :status, :mfa_enabled, :failed_attempts, :now, :now)
                        """),
                        {
                            "id": tenantadmin_user_id,
                            "tenant_id": tenant_id,
                            "email": TENANTADMIN_EMAIL,
                            "password_hash": tenantadmin_password_hash,
                            "role": TENANTADMIN_ROLE,
                            "status": "active",
                            "mfa_enabled": False,
                            "failed_attempts": 0,
                            "now": now,
                        },
                    )
                    print(
                        f"  ✅ Created tenant admin user: {TENANTADMIN_EMAIL} (id={tenantadmin_user_id})"
                    )

    await engine.dispose()
    print("\n✅ Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
