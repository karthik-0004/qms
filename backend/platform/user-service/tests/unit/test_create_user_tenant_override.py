"""Unit tests — super_admin provisioning tenant_id on create."""

import pytest

from app.schemas.requests import CreateUserRequest


def test_create_user_request_accepts_optional_tenant_id():
    payload = CreateUserRequest(
        platform_user_id="00000000-0000-0000-0000-000000000001",
        tenant_id="00000000-0000-0000-0000-000000000002",
        first_name="A",
        last_name="B",
    )
    assert payload.tenant_id == "00000000-0000-0000-0000-000000000002"
