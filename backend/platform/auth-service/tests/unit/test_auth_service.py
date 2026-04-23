"""Unit tests — AuthDomainService business logic."""

from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio

from rainer_common.exceptions import (
    ConflictError,
    ForbiddenError,
    InvalidTokenError,
    MFARequiredError,
    UnauthorizedError,
)

from app.core.config import Settings
from app.core.security import hash_password
from app.domain.services import AuthDomainService
from app.infra.db.models import PlatformUser, RefreshToken


# ── Helpers ───────────────────────────────────────────────────────────────

def make_user(**kwargs) -> PlatformUser:
    defaults = dict(
        id=str(uuid4()),
        email="user@example.com",
        password_hash=hash_password("TestPass123!"),
        tenant_id=str(uuid4()),
        role="tenant_user",
        status="active",
        mfa_enabled=False,
        mfa_secret=None,
        failed_attempts=0,
        locked_until=None,
        last_login_at=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    user = MagicMock(spec=PlatformUser)
    for k, v in defaults.items():
        setattr(user, k, v)
    return user


def make_settings() -> Settings:
    return Settings(
        rainer_env="testing",
        jwt_secret_key="test-secret-32chars-minimum-length",
        jwt_algorithm="HS256",
        jwt_access_token_expire_minutes=15,
        jwt_refresh_token_expire_days=7,
        rainer_master_secret="test-master",
        max_failed_login_attempts=5,
        account_lockout_minutes=30,
        mfa_issuer_name="TestIssuer",
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def token_repo():
    return AsyncMock()


@pytest.fixture
def key_repo():
    return AsyncMock()


@pytest.fixture
def audit_repo():
    return AsyncMock()


@pytest.fixture
def svc(user_repo, token_repo, key_repo, audit_repo):
    return AuthDomainService(
        user_repo=user_repo,
        token_repo=token_repo,
        key_repo=key_repo,
        audit_repo=audit_repo,
        settings=make_settings(),
    )


# ── Login tests ───────────────────────────────────────────────────────────
class TestLogin:
    @pytest.mark.asyncio
    async def test_successful_login_returns_tokens(self, svc, user_repo, token_repo, audit_repo):
        user = make_user()
        user_repo.get_by_email.return_value = user
        token_repo.create.return_value = MagicMock()
        user_repo.update_last_login.return_value = None
        audit_repo.create.return_value = MagicMock()

        result = await svc.login("user@example.com", "TestPass123!")

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"
        assert result["user"]["email"] == "user@example.com"
        token_repo.create.assert_called_once()
        audit_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_not_found_raises_unauthorized(self, svc, user_repo):
        user_repo.get_by_email.return_value = None
        with pytest.raises(UnauthorizedError, match="Invalid email or password"):
            await svc.login("notexist@example.com", "pass")

    @pytest.mark.asyncio
    async def test_login_wrong_password_raises_unauthorized(self, svc, user_repo):
        user = make_user()
        user_repo.get_by_email.return_value = user
        user_repo.increment_failed_attempts.return_value = 1
        with pytest.raises(UnauthorizedError, match="Invalid email or password"):
            await svc.login("user@example.com", "WrongPassword!")

    @pytest.mark.asyncio
    async def test_login_locked_account_raises_forbidden(self, svc, user_repo):
        user = make_user(
            locked_until=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        user_repo.get_by_email.return_value = user
        with pytest.raises(ForbiddenError, match="locked"):
            await svc.login("user@example.com", "TestPass123!")

    @pytest.mark.asyncio
    async def test_login_inactive_account_raises_forbidden(self, svc, user_repo):
        user = make_user(status="inactive")
        user_repo.get_by_email.return_value = user
        with pytest.raises(ForbiddenError, match="not active"):
            await svc.login("user@example.com", "TestPass123!")

    @pytest.mark.asyncio
    async def test_login_mfa_required_when_enabled(self, svc, user_repo):
        user = make_user(mfa_enabled=True)
        user_repo.get_by_email.return_value = user
        with pytest.raises(MFARequiredError):
            await svc.login("user@example.com", "TestPass123!")

    @pytest.mark.asyncio
    async def test_login_lockout_on_max_attempts(self, svc, user_repo, audit_repo):
        user = make_user()
        user_repo.get_by_email.return_value = user
        user_repo.increment_failed_attempts.return_value = 5
        audit_repo.create.return_value = MagicMock()
        user_repo.lock_account.return_value = None

        with pytest.raises(ForbiddenError, match="locked"):
            await svc.login("user@example.com", "WrongPass!")

        user_repo.lock_account.assert_called_once()


# ── Refresh token tests ───────────────────────────────────────────────────
class TestRefreshTokens:
    @pytest.mark.asyncio
    async def test_successful_refresh_returns_new_tokens(self, svc, user_repo, token_repo):
        user = make_user()
        token = MagicMock(spec=RefreshToken)
        token.id = str(uuid4())
        token.user_id = user.id

        token_repo.get_valid_by_hash.return_value = token
        user_repo.get_by_id.return_value = user
        token_repo.revoke.return_value = None
        token_repo.create.return_value = MagicMock()

        result = await svc.refresh_tokens("valid-token")

        assert "access_token" in result
        assert "refresh_token" in result
        token_repo.revoke.assert_called_once_with(token.id)

    @pytest.mark.asyncio
    async def test_invalid_refresh_token_raises(self, svc, token_repo):
        token_repo.get_valid_by_hash.return_value = None
        with pytest.raises(InvalidTokenError):
            await svc.refresh_tokens("invalid-token")


# ── MFA tests ─────────────────────────────────────────────────────────────
class TestMFA:
    @pytest.mark.asyncio
    async def test_setup_mfa_returns_qr_data(self, svc, user_repo):
        user = make_user(mfa_enabled=False, mfa_secret=None)
        user_repo.get_by_id.return_value = user
        user_repo.update_mfa.return_value = None

        result = await svc.setup_mfa(user.id)

        assert "secret" in result
        assert "provisioning_uri" in result
        assert "qr_code_url" in result

    @pytest.mark.asyncio
    async def test_setup_mfa_fails_if_already_enabled(self, svc, user_repo):
        user = make_user(mfa_enabled=True)
        user_repo.get_by_id.return_value = user
        with pytest.raises(ConflictError):
            await svc.setup_mfa(user.id)

    @pytest.mark.asyncio
    async def test_disable_mfa_requires_correct_password(self, svc, user_repo):
        user = make_user(mfa_enabled=True)
        user_repo.get_by_id.return_value = user
        with pytest.raises(UnauthorizedError):
            await svc.disable_mfa(user.id, "WrongPassword!")


# ── Access key tests ──────────────────────────────────────────────────────
class TestAccessKeys:
    @pytest.mark.asyncio
    async def test_create_access_key_returns_raw_key(self, svc, key_repo):
        key_mock = MagicMock()
        key_mock.id = str(uuid4())
        key_repo.create.return_value = key_mock

        result = await svc.create_access_key("test-service", ["read"])

        assert "raw_key" in result
        assert result["raw_key"].startswith("rsk_")
        assert "warning" in result
        key_repo.create.assert_called_once()
