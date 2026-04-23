"""Notification Service — Multi-channel notification domain service."""

import asyncio
from datetime import datetime, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Any
from uuid import uuid4

import aiosmtplib
import structlog

from ..core.config import Settings
from ..infra.db.models import NotificationLog
from ..infra.db.repositories import NotificationLogRepository, NotificationTemplateRepository

logger = structlog.get_logger(__name__)


class NotificationDomainService:
    def __init__(
        self,
        template_repo: NotificationTemplateRepository,
        log_repo: NotificationLogRepository,
        settings: Settings,
    ) -> None:
        self._templates = template_repo
        self._logs = log_repo
        self._settings = settings

    async def send_email(
        self,
        recipient_email: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        tenant_id: str | None = None,
        user_id: str | None = None,
        template_name: str | None = None,
        metadata: dict | None = None,
    ) -> NotificationLog:
        """Send an email notification."""
        log = await self._logs.create(
            tenant_id=tenant_id,
            user_id=user_id,
            recipient_email=recipient_email,
            template_name=template_name,
            subject=subject,
            channel="email",
            metadata=metadata,
        )

        try:
            await self._send_smtp(recipient_email, subject, body_html, body_text)
            await self._logs.mark_sent(log.id)
            logger.info("email_sent", recipient=recipient_email, template=template_name)
        except Exception as exc:
            await self._logs.mark_failed(log.id, str(exc))
            logger.error("email_send_failed", recipient=recipient_email, error=str(exc))

        return log

    async def send_from_template(
        self,
        template_name: str,
        recipient_email: str,
        variables: dict[str, Any],
        tenant_id: str | None = None,
        user_id: str | None = None,
    ) -> NotificationLog:
        """Render a template and send the notification."""
        template = await self._templates.get_by_name(template_name)
        if not template:
            from rainer_common.exceptions import NotFoundError
            raise NotFoundError("NotificationTemplate", template_name)

        subject = _render_template(template.subject, variables)
        body_html = _render_template(template.body_html, variables)
        body_text = _render_template(template.body_text, variables) if template.body_text else None

        return await self.send_email(
            recipient_email=recipient_email,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            tenant_id=tenant_id,
            user_id=user_id,
            template_name=template_name,
            metadata={"variables": variables},
        )

    async def _send_smtp(
        self,
        recipient: str,
        subject: str,
        body_html: str,
        body_text: str | None,
    ) -> None:
        """Send email via SMTP (async)."""
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self._settings.smtp_from_name} <{self._settings.smtp_from_email}>"
        msg["To"] = recipient

        if body_text:
            msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=self._settings.smtp_host,
            port=self._settings.smtp_port,
            use_tls=self._settings.smtp_use_tls,
            username=self._settings.smtp_username,
            password=self._settings.smtp_password,
        )


def _render_template(template: str, variables: dict) -> str:
    """Simple {{ variable }} template rendering."""
    result = template
    for key, value in variables.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result
