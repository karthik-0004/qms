"""Unit tests — UserDomainService business logic."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from rainer_common.exceptions import ConflictError, NotFoundError

from app.domain.services import UserDomainService
from app.infra.db.models import Role, User, UserRole


def make_user(**kwargs) -> User:
    defaults = dict(
        id=str(uuid4()), platform_user_id=str(uuid4()), tenant_id=str(uuid4()),
        first_name="John", last_name="Doe", display_name=None, phone=None,
        department=None, job_title=None, avatar_url=None, is_active=True,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    u = MagicMock(spec=User)
    for k, v in defaults.items():
        setattr(u, k, v)
    return u


def make_role(**kwargs) -> Role:
    defaults = dict(
        id=str(uuid4()), name="Manager", description=None, permissions=["document:read"],
        is_system_role=False, product=None,
        created_at=datetime.now(timezone.utc), updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    r = MagicMock(spec=Role)
    for k, v in defaults.items():
        setattr(r, k, v)
    return r


@pytest.fixture
def user_repo():
    return AsyncMock()


@pytest.fixture
def role_repo():
    return AsyncMock()


@pytest.fixture
def user_role_repo():
    return AsyncMock()


@pytest.fixture
def svc(user_repo, role_repo, user_role_repo):
    return UserDomainService(user_repo=user_repo, role_repo=role_repo, user_role_repo=user_role_repo)


class TestGetUser:
    @pytest.mark.asyncio
    async def test_returns_user(self, svc, user_repo):
        user = make_user()
        user_repo.get_by_id.return_value = user
        result = await svc.get_user(user.id)
        assert result.id == user.id

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, user_repo):
        user_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_user("nonexistent")


class TestCreateUser:
    @pytest.mark.asyncio
    async def test_creates_user(self, svc, user_repo):
        user_repo.get_by_platform_user_id.return_value = None
        mock_user = make_user()
        user_repo.create.return_value = mock_user
        result = await svc.create_user(
            platform_user_id=str(uuid4()), tenant_id=str(uuid4()),
            first_name="Jane", last_name="Doe"
        )
        assert result.first_name == "John"

    @pytest.mark.asyncio
    async def test_raises_conflict_if_exists(self, svc, user_repo):
        user_repo.get_by_platform_user_id.return_value = make_user()
        with pytest.raises(ConflictError):
            await svc.create_user(
                platform_user_id=str(uuid4()), tenant_id=str(uuid4()),
                first_name="Jane", last_name="Doe"
            )


class TestAssignRole:
    @pytest.mark.asyncio
    async def test_assigns_role(self, svc, user_repo, role_repo, user_role_repo):
        user = make_user()
        role = make_role()
        user_repo.get_by_id.return_value = user
        role_repo.get_by_id.return_value = role
        mock_ur = MagicMock(spec=UserRole)
        user_role_repo.assign_role.return_value = mock_ur
        result = await svc.assign_role(user.id, role.id)
        assert result is mock_ur

    @pytest.mark.asyncio
    async def test_raises_if_role_not_found(self, svc, user_repo, role_repo):
        user_repo.get_by_id.return_value = make_user()
        role_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.assign_role("user-id", "nonexistent-role-id")


class TestCreateRole:
    @pytest.mark.asyncio
    async def test_creates_new_role(self, svc, role_repo):
        role_repo.get_by_name.return_value = None
        mock_role = make_role()
        role_repo.create.return_value = mock_role
        result = await svc.create_role("NewRole", ["document:read"])
        assert result is mock_role

    @pytest.mark.asyncio
    async def test_raises_conflict_if_name_exists(self, svc, role_repo):
        role_repo.get_by_name.return_value = make_role()
        with pytest.raises(ConflictError):
            await svc.create_role("Manager", ["document:read"])
