"""Notification Service — Kafka consumer for Document domain events.

Subscribes to ``rainer.document.events`` and dispatches email notifications
for relevant document lifecycle transitions.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog
from aiokafka import AIOKafkaConsumer
import httpx

from ..core.config import get_settings
from ..core.database import AsyncSessionLocal
from ..domain.services import NotificationDomainService
from ..infra.db.repositories import NotificationLogRepository, NotificationTemplateRepository

logger = structlog.get_logger(__name__)

_consumer: AIOKafkaConsumer | None = None
_task: asyncio.Task[Any] | None = None

TOPIC = "rainer.document.events"

# Map event types to notification templates
EVENT_TEMPLATE_MAP: dict[str, str] = {
    "Document.SubmittedForReview": "document_submitted_for_review",
    "Document.Approved": "document_approved",
    "Document.Rejected": "document_rejected",
    "Document.Effective": "document_effective",
    "Document.Superseded": "document_superseded",
    "Document.Obsolete": "document_obsolete",
}


async def _resolve_user_email(user_id: str, settings) -> str | None:
    """Resolve a user ID to an email via the auth service."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{settings.auth_service_url}/api/v1/users/{user_id}",
                headers={"Authorization": f"Bearer {settings.rainer_master_secret}"},
            )
            if resp.is_success:
                user_data = resp.json()
                return user_data.get("email")
    except Exception as exc:
        logger.warning("user_email_resolution_failed", user_id=user_id, error=str(exc))
    return None


def _get_notification_recipient_id(event_type: str, data: dict[str, Any]) -> str | None:
    """Determine which user ID should receive the notification."""
    if event_type == "Document.SubmittedForReview":
        return data.get("approver_id")
    elif event_type == "Document.Approved":
        return data.get("owner_id")
    elif event_type == "Document.Rejected":
        return data.get("owner_id")
    elif event_type in ("Document.Effective", "Document.Superseded", "Document.Obsolete"):
        return data.get("owner_id")
    return None


async def _handle_message(msg_value: bytes | None) -> None:
    """Deserialize a Kafka message and dispatch a notification if applicable."""
    if msg_value is None:
        return
    try:
        payload: dict[str, Any] = json.loads(msg_value.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("notif_consumer_decode_failed", error=str(exc))
        return

    event_type = payload.get("event_type", "")
    data = payload.get("data", {})
    template_name = EVENT_TEMPLATE_MAP.get(event_type)

    if template_name is None:
        logger.debug("notif_consumer_skipped_irrelevant_event", event_type=event_type)
        return

    recipient_id = _get_notification_recipient_id(event_type, data)
    if not recipient_id:
        logger.debug("notif_consumer_no_recipient", event_type=event_type)
        return

    settings = get_settings()
    recipient_email = await _resolve_user_email(recipient_id, settings)
    if not recipient_email:
        logger.warning("notif_consumer_no_email", event_type=event_type, user_id=recipient_id)
        return

    variables = {
        "doc_number": data.get("doc_number", ""),
        "title": data.get("title", ""),
        "doc_type": data.get("doc_type", ""),
        "status": data.get("status", ""),
        "current_version": data.get("current_version", ""),
        "tenant_id": payload.get("tenant_id", ""),
        "actor_id": payload.get("actor_id", ""),
    }
    if event_type == "Document.Rejected":
        variables["rejection_reason"] = data.get("rejection_reason", "")
    if event_type == "Document.SubmittedForReview":
        variables["approver_id"] = data.get("approver_id", "")

    async with AsyncSessionLocal() as session:
        template_repo = NotificationTemplateRepository(session)
        log_repo = NotificationLogRepository(session)
        svc = NotificationDomainService(template_repo, log_repo, settings)

        try:
            await svc.send_from_template(
                template_name=template_name,
                recipient_email=recipient_email,
                variables=variables,
                tenant_id=payload.get("tenant_id"),
                user_id=recipient_id,
            )
            await session.commit()
            logger.info(
                "notif_consumer_dispatched",
                event_type=event_type,
                recipient=recipient_email,
                template=template_name,
            )
        except Exception as exc:
            await session.rollback()
            logger.error(
                "notif_consumer_dispatch_failed",
                event_type=event_type,
                template=template_name,
                error=str(exc),
            )


async def _consume_loop() -> None:
    """Background loop: poll Kafka and process document events."""
    settings = get_settings()
    global _consumer
    _consumer = AIOKafkaConsumer(
        TOPIC,
        bootstrap_servers=settings.kafka_bootstrap_servers,
        group_id=settings.kafka_group_id,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    await _consumer.start()
    logger.info("notif_document_consumer_started", topic=TOPIC)

    try:
        async for msg in _consumer:
            await _handle_message(msg.value)
    except asyncio.CancelledError:
        logger.info("notif_document_consumer_cancelled")
    except Exception:
        logger.exception("notif_document_consumer_error")
    finally:
        await _consumer.stop()
        _consumer = None
        logger.info("notif_document_consumer_stopped")


async def start_document_consumer() -> None:
    """Launch the document event consumer as a background task."""
    global _task
    if _task is not None and not _task.done():
        logger.warning("notif_document_consumer_already_running")
        return
    _task = asyncio.create_task(_consume_loop())
    logger.info("notif_document_consumer_task_created")


async def stop_document_consumer() -> None:
    """Cancel the background consumer task."""
    global _task
    if _task is not None and not _task.done():
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
        logger.info("notif_document_consumer_stopped_cleanly")
