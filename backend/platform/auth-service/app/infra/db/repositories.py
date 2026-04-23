"""Auth Service — Repository layer (data access pattern)."""

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PlatformAuditLog, PlatformUser, RefreshToken, ServiceAccessKey, Tenant


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, user_id: str) -> PlatformUser | None:
        result = await self._db.execute(
            select(PlatformUser).where(
                PlatformUser.id == user_id,
                PlatformUser.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> PlatformUser | None:
        result = await self._db.execute(
            select(PlatformUser).where(
                PlatformUser.email == email.lower().strip(),
                PlatformUser.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        password_hash: str,
        tenant_id: str | None = None,
        role: str = "tenant_user",
    ) -> PlatformUser:
        now = datetime.now(timezone.utc)
        user = PlatformUser(
            id=str(uuid4()),
            email=email.lower().strip(),
            password_hash=password_hash,
            tenant_id=tenant_id,
            role=role,
            status="active",
            mfa_enabled=False,
            failed_attempts=0,
            created_at=now,
            updated_at=now,
        )
        self._db.add(user)
        await self._db.flush()
        return user

    async def update_last_login(self, user_id: str, ip_address: str | None = None) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(PlatformUser)
            .where(PlatformUser.id == user_id)
            .values(
                last_login_at=now,
                failed_attempts=0,
                locked_until=None,
                updated_at=now,
            )
        )

    async def increment_failed_attempts(self, user_id: str) -> int:
        user = await self.get_by_id(user_id)
        if not user:
            return 0
        new_attempts = user.failed_attempts + 1
        await self._db.execute(
            update(PlatformUser)
            .where(PlatformUser.id == user_id)
            .values(failed_attempts=new_attempts, updated_at=datetime.now(timezone.utc))
        )
        return new_attempts

    async def lock_account(self, user_id: str, until: datetime) -> None:
        await self._db.execute(
            update(PlatformUser)
            .where(PlatformUser.id == user_id)
            .values(locked_until=until, updated_at=datetime.now(timezone.utc))
        )

    async def update_mfa(
        self, user_id: str, mfa_secret: str | None, enabled: bool
    ) -> None:
        await self._db.execute(
            update(PlatformUser)
            .where(PlatformUser.id == user_id)
            .values(
                mfa_secret=mfa_secret,
                mfa_enabled=enabled,
                updated_at=datetime.now(timezone.utc),
            )
        )

    async def update_password(self, user_id: str, password_hash: str) -> None:
        await self._db.execute(
            update(PlatformUser)
            .where(PlatformUser.id == user_id)
            .values(
                password_hash=password_hash,
                updated_at=datetime.now(timezone.utc),
            )
        )


class RefreshTokenRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        user_id: str,
        raw_token: str,
        expires_at: datetime,
        ip_address: str | None = None,
        device_info: dict | None = None,
    ) -> RefreshToken:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        token = RefreshToken(
            id=str(uuid4()),
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
            ip_address=ip_address,
            device_info=device_info,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(token)
        await self._db.flush()
        return token

    async def get_valid_by_hash(self, raw_token: str) -> RefreshToken | None:
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        result = await self._db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > now,
            )
        )
        return result.scalar_one_or_none()

    async def revoke(self, token_id: str) -> None:
        await self._db.execute(
            update(RefreshToken)
            .where(RefreshToken.id == token_id)
            .values(revoked_at=datetime.now(timezone.utc))
        )

    async def revoke_all_for_user(self, user_id: str) -> None:
        now = datetime.now(timezone.utc)
        await self._db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )


class AccessKeyRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        service_name: str,
        key_hash: str,
        key_prefix: str,
        scopes: list[str],
        expires_at: datetime | None = None,
    ) -> ServiceAccessKey:
        key = ServiceAccessKey(
            id=str(uuid4()),
            service_name=service_name,
            key_hash=key_hash,
            key_prefix=key_prefix,
            scopes=scopes,
            is_active=True,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(key)
        await self._db.flush()
        return key

    async def find_by_prefix(self, key_prefix: str) -> list[ServiceAccessKey]:
        result = await self._db.execute(
            select(ServiceAccessKey).where(
                ServiceAccessKey.key_prefix == key_prefix,
                ServiceAccessKey.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def revoke(self, key_id: str) -> None:
        await self._db.execute(
            update(ServiceAccessKey)
            .where(ServiceAccessKey.id == key_id)
            .values(is_active=False)
        )

    async def get_by_id(self, key_id: str) -> ServiceAccessKey | None:
        result = await self._db.execute(
            select(ServiceAccessKey).where(ServiceAccessKey.id == key_id)
        )
        return result.scalar_one_or_none()


class AuditLogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        action: str,
        tenant_id: str | None = None,
        user_id: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None,
        metadata: dict | None = None,
        severity: str = "info",
    ) -> PlatformAuditLog:
        log = PlatformAuditLog(
            id=str(uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata_=metadata or {},
            severity=severity,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(log)
        await self._db.flush()
        return log
