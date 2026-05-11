"""Tenant Service — Core tenant provisioning domain service."""

import asyncio

import structlog
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from rainer_common.exceptions import ConflictError, NotFoundError

from ..core.config import Settings
from ..infra.db.repositories import TenantRepository, TenantSettingsRepository
from ..infra.db.models import Tenant

logger = structlog.get_logger(__name__)

# Postgres DDL (e.g. CREATE USER) does not accept bind params for PASSWORD.
# We still avoid injection by strictly validating identifiers and escaping literals.
_PG_IDENT_RE = __import__("re").compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def _pg_ident(name: str) -> str:
    """Return a safely quoted Postgres identifier."""
    if not _PG_IDENT_RE.fullmatch(name):
        raise ConflictError("Generated database identifier is invalid")
    return f'"{name}"'


def _pg_literal(value: str) -> str:
    """Return a safely quoted Postgres string literal."""
    return "'" + value.replace("'", "''") + "'"


# Base tenant DB schema — applied when a new tenant is created
BASE_TENANT_SCHEMA_SQL = """
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_user_id UUID NOT NULL UNIQUE,
    tenant_id UUID NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    phone VARCHAR(50),
    department VARCHAR(100),
    job_title VARCHAR(100),
    avatar_url TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    permissions JSONB NOT NULL DEFAULT '[]',
    is_system_role BOOLEAN NOT NULL DEFAULT FALSE,
    product VARCHAR(20),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    UNIQUE (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID NOT NULL DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(150) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    old_value JSONB,
    new_value JSONB,
    ip_address INET,
    user_agent TEXT,
    session_id UUID,
    product VARCHAR(20),
    module VARCHAR(100),
    signature VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

CREATE TABLE IF NOT EXISTS audit_logs_default PARTITION OF audit_logs DEFAULT;

CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    data JSONB NOT NULL DEFAULT '{}',
    channel VARCHAR(50) NOT NULL DEFAULT 'in_app',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    sent_at TIMESTAMPTZ,
    read_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS schema_migrations (
    id SERIAL PRIMARY KEY,
    version VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Default system roles
INSERT INTO roles (id, name, description, permissions, is_system_role)
VALUES 
    (gen_random_uuid(), 'Admin', 'Full tenant admin access', '["*"]', TRUE),
    (gen_random_uuid(), 'Manager', 'Manager access', '["document:*","capa:*","training:*"]', TRUE),
    (gen_random_uuid(), 'User', 'Standard user', '["document:read","capa:read","training:read"]', TRUE)
ON CONFLICT (name) DO NOTHING;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_users_platform ON users(platform_user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_user ON user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs(resource_type, resource_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id, status, created_at DESC);

INSERT INTO schema_migrations (version, name) VALUES ('001', 'initial_tenant_schema') ON CONFLICT DO NOTHING;
"""


