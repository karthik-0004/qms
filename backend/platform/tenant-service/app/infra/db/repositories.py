"""Tenant Service — Repository layer."""

import re
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Tenant, TenantSettings


class TenantRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, tenant_id: str) -> Tenant | None:
        result = await self._db.execute(
            select(Tenant).where(
                Tenant.id == tenant_id,
                Tenant.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Tenant | None:
        result = await self._db.execute(
            select(Tenant).where(
                Tenant.slug == slug,
                Tenant.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Tenant | None:
        result = await self._db.execute(
            select(Tenant).where(
                Tenant.tenant_name == name,
                Tenant.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(
        self,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Tenant], int]:
        from sqlalchemy import func

        query = select(Tenant).where(Tenant.deleted_at.is_(None))
        count_query = select(func.count()).select_from(Tenant).where(Tenant.deleted_at.is_(None))

        if status:
            query = query.where(Tenant.status == status)
            count_query = count_query.where(Tenant.status == status)

        query = query.offset(offset).limit(limit).order_by(Tenant.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_query)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self,
        tenant_name: str,
        products: list[str],
        tier: str = "starter",
        region: str = "us-east-1",
        db_host: str = "postgres",
        db_port: int = 5432,
    ) -> Tenant:
        slug = _slugify(tenant_name)
        db_name = f"tenant_{slug.replace('-', '_')}_db"
        db_user = f"tenant_{slug.replace('-', '_')}_user"
        now = datetime.now(timezone.utc)
        tenant = Tenant(
            id=str(uuid4()),
            tenant_name=tenant_name,
            slug=slug,
            db_name=db_name,
            db_user=db_user,
            db_host=db_host,
            db_port=db_port,
            status="provisioning",
            tier=tier,
            products=products,
            region=region,
            created_at=now,
            updated_at=now,
        )
        self._db.add(tenant)
        await self._db.flush()
        return tenant

    async def update_status(self, tenant_id: str, status: str) -> None:
        await self._db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(status=status, updated_at=datetime.now(timezone.utc))
        )

    async def update(self, tenant_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Tenant).where(Tenant.id == tenant_id).values(**fields)
        )

    async def soft_delete(self, tenant_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(status="deleted", deleted_at=now, updated_at=now)
        )


class TenantSettingsRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_tenant(self, tenant_id: str) -> TenantSettings | None:
        result = await self._db.execute(
            select(TenantSettings).where(TenantSettings.tenant_id == tenant_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: str,
        max_users: int = 50,
        max_storage_gb: int = 10,
        timezone: str = "UTC",
        locale: str = "en-US",
    ) -> TenantSettings:
        now = datetime.now(timezone.utc) if hasattr(timezone, 'utc') else datetime.now(__import__('datetime').timezone.utc)
        now = datetime.now(__import__('datetime').timezone.utc)
        settings = TenantSettings(
            id=str(uuid4()),
            tenant_id=tenant_id,
            max_users=max_users,
            max_storage_gb=max_storage_gb,
            features={},
            branding={},
            webhook_urls=[],
            timezone=timezone,
            locale=locale,
            created_at=now,
            updated_at=now,
        )
        self._db.add(settings)
        await self._db.flush()
        return settings

    async def update(self, tenant_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(__import__('datetime').timezone.utc)
        await self._db.execute(
            update(TenantSettings)
            .where(TenantSettings.tenant_id == tenant_id)
            .values(**fields)
        )


def _slugify(name: str) -> str:
    """Convert tenant name to URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    slug = re.sub(r"-+", "-", slug)
    return slug.strip("-")
