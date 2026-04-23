#!/usr/bin/env python3
"""
Bootstrap seed script — creates admin tenant, admin user, and platform config defaults.

Usage:
    python backend/scripts/seed_database.py

Requires:
    DATABASE_URL env var pointing to the master DB.
    RAINER_MASTER_SECRET env var for HMAC-based tenant DB password derivation.
"""
import asyncio
import hashlib
import hmac
import os
import sys
import uuid
from datetime import datetime, timezone

# Ensure backend packages are importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://rainer:rainer_dev_password@localhost:5432/rainer_master",
)
MASTER_SECRET = os.getenv("RAINER_MASTER_SECRET", "dev-master-secret-change-in-production")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@rainertek.com")
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    # bcrypt hash for "RainerAdmin123!" — replace in production
    "$2b$12$LJ3m5ZQOJci.eFEVVx3BqORXV0JKH4rG1FGP.TJH6z4AbCrfD7VhK",
)


def derive_tenant_password(tenant_slug: str) -> str:
    """HMAC-SHA256 derived password for tenant DB."""
    return hmac.new(
        MASTER_SECRET.encode(), tenant_slug.encode(), hashlib.sha256
    ).hexdigest()[:32]


async def main():
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
    except ImportError:
        print("ERROR: sqlalchemy[asyncio] + asyncpg not installed.")
        print("  pip install sqlalchemy[asyncio] asyncpg")
        sys.exit(1)

    engine = create_async_engine(DATABASE_URL, echo=False)

    now = datetime.now(timezone.utc)
    tenant_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    tenant_slug = "rainertek-default"

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
                    INSERT INTO tenants (id, name, slug, status, db_host, db_port, db_name, db_user, db_password_hash, created_at, updated_at)
                    VALUES (:id, :name, :slug, :status, :db_host, :db_port, :db_name, :db_user, :db_password_hash, :now, :now)
                """),
                {
                    "id": tenant_id,
                    "name": "RainerTek (Default)",
                    "slug": tenant_slug,
                    "status": "active",
                    "db_host": "postgres",
                    "db_port": 5432,
                    "db_name": f"rainer_tenant_{tenant_slug.replace('-', '_')}",
                    "db_user": f"rainer_{tenant_slug.replace('-', '_')}",
                    "db_password_hash": derive_tenant_password(tenant_slug),
                    "now": now,
                },
            )
            print(f"  ✅ Created tenant: {tenant_slug} (id={tenant_id})")

        # ── 2. Seed admin user ───────────────────────────────────────────
        existing_user = await conn.execute(
            text("SELECT id FROM users WHERE email = :email"), {"email": ADMIN_EMAIL}
        )
        if existing_user.fetchone():
            print(f"  ⏭️  User '{ADMIN_EMAIL}' already exists")
        else:
            await conn.execute(
                text("""
                    INSERT INTO users (id, tenant_id, email, password_hash, first_name, last_name, role, status, is_active, created_at, updated_at)
                    VALUES (:id, :tenant_id, :email, :password_hash, :first_name, :last_name, :role, :status, :is_active, :now, :now)
                """),
                {
                    "id": user_id,
                    "tenant_id": tenant_id,
                    "email": ADMIN_EMAIL,
                    "password_hash": ADMIN_PASSWORD_HASH,
                    "first_name": "Platform",
                    "last_name": "Admin",
                    "role": "admin",
                    "status": "active",
                    "is_active": True,
                    "now": now,
                },
            )
            print(f"  ✅ Created admin user: {ADMIN_EMAIL} (id={user_id})")

        # ── 3. Seed platform config defaults ─────────────────────────────
        config_defaults = [
            ("platform.name", "Rainer Platform", "Platform display name"),
            ("platform.timezone", "America/New_York", "Default timezone"),
            ("platform.mfa_enforced", "false", "Enforce MFA for all users"),
            ("platform.audit_logging", "true", "Enable audit logging"),
            ("platform.max_login_attempts", "5", "Max failed login attempts before lockout"),
            ("platform.session_timeout_minutes", "30", "Session idle timeout"),
            ("feature.qms_enabled", "true", "Enable RainerQMS module"),
            ("feature.em_enabled", "true", "Enable EndGameBiotech EM module"),
            ("feature.ccv_enabled", "true", "Enable RainerCCV module"),
        ]

        for key, value, description in config_defaults:
            existing_cfg = await conn.execute(
                text("SELECT key FROM platform_config WHERE key = :key"), {"key": key}
            )
            if existing_cfg.fetchone():
                print(f"  ⏭️  Config '{key}' already exists")
            else:
                await conn.execute(
                    text("""
                        INSERT INTO platform_config (id, key, value, description, created_at, updated_at)
                        VALUES (:id, :key, :value, :description, :now, :now)
                    """),
                    {
                        "id": str(uuid.uuid4()),
                        "key": key,
                        "value": value,
                        "description": description,
                        "now": now,
                    },
                )
                print(f"  ✅ Config: {key} = {value}")

    await engine.dispose()
    print("\n✅ Seed complete!")


if __name__ == "__main__":
    asyncio.run(main())
