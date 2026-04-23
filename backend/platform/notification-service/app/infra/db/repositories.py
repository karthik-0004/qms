"""Notification Service — Repository layer."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import NotificationLog, NotificationTemplate


class NotificationTemplateRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_name(self, name: str) -> NotificationTemplate | None:
        result = await self._db.execute(
            select(NotificationTemplate).where(
                NotificationTemplate.name == name,
                NotificationTemplate.is_active.is_(True),
            )
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[NotificationTemplate]:
        result = await self._db.execute(select(NotificationTemplate))
        return list(result.scalars().all())

    async def create(
        self,
        name: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        channel: str = "email",
        variables: list[str] | None = None,
    ) -> NotificationTemplate:
        now = datetime.now(timezone.utc)
        template = NotificationTemplate(
            id=str(uuid4()),
            name=name,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            channel=channel,
            variables=variables or [],
            is_active=True,
            created_at=now,
            updated_at=now,
        )
        self._db.add(template)
        await self._db.flush()
        return template


class NotificationLogRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(
        self,
        channel: str,
        tenant_id: str | None = None,
        user_id: str | None = None,
        recipient_email: str | None = None,
        template_name: str | None = None,
        subject: str | None = None,
        metadata: dict | None = None,
    ) -> NotificationLog:
        now = datetime.now(timezone.utc)
        log = NotificationLog(
            id=str(uuid4()),
            tenant_id=tenant_id,
            user_id=user_id,
            recipient_email=recipient_email,
            template_name=template_name,
            subject=subject,
            channel=channel,
            status="pending",
            metadata_=metadata or {},
            created_at=now,
        )
        self._db.add(log)
        await self._db.flush()
        return log

    async def mark_sent(self, log_id: str) -> None:
        await self._db.execute(
            update(NotificationLog)
            .where(NotificationLog.id == log_id)
            .values(status="sent", sent_at=datetime.now(timezone.utc))
        )

    async def mark_failed(self, log_id: str, error: str) -> None:
        await self._db.execute(
            update(NotificationLog)
            .where(NotificationLog.id == log_id)
            .values(status="failed", error_message=error)
        )
