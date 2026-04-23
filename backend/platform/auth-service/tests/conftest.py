"""Auth Service — Shared test fixtures."""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings
from app.core.database import get_db
from app.infra.db.models import Base, PlatformUser
from app.main import create_app


# ── Pytest configuration ──────────────────────────────────────────────────
pytest_plugins = ("pytest_asyncio",)


@pytest.fixture(scope="session")
def event_loop_policy():
    return asyncio.DefaultEventLoopPolicy()


# ── Test settings ─────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def test_settings() -> Settings:
    return Settings(
        rainer_env="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        redis_url="redis://localhost:6379/15",
        kafka_bootstrap_servers="localhost:9092",
        jwt_secret_key="test-secret-key-that-is-long-enough-32chars",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=15,
        jwt_refresh_token_expire_days=7,
        rainer_master_secret="test-master-secret",
        log_level="DEBUG",
        json_logs=False,
    )


# ── In-memory SQLite engine for unit tests ────────────────────────────────
@pytest_asyncio.fixture(scope="session")
async def engine(test_settings):
    _engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
    )
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield _engine
    await _engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


# ── FastAPI test client ───────────────────────────────────────────────────
@pytest_asyncio.fixture
async def app(test_settings, db_session) -> FastAPI:
    _app = create_app()
    _app.dependency_overrides[get_db] = lambda: db_session
    _app.dependency_overrides[lambda: Settings()] = lambda: test_settings
    return _app


@pytest_asyncio.fixture
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


# ── Seed data helpers ─────────────────────────────────────────────────────
@pytest_asyncio.fixture
async def test_user(db_session) -> PlatformUser:
    from app.core.security import hash_password
    user = PlatformUser(
        id=str(uuid4()),
        email="test@example.com",
        password_hash=hash_password("TestPass123!"),
        role="tenant_user",
        status="active",
        mfa_enabled=False,
        failed_attempts=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def super_admin_user(db_session) -> PlatformUser:
    from app.core.security import hash_password
    user = PlatformUser(
        id=str(uuid4()),
        email="superadmin@rainer.com",
        password_hash=hash_password("SuperAdmin123!"),
        role="super_admin",
        status="active",
        mfa_enabled=False,
        failed_attempts=0,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def auth_headers(client, test_user) -> dict[str, str]:
    """Returns Authorization headers for test_user."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "TestPass123!"},
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def admin_auth_headers(client, super_admin_user) -> dict[str, str]:
    """Returns Authorization headers for super_admin_user."""
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "superadmin@rainer.com", "password": "SuperAdmin123!"},
    )
    assert resp.status_code == 200
    token = resp.json()["data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
