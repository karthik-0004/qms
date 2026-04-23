"""E2E tests — full login → refresh → logout flow for auth-service."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.security import hash_password
from app.core.database import get_db
from app.infra.db.models import Base, PlatformUser
from app.main import create_app


@pytest.fixture(scope="module")
def pg_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="module")
async def e2e_engine(pg_container):
    url = pg_container.get_connection_url().replace(
        "postgresql://", "postgresql+asyncpg://"
    )
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def e2e_session(e2e_engine) -> AsyncSession:
    factory = async_sessionmaker(e2e_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture(scope="module")
async def e2e_client(e2e_session) -> AsyncClient:
    from app.core.config import Settings
    _app = create_app()
    _app.dependency_overrides[get_db] = lambda: e2e_session
    async with AsyncClient(
        transport=ASGITransport(app=_app), base_url="http://test"
    ) as c:
        yield c


@pytest_asyncio.fixture(scope="module")
async def e2e_user(e2e_session) -> PlatformUser:
    now = datetime.now(timezone.utc)
    user = PlatformUser(
        id=str(uuid4()),
        email="e2e@example.com",
        password_hash=hash_password("E2EPassword123!"),
        role="tenant_user",
        status="active",
        mfa_enabled=False,
        failed_attempts=0,
        created_at=now,
        updated_at=now,
    )
    e2e_session.add(user)
    await e2e_session.commit()
    return user


class TestLoginRefreshLogoutFlow:
    """
    E2E vertical slice:
    login → get profile → refresh token → logout
    """

    @pytest.mark.asyncio
    async def test_full_login_flow(self, e2e_client, e2e_user):
        # Step 1: Login
        login_resp = await e2e_client.post(
            "/api/v1/auth/login",
            json={"email": "e2e@example.com", "password": "E2EPassword123!"},
        )
        assert login_resp.status_code == 200, login_resp.text
        data = login_resp.json()
        assert data["success"] is True
        access_token = data["data"]["access_token"]
        refresh_token = data["data"]["refresh_token"]
        assert access_token
        assert refresh_token
        assert data["data"]["user"]["email"] == "e2e@example.com"

        # Step 2: Refresh token
        refresh_resp = await e2e_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert refresh_resp.status_code == 200, refresh_resp.text
        new_data = refresh_resp.json()
        new_access_token = new_data["data"]["access_token"]
        new_refresh_token = new_data["data"]["refresh_token"]
        assert new_access_token != access_token
        assert new_refresh_token != refresh_token

        # Step 3: Old refresh token should no longer work (rotation)
        old_refresh_resp = await e2e_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert old_refresh_resp.status_code == 401

        # Step 4: Logout with new refresh token
        logout_resp = await e2e_client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": new_refresh_token},
        )
        assert logout_resp.status_code == 200

        # Step 5: After logout, refresh should fail
        post_logout_resp = await e2e_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": new_refresh_token},
        )
        assert post_logout_resp.status_code == 401

    @pytest.mark.asyncio
    async def test_wrong_password_increments_attempts(self, e2e_client, e2e_user):
        for i in range(3):
            resp = await e2e_client.post(
                "/api/v1/auth/login",
                json={"email": "e2e@example.com", "password": "WrongPassword!"},
            )
            assert resp.status_code == 401

    @pytest.mark.asyncio
    async def test_mfa_setup_and_verification_flow(self, e2e_client, e2e_user):
        # Login first to get token
        login = await e2e_client.post(
            "/api/v1/auth/login",
            json={"email": "e2e@example.com", "password": "E2EPassword123!"},
        )
        assert login.status_code == 200
        token = login.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Setup MFA
        setup_resp = await e2e_client.post(
            "/api/v1/auth/mfa/setup",
            headers=headers,
        )
        assert setup_resp.status_code == 200
        mfa_data = setup_resp.json()["data"]
        assert "secret" in mfa_data
        assert "provisioning_uri" in mfa_data

        # Verify MFA with correct TOTP
        import pyotp
        totp = pyotp.TOTP(mfa_data["secret"])
        code = totp.now()

        verify_resp = await e2e_client.post(
            "/api/v1/auth/mfa/verify",
            json={"code": code},
            headers=headers,
        )
        assert verify_resp.status_code == 200

        # Login should now require MFA
        login_no_mfa = await e2e_client.post(
            "/api/v1/auth/login",
            json={"email": "e2e@example.com", "password": "E2EPassword123!"},
        )
        assert login_no_mfa.status_code == 401
        assert login_no_mfa.json()["error"]["code"] == "MFA_REQUIRED"

        # Login with MFA code
        login_mfa = await e2e_client.post(
            "/api/v1/auth/login",
            json={
                "email": "e2e@example.com",
                "password": "E2EPassword123!",
                "mfa_code": totp.now(),
            },
        )
        assert login_mfa.status_code == 200
