"""Training Service — Kafka consumer for Document events.

Listens for Document.Effective events and auto-creates training assignments
for distribution list users linked to courses that reference the document.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import httpx
import structlog
from aiokafka import AIOKafkaConsumer

from ..core.config import get_settings
from ..core.database import AsyncSessionLocal
from ..domain.services import TrainingDomainService
from ..infra.db.repositories import (
    TrainingAssignmentRepository, TrainingCourseRepository,
    JobCodeCourseRepository, JobCodeAssignmentRepository,
)

logger = structlog.get_logger(__name__)

_consumer: AIOKafkaConsumer | None = None
_task: asyncio.Task[Any] | None = None

TOPIC = "rainer.document.events"

# Cache the document-service base URL
_DOCUMENT_SERVICE_URL: str | None = None


def _get_doc_service_url() -> str:
    global _DOCUMENT_SERVICE_URL
    if _DOCUMENT_SERVICE_URL is None:
        settings = get_settings()
        _DOCUMENT_SERVICE_URL = settings.document_service_url or "http://document-service:8015"
    return _DOCUMENT_SERVICE_URL


async def _fetch_document_distribution(tenant_id: str, document_id: str) -> list[str]:
    """Fetch distribution list user IDs from document-service."""
    base = _get_doc_service_url()
    url = f"{base}/api/v1/documents/{document_id}/distribution"
    headers = {
        "X-Tenant-ID": tenant_id,
        "X-Internal-Call": "true",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            users = data.get("data", [])
            return [u["user_id"] for u in users if "user_id" in u]
    except Exception as exc:
        logger.warning("failed_to_fetch_distribution", document_id=document_id, error=str(exc))
        return []


async def _handle_message(msg_value: bytes | None) -> None:
    if msg_value is None:
        return
    try:
        payload: dict[str, Any] = json.loads(msg_value.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.warning("training_consumer_decode_failed", error=str(exc))
        return

    event_type = payload.get("event_type")
    if event_type != "Document.Effective":
        return

    tenant_id = payload.get("tenant_id")
    document_id = payload.get("aggregate_id")
    data = payload.get("data", {})

    if not tenant_id or not document_id:
        logger.warning("training_consumer_missing_fields", payload=payload)
        return

    logger.info("document_effective_received", document_id=document_id, tenant_id=tenant_id)

    async with AsyncSessionLocal() as session:
        course_repo = TrainingCourseRepository(session)
        assignment_repo = TrainingAssignmentRepository(session)

        # Find all training courses linked to this document
        try:
            from sqlalchemy import select
            from ..infra.db.models import TrainingCourse
            result = await session.execute(
                select(TrainingCourse).where(
                    TrainingCourse.document_id == document_id,
                    TrainingCourse.is_active.is_(True),
                )
            )
            courses = list(result.scalars().all())
        except Exception as exc:
            logger.error("training_consumer_query_failed", error=str(exc))
            await session.rollback()
            return

        if not courses:
            logger.info("no_courses_linked_to_document", document_id=document_id)
            return

        # Fetch distribution list users
        user_ids = await _fetch_document_distribution(tenant_id, document_id)
        if not user_ids:
            logger.info("no_distribution_users", document_id=document_id)
            return

        svc = TrainingDomainService(
            course_repo=course_repo,
            assignment_repo=assignment_repo,
            tenant_id=tenant_id,
        )

        created_count = 0
        for course in courses:
            for user_id in user_ids:
                try:
                    existing = await assignment_repo.get_by_course_user(course.id, user_id)
                    if existing and existing.status in ("assigned", "in_progress"):
                        continue
                    await assignment_repo.create(
                        tenant_id=tenant_id,
                        course_id=course.id,
                        user_id=user_id,
                        assigned_by=data.get("actor_id") or "system",
                        due_date=None,
                    )
                    created_count += 1
                except Exception as exc:
                    logger.warning(
                        "failed_to_create_assignment",
                        course_id=course.id, user_id=user_id, error=str(exc),
                    )

        await session.commit()
        logger.info(
            "training_assignments_created",
            document_id=document_id, count=created_count,
        )


async def _consume_loop() -> None:
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
    logger.info("training_document_consumer_started", topic=TOPIC)

    try:
        async for msg in _consumer:
            await _handle_message(msg.value)
    except asyncio.CancelledError:
        logger.info("training_document_consumer_cancelled")
    except Exception:
        logger.exception("training_document_consumer_error")
    finally:
        await _consumer.stop()
        _consumer = None
        logger.info("training_document_consumer_stopped")


async def start_training_consumer() -> None:
    global _task
    if _task is not None and not _task.done():
        logger.warning("training_document_consumer_already_running")
        return
    _task = asyncio.create_task(_consume_loop())
    logger.info("training_document_consumer_task_created")


async def stop_training_consumer() -> None:
    global _task
    if _task is not None and not _task.done():
        _task.cancel()
        try:
            await _task
        except asyncio.CancelledError:
            pass
        _task = None
        logger.info("training_document_consumer_stopped_cleanly")
