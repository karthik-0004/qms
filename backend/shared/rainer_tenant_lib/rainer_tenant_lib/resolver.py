"""Rainer Tenant Lib — Tenant resolver with connection pool management."""

import asyncio
from dataclasses import dataclass
from typing import Any

import structlog
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .credentials import TenantCredentials, derive_tenant_password

logger = structlog.get_logger(__name__)


@dataclass
class TenantConfig:
    tenant_id: str
    tenant_name: str
    db_name: str
    db_user: str
    db_host: str
    db_port: int
    status: str
    products: list[str]


class TenantResolver:
    """
    Resolves tenant DB credentials and manages per-tenant connection pools.

    - Credentials are derived on the fly (never stored)
    - Maintains a pool of SQLAlchemy engines keyed by tenant_id
    - Caches tenant config in Redis (if available)
    """

    def __init__(
        self,
        master_session_factory: async_sessionmaker,
        master_secret: str,
        redis_client: Any | None = None,
        cache_ttl_seconds: int = 300,
        pool_size: int = 5,
        max_overflow: int = 10,
    ) -> None:
        self._master_session_factory = master_session_factory
        self._master_secret = master_secret
        self._redis = redis_client
        self._cache_ttl = cache_ttl_seconds
        self._pool_size = pool_size
        self._max_overflow = max_overflow
        self._engines: dict[str, AsyncEngine] = {}
        self._session_factories: dict[str, async_sessionmaker] = {}
        self._lock = asyncio.Lock()

    async def resolve(self, tenant_id: str) -> TenantConfig:
        """Resolve tenant config from cache or Master DB."""
        cached = await self._get_cached_config(tenant_id)
        if cached:
            return cached

        config = await self._load_from_master(tenant_id)
        await self._cache_config(tenant_id, config)
        return config

    async def get_credentials(self, tenant_id: str) -> TenantCredentials:
        """Get derived DB credentials for a tenant."""
        config = await self.resolve(tenant_id)
        password = derive_tenant_password(tenant_id, self._master_secret)
        return TenantCredentials(
            db_name=config.db_name,
            db_user=config.db_user,
            db_password=password,
            db_host=config.db_host,
            db_port=config.db_port,
        )

    async def get_session(self, tenant_id: str) -> AsyncSession:
        """Get an async DB session scoped to the tenant DB."""
        factory = await self._get_or_create_session_factory(tenant_id)
        return factory()

    async def invalidate_cache(self, tenant_id: str) -> None:
        """Invalidate cached tenant config (call on tenant update)."""
        if self._redis:
            await self._redis.delete(f"rainer:tenant:config:{tenant_id}")

        async with self._lock:
            if tenant_id in self._engines:
                await self._engines[tenant_id].dispose()
                del self._engines[tenant_id]
                del self._session_factories[tenant_id]

    async def get_pool_stats(self) -> dict[str, dict[str, int]]:
        """Return connection pool statistics per tenant."""
        stats: dict[str, dict[str, int]] = {}
        for tenant_id, engine in self._engines.items():
            pool = engine.pool
            stats[tenant_id] = {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
            }
        return stats

    async def close_all(self) -> None:
        """Dispose all tenant engines on shutdown."""
        async with self._lock:
            for engine in self._engines.values():
                await engine.dispose()
            self._engines.clear()
            self._session_factories.clear()

    async def _get_or_create_session_factory(self, tenant_id: str) -> async_sessionmaker:
        if tenant_id in self._session_factories:
            return self._session_factories[tenant_id]

        async with self._lock:
            if tenant_id in self._session_factories:
                return self._session_factories[tenant_id]

            creds = await self.get_credentials(tenant_id)
            engine = create_async_engine(
                creds.dsn,
                pool_size=self._pool_size,
                max_overflow=self._max_overflow,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False,
            )
            factory = async_sessionmaker(
                engine,
                expire_on_commit=False,
                class_=AsyncSession,
            )
            self._engines[tenant_id] = engine
            self._session_factories[tenant_id] = factory

            logger.info("tenant_pool_created", tenant_id=tenant_id, db_name=creds.db_name)
            return factory

    async def _load_from_master(self, tenant_id: str) -> TenantConfig:
        """Query Master DB for tenant config."""
        from sqlalchemy import text

        async with self._master_session_factory() as session:
            result = await session.execute(
                text(
                    "SELECT id, tenant_name, db_name, db_user, db_host, db_port, "
                    "status, products FROM tenants WHERE id = :tenant_id AND deleted_at IS NULL"
                ),
                {"tenant_id": tenant_id},
            )
            row = result.fetchone()

        if not row:
            from rainer_common.exceptions import TenantNotFoundError

            raise TenantNotFoundError(tenant_id)

        if row.status == "suspended":
            from rainer_common.exceptions import TenantSuspendedError

            raise TenantSuspendedError()

        return TenantConfig(
            tenant_id=str(row.id),
            tenant_name=row.tenant_name,
            db_name=row.db_name,
            db_user=row.db_user,
            db_host=row.db_host,
            db_port=row.db_port,
            status=row.status,
            products=row.products or [],
        )

    async def _get_cached_config(self, tenant_id: str) -> TenantConfig | None:
        if not self._redis:
            return None
        import json

        raw = await self._redis.get(f"rainer:tenant:config:{tenant_id}")
        if raw:
            data = json.loads(raw)
            return TenantConfig(**data)
        return None

    async def _cache_config(self, tenant_id: str, config: TenantConfig) -> None:
        if not self._redis:
            return
        import dataclasses
        import json

        await self._redis.setex(
            f"rainer:tenant:config:{tenant_id}",
            self._cache_ttl,
            json.dumps(dataclasses.asdict(config)),
        )