class TenantDomainService:
    """Core tenant lifecycle and provisioning business logic."""

    def __init__(
        self,
        tenant_repo: TenantRepository,
        settings_repo: TenantSettingsRepository,
        settings: Settings,
    ) -> None:
        self._tenants = tenant_repo
        self._settings = settings_repo
        self._config = settings

    async def create_tenant(
        self,
        tenant_name: str,
        products: list[str],
        tier: str = "starter",
        region: str = "us-east-1",
        *,
        company_profile: dict | None = None,
        billing_profile: dict | None = None,
        primary_contact_first_name: str | None = None,
        primary_contact_last_name: str | None = None,
        primary_contact_email: str | None = None,
        primary_contact_phone: str | None = None,
        settings_timezone: str = "UTC",
        settings_locale: str = "en-US",
    ) -> Tenant:
        """
        Provision a new tenant:
        1. Create tenant record in Master DB
        2. Create tenant-specific PostgreSQL DB + user
        3. Run base schema migrations
        4. Create tenant settings
        5. Publish tenant.created event
        """
        # Check uniqueness
        existing = await self._tenants.get_by_name(tenant_name)
        if existing:
            raise ConflictError("tenant_name already exists")

        # Create Master DB record
        tenant = await self._tenants.create(
            tenant_name=tenant_name,
            products=products,
            tier=tier,
            region=region,
            db_host=self._config.default_tenant_db_host,
            db_port=self._config.default_tenant_db_port,
            company_profile=company_profile,
            billing_profile=billing_profile,
            primary_contact_first_name=primary_contact_first_name,
            primary_contact_last_name=primary_contact_last_name,
            primary_contact_email=primary_contact_email,
            primary_contact_phone=primary_contact_phone,
        )

        logger.info("tenant_created_in_master", tenant_id=tenant.id, tenant_name=tenant_name)

        try:
            # Provision tenant database
            await self._provision_db(tenant)

            # Update status to active
            await self._tenants.update_status(tenant.id, "active")
            tenant.status = "active"

            # Create settings with tenant defaults
            await self._settings.create(
                tenant_id=tenant.id,
                timezone=settings_timezone,
                locale=settings_locale,
            )

            logger.info("tenant_provisioned", tenant_id=tenant.id, db_name=tenant.db_name)
            return tenant

        except Exception as exc:
            logger.error("tenant_provisioning_failed", tenant_id=tenant.id, error=str(exc))
            await self._tenants.update_status(tenant.id, "provisioning_failed")
            raise

    async def update_tenant(self, tenant_id: str, **fields) -> None:
        """
        Update tenant fields while preventing unique constraint violations from
        surfacing as INTERNAL_SERVER_ERROR.
        """
        if "tenant_name" in fields and fields["tenant_name"]:
            existing = await self._tenants.get_by_name(fields["tenant_name"])
            if existing and existing.id != tenant_id:
                raise ConflictError("tenant_name already exists")

        await self._tenants.update(tenant_id, **fields)

    async def get_tenant(self, tenant_id: str) -> Tenant:
        tenant = await self._tenants.get_by_id(tenant_id)
        if not tenant:
            raise NotFoundError("Tenant", tenant_id)
        return tenant

    async def get_tenant_by_slug(self, slug: str) -> Tenant:
        tenant = await self._tenants.get_by_slug(slug)
        if not tenant:
            raise NotFoundError("Tenant", slug)
        return tenant

    async def list_tenants(
        self,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Tenant], int]:
        offset = (page - 1) * page_size
        return await self._tenants.list_all(status=status, offset=offset, limit=page_size)

    async def suspend_tenant(self, tenant_id: str) -> None:
        tenant = await self.get_tenant(tenant_id)
        if tenant.status == "suspended":
            raise ConflictError("Tenant is already suspended")
        await self._tenants.update_status(tenant_id, "suspended")
        logger.info("tenant_suspended", tenant_id=tenant_id)

    async def activate_tenant(self, tenant_id: str) -> None:
        tenant = await self.get_tenant(tenant_id)
        if tenant.status == "active":
            raise ConflictError("Tenant is already active")
        await self._tenants.update_status(tenant_id, "active")
        logger.info("tenant_activated", tenant_id=tenant_id)

    async def delete_tenant(self, tenant_id: str) -> None:
        tenant = await self.get_tenant(tenant_id)
        await self._tenants.soft_delete(tenant_id)
        logger.info("tenant_deleted", tenant_id=tenant_id)

    async def get_settings(self, tenant_id: str):
        await self.get_tenant(tenant_id)
        settings = await self._settings.get_by_tenant(tenant_id)
        if not settings:
            raise NotFoundError("TenantSettings", tenant_id)
        return settings

    async def update_settings(self, tenant_id: str, **fields) -> None:
        await self.get_tenant(tenant_id)
        await self._settings.update(tenant_id, **fields)

    async def _provision_db(self, tenant) -> None:
        """Create tenant DB, user, and apply base schema."""
        from rainer_tenant_lib.credentials import derive_tenant_password

        db_password = derive_tenant_password(tenant.id, self._config.rainer_master_secret)
        db_user_ident = _pg_ident(tenant.db_user)
        db_name_ident = _pg_ident(tenant.db_name)
        db_password_lit = _pg_literal(db_password)

        # Connect as admin to postgres to create DB/user
        admin_engine = create_async_engine(
            self._config.postgres_admin_url.replace(
                "postgresql://", "postgresql+asyncpg://"
            ),
            isolation_level="AUTOCOMMIT",
        )

        try:
            async with admin_engine.connect() as conn:
                # Ensure role exists (idempotent) and has expected password
                role_exists = await conn.execute(
                    text("SELECT 1 FROM pg_roles WHERE rolname = :name"),
                    {"name": tenant.db_user},
                )
                if role_exists.scalar_one_or_none() is None:
                    # NOTE: Postgres does not accept a bind parameter for CREATE/ALTER ROLE password;
                    # it must be a SQL literal. `_pg_literal` ensures safe quoting.
                    await conn.execute(text(f"CREATE USER {db_user_ident} WITH PASSWORD {db_password_lit}"))
                else:
                    # Keep provisioning stable across retries
                    await conn.execute(text(f"ALTER ROLE {db_user_ident} WITH PASSWORD {db_password_lit}"))

                # Ensure database exists (idempotent)
                db_exists = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": tenant.db_name},
                )
                if db_exists.scalar_one_or_none() is None:
                    await conn.execute(
                        text(f"CREATE DATABASE {db_name_ident} OWNER {db_user_ident}")
                    )
        finally:
            await admin_engine.dispose()

        # Connect to new tenant DB and apply base schema
        tenant_dsn = (
            f"postgresql+asyncpg://{tenant.db_user}:{db_password}"
            f"@{tenant.db_host}:{tenant.db_port}/{tenant.db_name}"
        )
        tenant_engine = create_async_engine(tenant_dsn, isolation_level="AUTOCOMMIT")
        try:
            async with tenant_engine.connect() as conn:
                # asyncpg disallows multiple statements per prepared statement.
                # Execute the schema one statement at a time for compatibility.
                for stmt in BASE_TENANT_SCHEMA_SQL.split(";"):
                    statement = stmt.strip()
                    if not statement:
                        continue
                    await conn.execute(text(statement))
        finally:
            await tenant_engine.dispose()

        logger.info("tenant_db_provisioned", tenant_id=tenant.id, db_name=tenant.db_name)
