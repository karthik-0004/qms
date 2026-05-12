"""User Service — User, role, and company management domain service."""

import re
from uuid import uuid4

import structlog

from rainer_common.exceptions import ConflictError, NotFoundError, ValidationError

from ..infra.db.models import Company, Role, User, UserRole
from ..infra.db.repositories import (
    CompanyRepository,
    RoleRepository,
    UserRepository,
    UserRoleRepository,
)

logger = structlog.get_logger(__name__)

_COMPANY_CODE_RE = re.compile(r"^[A-Z0-9_-]{2,50}$")


def _slugify_company_code(name: str) -> str:
    """Derive a URL-safe company code from the company name."""
    slug = re.sub(r"[^A-Z0-9]+", "-", name.upper().strip())
    return slug[:50].strip("-") or "COMPANY"


class UserDomainService:
    def __init__(
        self,
        user_repo: UserRepository,
        role_repo: RoleRepository,
        user_role_repo: UserRoleRepository,
        company_repo: CompanyRepository | None = None,
    ) -> None:
        self._users = user_repo
        self._roles = role_repo
        self._user_roles = user_role_repo
        self._companies = company_repo

    # ── Users ────────────────────────────────────────────────────────────

    async def get_user(self, user_id: str) -> User:
        user = await self._users.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return user

    async def list_users(
        self,
        is_active: bool | None = None,
        department: str | None = None,
        company_id: str | None = None,
        tenant_id: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[User], int]:
        return await self._users.list_users(
            is_active=is_active,
            department=department,
            company_id=company_id,
            tenant_id=tenant_id,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create_user(
        self,
        platform_user_id: str,
        tenant_id: str,
        first_name: str,
        last_name: str,
        company_id: str | None = None,
        **kwargs,
    ) -> User:
        existing = await self._users.get_by_platform_user_id(platform_user_id)
        if existing:
            raise ConflictError("User already exists for this platform user")

        if company_id and self._companies:
            company = await self._companies.get_by_id(company_id)
            if not company:
                raise NotFoundError("Company", company_id)
            active_count = await self._companies.count_active_users(company_id)
            if active_count >= company.employee_limit:
                raise ValidationError(
                    f"Company has reached its employee limit of {company.employee_limit}"
                )

        user = await self._users.create(
            platform_user_id=platform_user_id,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            company_id=company_id,
            **kwargs,
        )
        logger.info("user_created", user_id=user.id, tenant_id=tenant_id, company_id=company_id)
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

    # ── Roles ────────────────────────────────────────────────────────────

    async def list_roles(
        self,
        product: str | None = None,
        scope: str | None = None,
        company_id: str | None = None,
    ) -> list[Role]:
        return await self._roles.list_roles(product=product, scope=scope, company_id=company_id)

    async def create_role(
        self,
        name: str,
        permissions: list[str],
        description: str | None = None,
        product: str | None = None,
        scope: str = "tenant",
        company_id: str | None = None,
    ) -> Role:
        existing = await self._roles.get_by_name(name, company_id=company_id)
        if existing:
            raise ConflictError(f"Role '{name}' already exists")
        role = await self._roles.create(
            name=name,
            permissions=permissions,
            description=description,
            product=product,
            scope=scope,
            company_id=company_id,
        )
        logger.info("role_created", role_id=role.id, name=name, scope=scope)
        return role

    async def update_role(self, role_id: str, **fields) -> Role:
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role", role_id)
        if role.is_system_role:
            raise ConflictError("Cannot modify system roles")
        await self._roles.update(role_id, **fields)
        return await self._roles.get_by_id(role_id)

    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        granted_by: str | None = None,
        caller_company_id: str | None = None,
    ) -> UserRole:
        await self.get_user(user_id)
        role = await self._roles.get_by_id(role_id)
        if not role:
            raise NotFoundError("Role", role_id)

        # Company admins can only assign company-scoped roles for their own company
        if caller_company_id and role.scope == "company" and role.company_id != caller_company_id:
            from rainer_common.exceptions import ForbiddenError
            raise ForbiddenError("Cannot assign roles from another company")

        result = await self._user_roles.assign_role(user_id, role_id, granted_by)
        logger.info("role_assigned", user_id=user_id, role_id=role_id)
        return result

    async def remove_role(self, user_id: str, role_id: str) -> None:
        await self._user_roles.remove_role(user_id, role_id)
        logger.info("role_removed", user_id=user_id, role_id=role_id)

    # ── Companies ─────────────────────────────────────────────────────────

    def _require_company_repo(self) -> CompanyRepository:
        if not self._companies:
            raise RuntimeError("CompanyRepository not injected")
        return self._companies

    async def get_company(self, company_id: str) -> Company:
        repo = self._require_company_repo()
        company = await repo.get_by_id(company_id)
        if not company:
            raise NotFoundError("Company", company_id)
        return company

    async def list_companies(
        self,
        tenant_id: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Company], int]:
        repo = self._require_company_repo()
        return await repo.list_companies(
            tenant_id=tenant_id,
            is_active=is_active,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create_company(
        self,
        tenant_id: str,
        name: str,
        email: str,
        phone: str | None = None,
        address: str | None = None,
        company_code: str | None = None,
        employee_limit: int = 10,
    ) -> Company:
        repo = self._require_company_repo()

        existing_email = await repo.get_by_email(email)
        if existing_email:
            raise ConflictError(f"A company with email '{email}' already exists")

        code = company_code or _slugify_company_code(name)
        existing_code = await repo.get_by_code(code)
        if existing_code:
            code = f"{code}-{str(uuid4())[:8].upper()}"

        company = await repo.create(
            tenant_id=tenant_id,
            name=name,
            email=email,
            phone=phone,
            address=address,
            company_code=code,
            employee_limit=employee_limit,
        )
        logger.info("company_created", company_id=company.id, tenant_id=tenant_id)
        return company

    async def update_company(self, company_id: str, **fields) -> Company:
        repo = self._require_company_repo()
        await self.get_company(company_id)
        await repo.update(company_id, **fields)
        return await self.get_company(company_id)

    async def deactivate_company(self, company_id: str) -> None:
        repo = self._require_company_repo()
        await self.get_company(company_id)
        await repo.deactivate(company_id)
        logger.info("company_deactivated", company_id=company_id)

    async def set_company_admin(self, company_id: str, user_id: str) -> None:
        repo = self._require_company_repo()
        await self.get_company(company_id)
        await repo.set_admin(company_id, user_id)
