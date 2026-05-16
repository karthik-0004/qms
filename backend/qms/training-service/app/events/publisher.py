"""Training Service — Event publisher for Training.* domain events."""

from __future__ import annotations

import structlog
from rainer_events import DomainEvent, EventPublisher, get_event_producer, close_event_producer

logger = structlog.get_logger(__name__)

_publisher: EventPublisher | None = None


async def init_training_event_publisher(bootstrap_servers: str = "localhost:9092") -> EventPublisher:
    global _publisher
    if _publisher is None:
        producer = await get_event_producer(
            bootstrap_servers=bootstrap_servers,
            client_id="training-service",
        )
        _publisher = EventPublisher(producer, default_topic="rainer.training.events")
        logger.info("training_event_publisher_initialized", bootstrap_servers=bootstrap_servers)
    return _publisher


async def close_training_event_publisher() -> None:
    global _publisher
    if _publisher is not None:
        await close_event_producer()
        _publisher = None
        logger.info("training_event_publisher_closed")


def get_training_event_publisher() -> EventPublisher | None:
    return _publisher


async def _try_publish(event: DomainEvent) -> None:
    publisher = get_training_event_publisher()
    if publisher is None:
        logger.debug("event_skipped_no_publisher", event_type=event.event_type)
        return
    await publisher.publish(event)


async def publish_training_assigned(
    tenant_id: str, course_id: str, user_id: str, assigned_by: str | None, due_date: str | None = None,
) -> None:
    await _try_publish(DomainEvent(
        event_type="Training.Assigned",
        aggregate_type="training_assignment",
        aggregate_id=course_id,
        tenant_id=tenant_id,
        actor_id=assigned_by,
        data={
            "course_id": course_id,
            "user_id": user_id,
            "assigned_by": assigned_by,
            "due_date": due_date,
        },
    ))


async def publish_training_completed(
    tenant_id: str, assignment_id: str, course_id: str, user_id: str, score: int | None, passed: bool,
) -> None:
    await _try_publish(DomainEvent(
        event_type="Training.Completed",
        aggregate_type="training_assignment",
        aggregate_id=assignment_id,
        tenant_id=tenant_id,
        actor_id=user_id,
        data={
            "course_id": course_id,
            "user_id": user_id,
            "score": score,
            "passed": passed,
        },
    ))


async def publish_course_completed(
    tenant_id: str, assignment_id: str, course_id: str, user_id: str, score: int | None,
) -> None:
    await _try_publish(DomainEvent(
        event_type="Training.CourseCompleted",
        aggregate_type="training_assignment",
        aggregate_id=assignment_id,
        tenant_id=tenant_id,
        actor_id=user_id,
        data={
            "course_id": course_id,
            "user_id": user_id,
            "score": score,
        },
    ))


async def publish_training_exam_passed(
    tenant_id: str, exam_id: str, course_id: str, user_id: str, score: int,
) -> None:
    await _try_publish(DomainEvent(
        event_type="Training.ExamPassed",
        aggregate_type="exam_attempt",
        aggregate_id=exam_id,
        tenant_id=tenant_id,
        actor_id=user_id,
        data={
            "exam_id": exam_id,
            "course_id": course_id,
            "user_id": user_id,
            "score": score,
        },
    ))


async def publish_training_exam_failed(
    tenant_id: str, exam_id: str, course_id: str, user_id: str, score: int,
) -> None:
    await _try_publish(DomainEvent(
        event_type="Training.ExamFailed",
        aggregate_type="exam_attempt",
        aggregate_id=exam_id,
        tenant_id=tenant_id,
        actor_id=user_id,
        data={
            "exam_id": exam_id,
            "course_id": course_id,
            "user_id": user_id,
            "score": score,
        },
    ))
