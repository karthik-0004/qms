"""User Service — User and role management domain service."""

import structlog

from rainer_common.exceptions import ConflictError, NotFoundError

from ..infra.db.models import Role, User, UserRole
from ..infra.db.repositories import RoleRepository, UserRepository, UserRoleRepository

logger = structlog.get_logger(__name__)


class UserDomainService:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        user_role_repo: UserRoleRepository,
    ) -> None:
        self._users = user_repo
        self._roles = role_repo
        self._user_roles = user_role_repo

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def list_users(
        self,
        is_active: bool | None = None,
        department: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        return await self._users.list_users(
            is_active=is_active,
            department=department,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create_user(
        self,
        platform_user_id: str,
        tenant_id: str,
        first_name: str,
        last_name: str,
        **kwargs,
    ) -> User:
        existing = await self._users.get_by_platform_user_id(platform_user_id)
        if existing:
            raise ConflictError("User already exists for this platform user")

        user = await self._users.create(
            platform_user_id=platform_user_id,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            **kwargs,
        )
        logger.info("user_created", user_id=user.id, tenant_id=tenant_id)
        return user

    async def update_user(self, user_id: str, **fields) -> User:
        await self.get_user(user_id)
        await self._users.update(user_id, **fields)
        return await self.get_user(user_id)

    async def deactivate_user(self, user_id: str) -> None:
        await self.get_user(user_id)
        await self._users.deactivate(user_id)
        logger.info("user_deactivated", user_id=user_id)

    async def get_user_permissions(self, user_id: str) -> list[str]:
        user_roles = await self._user_roles.get_user_roles(user_id)
        all_permissions: set[str] = set()
        for ur in user_roles:
            role = await self._roles.get_by_id(ur.role_id)
            if role:
                if "*" in role.permissions:
                    return ["*"]
                all_permissions.update(role.permissions)
        return list(all_permissions)

    async def list_roles(self, product: str | None = None) -> list[Role]:
        return await self._roles.list_roles(product=product)

    async def create_role(
        self,
        name: str,
        permissions: list[str],
        description: str | None = None,
        product: str | None = None,
    ) -> Role:
        existing = await self._roles.get_by_name(name)
        if existing:
            raise ConflictError(f"Role '{name}' already exists")
        role = await self._roles.create(
            name=name, permissions=permissions, description=description, product=product
        )
        logger.info("role_created", role_id=role.id, name=name)
        return role

    async def update_role(self, role_id: str, **fields) -> Role:
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role", role_id)
        if role.is_system_role:
            raise ConflictError("Cannot modify system roles")
        await self._roles.update(role_id, **fields)
        return await self._roles.get_by_id(role_id)

    async def assign_role(self, user_id: str, role_id: str, granted_by: str | None = None) -> UserRole:
        await self.get_user(user_id)
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role", role_id)
        result = await self._user_roles.assign_role(user_id, role_id, granted_by)
        logger.info("role_assigned", user_id=user_id, role_id=role_id)
        return result

    async def remove_role(self, user_id: str, role_id: str) -> None:
        await self._user_roles.remove_role(user_id, role_id)
        logger.info("role_removed", user_id=user_id, role_id=role_id)
