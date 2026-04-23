"""Audit Service — Core audit domain service (append-only compliance log)."""

from datetime import datetime

import structlog

from rainer_common.exceptions import NotFoundError

from ..infra.db.models import PlatformAuditLog
from ..infra.db.repositories import AuditLogRepository

logger = structlog.get_logger(__name__)


class AuditDomainService:
    """Immutable audit trail management — append-only, no updates, no deletes."""

    def __init__(self, repo: AuditLogRepository) -> None:
        self._repo = repo

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
        """Append an immutable audit log entry."""
        log = await self._repo.append(
            action=action,
            tenant_id=tenant_id,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata,
            severity=severity,
            source_service=source_service,
            event_id=event_id,
        )
        logger.info("audit_log_appended", action=action, tenant_id=tenant_id, log_id=log.id)
        return log

    async def query_logs(
        self,
        tenant_id: str | None = None,
        user_id: str | None = None,
        action: str | None = None,
        resource_type: str | None = None,
        resource_id: str | None = None,
        severity: str | None = None,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> tuple[list[PlatformAuditLog], int]:
        return await self._repo.query(
            tenant_id=tenant_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            severity=severity,
            from_date=from_date,
            to_date=to_date,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def get_log(self, log_id: str) -> PlatformAuditLog:
        log = await self._repo.get_by_id(log_id)
        if not log:
            raise NotFoundError("AuditLog", log_id)
        return log

    async def process_kafka_event(self, event: dict) -> None:
        """Process an incoming domain event from Kafka and create an audit entry."""
        await self.append(
            action=event.get("event_type", "UNKNOWN"),
            tenant_id=event.get("tenant_id"),
            user_id=event.get("actor_id"),
            metadata=event.get("payload", {}),
            source_service=event.get("source_service"),
            event_id=event.get("event_id"),
        )
