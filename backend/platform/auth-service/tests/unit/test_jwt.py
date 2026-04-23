"""Unit tests — JWT creation and verification."""

from datetime import timedelta

import pytest

from rainer_auth_lib.jwt import (
    JWTSettings,
    create_access_token,
    create_refresh_token,
    verify_token,
)
from rainer_common.exceptions import InvalidTokenError


@pytest.fixture
def jwt_settings():
    return JWTSettings(
        secret_key="test-secret-key-that-is-long-enough-32chars",
        algorithm="HS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


class TestCreateAccessToken:
    def test_creates_valid_token(self, jwt_settings):
        token, jti = create_access_token(
            subject="user-123",
            email="user@example.com",
            settings=jwt_settings,
            tenant_id="tenant-456",
            role="tenant_admin",
        )
        assert isinstance(token, str)
        assert len(token) > 0
        assert isinstance(jti, str)

    def test_payload_contains_correct_fields(self, jwt_settings):
        token, _ = create_access_token(
            subject="user-123",
            email="user@example.com",
            settings=jwt_settings,
            tenant_id="tenant-456",
            role="tenant_admin",
            permissions=["document:read"],
            product_access=["qms"],
        )
        payload = verify_token(token, jwt_settings)
        assert payload.sub == "user-123"
        assert payload.email == "user@example.com"
        assert payload.tenant_id == "tenant-456"
        assert payload.role == "tenant_admin"
        assert "document:read" in payload.permissions
        assert "qms" in payload.product_access
        assert payload.type == "access"

    def test_token_has_unique_jti(self, jwt_settings):
        _, jti1 = create_access_token("u1", "u1@e.com", jwt_settings)
        _, jti2 = create_access_token("u2", "u2@e.com", jwt_settings)
        assert jti1 != jti2

    def test_custom_expiry(self, jwt_settings):
        token, _ = create_access_token(
            subject="u", email="u@e.com", settings=jwt_settings,
            expires_delta=timedelta(hours=1)
        )
        payload = verify_token(token, jwt_settings)
        assert payload.exp - payload.iat >= 3590  # ~1 hour


class TestCreateRefreshToken:
    def test_creates_valid_token(self, jwt_settings):
        token, jti = create_refresh_token(subject="user-123", settings=jwt_settings)
        assert isinstance(token, str)
        assert isinstance(jti, str)

    def test_refresh_token_type(self, jwt_settings):
        token, _ = create_refresh_token(subject="user-123", settings=jwt_settings)
        payload = verify_token(token, jwt_settings)
        assert payload.type == "refresh"
        assert payload.sub == "user-123"


class TestVerifyToken:
    def test_valid_token_verifies(self, jwt_settings):
        token, _ = create_access_token("u", "u@e.com", jwt_settings)
        payload = verify_token(token, jwt_settings)
        assert payload.sub == "u"

    def test_expired_token_raises(self, jwt_settings):
        token, _ = create_access_token(
            "u", "u@e.com", jwt_settings,
            expires_delta=timedelta(seconds=-1)
        )
        with pytest.raises(InvalidTokenError, match="expired"):
            verify_token(token, jwt_settings)

    def test_tampered_token_raises(self, jwt_settings):
        token, _ = create_access_token("u", "u@e.com", jwt_settings)
        tampered = token[:-5] + "XXXXX"
        with pytest.raises(InvalidTokenError):
            verify_token(tampered, jwt_settings)

    def test_wrong_secret_raises(self, jwt_settings):
        token, _ = create_access_token("u", "u@e.com", jwt_settings)
        wrong_settings = JWTSettings(
            secret_key="completely-different-secret-key-here",
            algorithm="HS256",
        )
        with pytest.raises(InvalidTokenError):
            verify_token(token, wrong_settings)
