"""Document-specific event publisher — creates DomainEvent objects for every document lifecycle transition."""

from __future__ import annotations

import structlog
from aiokafka import AIOKafkaProducer

from rainer_events import DomainEvent, EventPublisher, get_event_producer, close_event_producer

from ..infra.db.models import ControlledCopy, Document, DocumentAcknowledgment

logger = structlog.get_logger(__name__)

_publisher: EventPublisher | None = None


async def init_document_event_publisher(
    bootstrap_servers: str = "localhost:9092",
) -> EventPublisher:
    global _publisher
    if _publisher is None:
        producer = await get_event_producer(
            bootstrap_servers=bootstrap_servers,
            client_id="document-service",
        )
        _publisher = EventPublisher(producer, default_topic="rainer.document.events")
        logger.info("document_event_publisher_initialized", bootstrap_servers=bootstrap_servers)
    return _publisher


async def close_document_event_publisher() -> None:
    global _publisher
    if _publisher is not None:
        await close_event_producer()
        _publisher = None
        logger.info("document_event_publisher_closed")


def get_document_event_publisher() -> EventPublisher | None:
    return _publisher


def _base_event(doc: Document, actor_id: str | None) -> dict:
    return {
        "doc_number": doc.doc_number,
        "title": doc.title,
        "doc_type": doc.doc_type,
        "status": doc.status,
        "current_version": doc.current_version,
        "department": doc.department,
        "owner_id": doc.owner_id,
        "file_id": doc.file_id,
    }


async def _try_publish(event: DomainEvent) -> None:
    publisher = get_document_event_publisher()
    if publisher is None:
        logger.debug("event_skipped_no_publisher", event_type=event.event_type)
        return
    await publisher.publish(event)


async def publish_document_created(doc: Document, actor_id: str) -> None:
    await _try_publish(DomainEvent(
        event_type="Document.Created",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=_base_event(doc, actor_id),
    ))


async def publish_document_submitted(doc: Document, actor_id: str, approver_id: str | None = None) -> None:
    data = _base_event(doc, actor_id)
    data["previous_status"] = "draft"
    data["new_status"] = "under_review"
    data["approver_id"] = approver_id
    await _try_publish(DomainEvent(
        event_type="Document.SubmittedForReview",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_approved(doc: Document, actor_id: str, signature_hash: str | None = None) -> None:
    data = _base_event(doc, actor_id)
    data["previous_status"] = "under_review"
    data["new_status"] = "approved"
    data["signature_hash"] = signature_hash
    data["effective_date"] = str(doc.effective_date) if doc.effective_date else None
    await _try_publish(DomainEvent(
        event_type="Document.Approved",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_rejected(doc: Document, actor_id: str, reason: str) -> None:
    data = _base_event(doc, actor_id)
    data["previous_status"] = "under_review"
    data["new_status"] = "draft"
    data["rejection_reason"] = reason
    await _try_publish(DomainEvent(
        event_type="Document.Rejected",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_effective(doc: Document, actor_id: str) -> None:
    data = _base_event(doc, actor_id)
    data["previous_status"] = "approved"
    data["new_status"] = "effective"
    await _try_publish(DomainEvent(
        event_type="Document.Effective",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_superseded(doc: Document, actor_id: str) -> None:
    data = _base_event(doc, actor_id)
    data["previous_status"] = "effective"
    data["new_status"] = "superseded"
    await _try_publish(DomainEvent(
        event_type="Document.Superseded",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_obsolete(doc: Document, actor_id: str, previous_status: str | None = None) -> None:
    data = _base_event(doc, actor_id)
    data["previous_status"] = previous_status or doc.status
    data["new_status"] = "obsolete"
    await _try_publish(DomainEvent(
        event_type="Document.Obsolete",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_version_created(
    doc: Document, actor_id: str, change_summary: str, prev_version: str, new_version: str
) -> None:
    data = _base_event(doc, actor_id)
    data["prev_version"] = prev_version
    data["new_version"] = new_version
    data["change_summary"] = change_summary
    await _try_publish(DomainEvent(
        event_type="Document.VersionCreated",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_document_acknowledged(
    doc: Document, ack: DocumentAcknowledgment, actor_id: str
) -> None:
    data = _base_event(doc, actor_id)
    data["acknowledged_by"] = ack.user_id
    data["acknowledged_at"] = str(ack.acknowledged_at)
    data["version"] = ack.version
    data["signature_hash"] = ack.signature_hash
    await _try_publish(DomainEvent(
        event_type="Document.Acknowledged",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_controlled_copy_issued(
    doc: Document, cc: ControlledCopy, actor_id: str
) -> None:
    data = _base_event(doc, actor_id)
    data["copy_id"] = cc.id
    data["copy_number"] = cc.copy_number
    data["issued_to"] = cc.issued_to
    data["version"] = cc.version
    await _try_publish(DomainEvent(
        event_type="Document.ControlledCopyIssued",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))


async def publish_controlled_copy_recalled(
    doc: Document, cc: ControlledCopy, actor_id: str
) -> None:
    data = _base_event(doc, actor_id)
    data["copy_id"] = cc.id
    data["copy_number"] = cc.copy_number
    data["issued_to"] = cc.issued_to
    data["version"] = cc.version
    data["recalled_at"] = str(cc.recalled_at)
    data["status"] = cc.status
    await _try_publish(DomainEvent(
        event_type="Document.ControlledCopyRecalled",
        aggregate_type="document",
        aggregate_id=doc.id,
        tenant_id=doc.tenant_id,
        actor_id=actor_id,
        data=data,
    ))
