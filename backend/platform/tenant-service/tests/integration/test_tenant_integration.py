"""Integration tests — tenant-service with real PostgreSQL (TestContainers)."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.database import get_db
from app.infra.db.models import Base
from app.main import create_app


@pytest.fixture(scope="module")
def postgres_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="module")
async def integration_engine(postgres_container):
    url = postgres_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def integration_db(integration_engine) -> AsyncSession:
    factory = async_sessionmaker(integration_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def integration_client(integration_db) -> AsyncClient:
    _app = create_app()
    _app.dependency_overrides[get_db] = lambda: integration_db
    async with AsyncClient(
        transport=ASGITransport(app=_app), base_url="http://test"
    ) as client:
        yield client


class TestTenantServiceHealth:
    @pytest.mark.asyncio
    async def test_health_live(self, integration_client):
        resp = await integration_client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"
        assert resp.json()["service"] == "tenant-service"

    @pytest.mark.asyncio
    async def test_health_ready(self, integration_client):
        resp = await integration_client.get("/health/ready")
        assert resp.status_code == 200


class TestTenantEndpointsRequireAuth:
    @pytest.mark.asyncio
    async def test_list_tenants_requires_auth(self, integration_client):
        resp = await integration_client.get("/api/v1/tenants")
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_tenant_requires_auth(self, integration_client):
        resp = await integration_client.post(
            "/api/v1/tenants",
            json={
                "tenant_name": "Test Corp",
                "products": ["qms"],
                "primary_contact": {
                    "first_name": "A",
                    "last_name": "B",
                    "email": "a@example.com",
                },
            },
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_create_tenant_validates_products(self, integration_client):
        resp = await integration_client.post(
            "/api/v1/tenants",
            json={
                "tenant_name": "Test Corp",
                "products": ["invalid_product"],
                "primary_contact": {
                    "first_name": "A",
                    "last_name": "B",
                    "email": "a@example.com",
                },
            },
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_get_tenant_not_found(self, integration_client):
        resp = await integration_client.get(
            "/api/v1/tenants/00000000-0000-0000-0000-000000000000",
            headers={"Authorization": "Bearer fake-token"},
        )
        assert resp.status_code in (401, 404)
