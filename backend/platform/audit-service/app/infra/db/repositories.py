"""Audit Service — Repository layer (append-only, no updates or deletes)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PlatformAuditLog


class AuditLogRepository:
    """Append-only audit log repository. No update or delete methods."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def append(
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
        source_service: str | None = None,
        event_id: str | None = None,
    ) -> PlatformAuditLog:
        """Append a new immutable audit log entry."""
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
            source_service=source_service,
            event_id=event_id,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(log)
        await self._db.flush()
        return log

    async def query(
        self,
        tenant_id: str | None = None,
        user_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        severity: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[PlatformAuditLog], int]:
        q = select(PlatformAuditLog)
        count_q = select(func.count()).select_from(PlatformAuditLog)

        if tenant_id:
            q = q.where(PlatformAuditLog.tenant_id == tenant_id)
            count_q = count_q.where(PlatformAuditLog.tenant_id == tenant_id)
        if user_id:
            q = q.where(PlatformAuditLog.user_id == user_id)
            count_q = count_q.where(PlatformAuditLog.user_id == user_id)
        if action:
            q = q.where(PlatformAuditLog.action == action)
            count_q = count_q.where(PlatformAuditLog.action == action)
        if resource_type:
            q = q.where(PlatformAuditLog.resource_type == resource_type)
            count_q = count_q.where(PlatformAuditLog.resource_type == resource_type)
        if resource_id:
            q = q.where(PlatformAuditLog.resource_id == resource_id)
            count_q = count_q.where(PlatformAuditLog.resource_id == resource_id)
        if severity:
            q = q.where(PlatformAuditLog.severity == severity)
            count_q = count_q.where(PlatformAuditLog.severity == severity)
        if from_date:
            q = q.where(PlatformAuditLog.created_at >= from_date)
            count_q = count_q.where(PlatformAuditLog.created_at >= from_date)
        if to_date:
            q = q.where(PlatformAuditLog.created_at <= to_date)
            count_q = count_q.where(PlatformAuditLog.created_at <= to_date)

        q = q.offset(offset).limit(limit).order_by(PlatformAuditLog.created_at.desc())
        result = await self._db.execute(q)
        count_result = await self._db.execute(count_q)
        return list(result.scalars().all()), count_result.scalar_one()

    async def get_by_id(self, log_id: str) -> PlatformAuditLog | None:
        result = await self._db.execute(
            select(PlatformAuditLog).where(PlatformAuditLog.id == log_id)
        )
        return result.scalar_one_or_none()
