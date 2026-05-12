"""User Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone

from rainer_common.uuid_utils import uuid7

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Company, Role, User, UserRole


class CompanyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, company_id: str) -> Company | None:
        result = await self._db.execute(
            select(Company).where(Company.id == company_id, Company.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_code(self, company_code: str) -> Company | None:
        result = await self._db.execute(
            select(Company).where(Company.company_code == company_code)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Company | None:
        result = await self._db.execute(
            select(Company).where(Company.email == email, Company.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def list_companies(
        self,
        tenant_id: str | None = None,
        is_active: bool | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[Company], int]:
        query = select(Company)
        count_query = select(func.count()).select_from(Company)

        if tenant_id:
            query = query.where(Company.tenant_id == tenant_id)
            count_query = count_query.where(Company.tenant_id == tenant_id)
        if is_active is not None:
            query = query.where(Company.is_active == is_active)
            count_query = count_query.where(Company.is_active == is_active)

        query = query.offset(offset).limit(limit).order_by(Company.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_query)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self,
        tenant_id: str,
        name: str,
        email: str,
        company_code: str,
        phone: str | None = None,
        address: str | None = None,
        employee_limit: int = 10,
    ) -> Company:
        now = datetime.now(timezone.utc)
        company = Company(
            id=uuid7(),
            tenant_id=tenant_id,
            name=name,
            email=email,
            phone=phone,
            address=address,
            company_code=company_code,
            status="active",
            employee_limit=employee_limit,
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._db.add(company)
        await self._db.flush()
        return company

    async def update(self, company_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Company).where(Company.id == company_id).values(**fields)
        )

    async def set_admin(self, company_id: str, admin_id: str) -> None:
        await self._db.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(admin_id=admin_id, updated_at=datetime.now(timezone.utc))
        )

    async def deactivate(self, company_id: str) -> None:
        await self._db.execute(
            update(Company)
            .where(Company.id == company_id)
            .values(is_active=False, status="inactive", updated_at=datetime.now(timezone.utc))
        )

    async def count_active_users(self, company_id: str) -> int:
        result = await self._db.execute(
            select(func.count()).select_from(User).where(
                User.company_id == company_id, User.is_active.is_(True)
            )
        )
        return result.scalar_one()


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.id == user_id, User.is_active.is_(True))
        )
        return result.scalar_one_or_none()

    async def get_by_platform_user_id(self, platform_user_id: str) -> User | None:
        result = await self._db.execute(
            select(User).where(User.platform_user_id == platform_user_id)
        )
        return result.scalar_one_or_none()

    async def list_users(
        self,
        is_active: bool | None = None,
        department: str | None = None,
        company_id: str | None = None,
        tenant_id: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        query = select(User)
        count_query = select(func.count()).select_from(User)

        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)
        if department:
            query = query.where(User.department == department)
            count_query = count_query.where(User.department == department)
        if company_id is not None:
            query = query.where(User.company_id == company_id)
            count_query = count_query.where(User.company_id == company_id)
        if tenant_id is not None:
            query = query.where(User.tenant_id == tenant_id)
            count_query = count_query.where(User.tenant_id == tenant_id)

        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        result = await self._db.execute(query)
        count_result = await self._db.execute(count_query)
        return list(result.scalars().all()), count_result.scalar_one()

    async def create(
        self,
        platform_user_id: str,
        tenant_id: str,
        first_name: str,
        last_name: str,
        **kwargs,
    ) -> User:
        now = datetime.now(timezone.utc)
        user = User(
            id=uuid7(),
            platform_user_id=platform_user_id,
            tenant_id=tenant_id,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self._db.add(user)
        await self._db.flush()
        return user

    async def update(self, user_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(User).where(User.id == user_id).values(**fields)
        )

    async def deactivate(self, user_id: str) -> None:
        await self._db.execute(
            update(User)
            .where(User.id == user_id)
            .values(is_active=False, updated_at=datetime.now(timezone.utc))
        )


class RoleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, role_id: str) -> Role | None:
        result = await self._db.execute(select(Role).where(Role.id == role_id))
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str, company_id: str | None = None) -> Role | None:
        query = select(Role).where(Role.name == name)
        if company_id is not None:
            query = query.where(Role.company_id == company_id)
        else:
            query = query.where(Role.company_id.is_(None))
        result = await self._db.execute(query)
        return result.scalar_one_or_none()

    async def list_roles(
        self,
        product: str | None = None,
        scope: str | None = None,
        company_id: str | None = None,
    ) -> list[Role]:
        query = select(Role)
        if product:
            query = query.where(Role.product == product)
        if scope:
            query = query.where(Role.scope == scope)
        if company_id is not None:
            query = query.where(Role.company_id == company_id)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def get_default_for_scope(self, scope: str, company_id: str | None = None) -> Role | None:
        """Get the default system role for a given scope (used on user creation)."""
        query = (
            select(Role)
            .where(Role.scope == scope, Role.is_system_role.is_(True))
        )
        if company_id is not None:
            query = query.where(Role.company_id == company_id)
        else:
            query = query.where(Role.company_id.is_(None))
        result = await self._db.execute(query)
        return result.scalars().first()

    async def create(
        self,
        name: str,
        permissions: list[str],
        description: str | None = None,
        product: str | None = None,
        scope: str = "tenant",
        company_id: str | None = None,
        is_system_role: bool = False,
    ) -> Role:
        now = datetime.now(timezone.utc)
        role = Role(
            id=uuid7(),
            name=name,
            description=description,
            permissions=permissions,
            is_system_role=is_system_role,
            product=product,
            scope=scope,
            company_id=company_id,
            created_at=now,
            updated_at=now,
        )
        self._db.add(role)
        await self._db.flush()
        return role

    async def update(self, role_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(Role).where(Role.id == role_id).values(**fields)
        )


class UserRoleRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_user_roles(self, user_id: str) -> list[UserRole]:
        result = await self._db.execute(
            select(UserRole).where(UserRole.user_id == user_id)
        )
        return list(result.scalars().all())

    async def assign_role(
        self,
        user_id: str,
        role_id: str,
        granted_by: str | None = None,
    ) -> UserRole:
        existing = await self._db.execute(
            select(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
        if existing.scalar_one_or_none():
            from rainer_common.exceptions import ConflictError
            raise ConflictError("User already has this role")

        user_role = UserRole(
            id=uuid7(),
            user_id=user_id,
            role_id=role_id,
            granted_by=granted_by,
            granted_at=datetime.now(timezone.utc),
        )
        self._db.add(user_role)
        await self._db.flush()
        return user_role

    async def remove_role(self, user_id: str, role_id: str) -> None:
        from sqlalchemy import delete
        await self._db.execute(
            delete(UserRole).where(
                UserRole.user_id == user_id,
                UserRole.role_id == role_id,
            )
        )
