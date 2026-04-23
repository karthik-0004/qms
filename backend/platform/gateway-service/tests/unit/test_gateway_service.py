"""Unit tests — GatewayDomainService business logic."""

import pytest

from rainer_auth_lib.jwt import JWTSettings, create_access_token
from rainer_common.exceptions import UnauthorizedError

from app.domain.services import GatewayDomainService


@pytest.fixture
def jwt_settings():
    return JWTSettings(
        secret_key="test-secret-key-that-is-long-enough-32chars",
        algorithm="HS256",
        access_token_expire_minutes=15,
        refresh_token_expire_days=7,
    )


@pytest.fixture
def svc(jwt_settings):
    return GatewayDomainService(jwt_settings=jwt_settings)


class TestExtractBearerToken:
    def test_extracts_token(self, svc):
        result = svc.extract_bearer_token("Bearer mytoken123")
        assert result == "mytoken123"

    def test_returns_none_for_missing_header(self, svc):
        assert svc.extract_bearer_token(None) is None

    def test_returns_none_for_non_bearer(self, svc):
        assert svc.extract_bearer_token("Basic dXNlcjpwYXNz") is None

    def test_returns_none_for_empty_string(self, svc):
        assert svc.extract_bearer_token("") is None

    def test_case_insensitive_bearer(self, svc):
        result = svc.extract_bearer_token("bearer token123")
        assert result == "token123"


class TestValidateToken:
    def test_validates_valid_token(self, svc, jwt_settings):
        from uuid import uuid4
        token, _ = create_access_token(
            subject=str(uuid4()),
            email="user@test.com",
            settings=jwt_settings,
            tenant_id=str(uuid4()),
            role="tenant_admin",
        )
        payload = svc.validate_token(token)
        assert payload["email"] == "user@test.com"
        assert payload["role"] == "tenant_admin"

    def test_raises_for_invalid_token(self, svc):
        with pytest.raises(UnauthorizedError):
            svc.validate_token("invalid.token.here")

    def test_raises_for_expired_token(self, svc, jwt_settings):
        from datetime import timedelta
        from uuid import uuid4
        token, _ = create_access_token(
            subject=str(uuid4()),
            email="u@e.com",
            settings=jwt_settings,
            expires_delta=timedelta(seconds=-1),
        )
        with pytest.raises(UnauthorizedError, match="expired"):
            svc.validate_token(token)


class TestBuildUpstreamHeaders:
    def test_builds_headers_with_all_fields(self, svc):
        payload = {
            "user_id": "user-1",
            "tenant_id": "tenant-1",
            "role": "tenant_admin",
            "permissions": ["document:read"],
        }
        headers = svc.build_upstream_headers(payload)
        assert headers["X-Tenant-ID"] == "tenant-1"
        assert headers["X-User-ID"] == "user-1"
        assert headers["X-User-Role"] == "tenant_admin"

    def test_omits_none_fields(self, svc):
        payload = {"user_id": "user-1", "tenant_id": None, "role": None}
        headers = svc.build_upstream_headers(payload)
        assert "X-Tenant-ID" not in headers
        assert "X-User-Role" not in headers
        assert "X-User-ID" in headers
