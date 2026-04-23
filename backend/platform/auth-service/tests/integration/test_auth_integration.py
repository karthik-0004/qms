"""Integration tests — auth-service with real PostgreSQL (TestContainers)."""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.config import Settings
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
    settings = Settings(
        rainer_env="testing",
        database_url="placeholder",
        jwt_secret_key="integration-test-secret-32chars-min",
        rainer_master_secret="integration-master",
    )
    _app = create_app()
    _app.dependency_overrides[get_db] = lambda: integration_db

    async with AsyncClient(
        transport=ASGITransport(app=_app), base_url="http://test"
    ) as client:
        yield client


class TestLoginIntegration:
    @pytest.mark.asyncio
    async def test_login_nonexistent_user_returns_401(self, integration_client):
        resp = await integration_client.post(
            "/api/v1/auth/login",
            json={"email": "nobody@example.com", "password": "SomePass123!"},
        )
        assert resp.status_code == 401
        assert resp.json()["success"] is False
        assert resp.json()["error"]["code"] == "UNAUTHORIZED"

    @pytest.mark.asyncio
    async def test_health_live_returns_ok(self, integration_client):
        resp = await integration_client.get("/health/live")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_health_ready_checks_db(self, integration_client):
        resp = await integration_client.get("/health/ready")
        assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token_returns_401(self, integration_client):
        resp = await integration_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid.refresh.token"},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_login_missing_fields_returns_422(self, integration_client):
        resp = await integration_client.post(
            "/api/v1/auth/login",
            json={"email": "not-an-email"},
        )
        assert resp.status_code == 422
        assert resp.json()["error"]["code"] == "VALIDATION_ERROR"


class TestAccessKeyIntegration:
    @pytest.mark.asyncio
    async def test_create_access_key_requires_auth(self, integration_client):
        resp = await integration_client.post(
            "/api/v1/auth/access-keys",
            json={"service_name": "test-service", "scopes": ["read"]},
        )
        assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_revoke_access_key_requires_auth(self, integration_client):
        resp = await integration_client.delete(
            "/api/v1/auth/access-keys/some-key-id",
        )
        assert resp.status_code == 401
