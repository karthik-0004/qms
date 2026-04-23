"""User Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Role, User, UserRole


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
            id=str(uuid4()),
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

    async def get_by_name(self, name: str) -> Role | None:
        result = await self._db.execute(select(Role).where(Role.name == name))
        return result.scalar_one_or_none()

    async def list_roles(self, product: str | None = None) -> list[Role]:
        query = select(Role)
        if product:
            query = query.where(Role.product == product)
        result = await self._db.execute(query)
        return list(result.scalars().all())

    async def create(
        self,
        name: str,
        permissions: list[str],
        description: str | None = None,
        product: str | None = None,
    ) -> Role:
        now = datetime.now(timezone.utc)
        role = Role(
            id=str(uuid4()),
            name=name,
            description=description,
            permissions=permissions,
            is_system_role=False,
            product=product,
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
            id=str(uuid4()),
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
