"""Audit Service — Kafka consumer for Document domain events.

Subscribes to ``rainer.document.events`` and persists each event
as an immutable audit log entry via ``AuditDomainService``.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import structlog
from aiokafka import AIOKafkaConsumer

from ..core.config import get_settings
from ..core.database import AsyncSessionLocal
from ..domain.services import AuditDomainService
from ..infra.db.repositories import AuditLogRepository

logger = structlog.get_logger(__name__)

_consumer: AIOKafkaConsumer | None = None
_task: asyncio.Task[Any] | None = None

TOPIC = "rainer.document.events"


async def _handle_message(msg_value: bytes | None) -> None:
    """Deserialize a Kafka message and write it to the audit log."""
    if msg_value is None:
        return
    try:
        payload: dict[str, Any] = json.loads(msg_value.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("audit_consumer_decode_failed", error=str(exc))
        return

    async with AsyncSessionLocal() as session:
        repo = AuditLogRepository(session)
        svc = AuditDomainService(repo)
        await svc.append(
            action=payload.get("event_type", "UNKNOWN"),
            tenant_id=payload.get("tenant_id"),
            user_id=payload.get("actor_id"),
            resource_type=payload.get("aggregate_type"),
            resource_id=payload.get("aggregate_id"),
            metadata=payload.get("data", {}),
            source_service="document-service",
            event_id=payload.get("event_id"),
        )
        await session.commit()

    logger.debug("audit_consumer_processed", event_type=payload.get("event_type"))


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
    logger.info("audit_document_consumer_started", topic=TOPIC)

    try:
        async for msg in _consumer:
            await _handle_message(msg.value)
    except asyncio.CancelledError:
        logger.info("audit_document_consumer_cancelled")
    except Exception:
        logger.exception("audit_document_consumer_error")
    finally:
        await _consumer.stop()
        _consumer = None
        logger.info("audit_document_consumer_stopped")


async def start_document_consumer() -> None:
    """Launch the document event consumer as a background task."""
    global _task
    if _task is not None and not _task.done():
        logger.warning("audit_document_consumer_already_running")
        return
    _task = asyncio.create_task(_consume_loop())
    logger.info("audit_document_consumer_task_created")


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
        logger.info("audit_document_consumer_stopped_cleanly")
