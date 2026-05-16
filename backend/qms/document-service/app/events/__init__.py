"""Document Service — Domain event publishing to Kafka."""

from .publisher import (
    close_document_event_publisher,
    get_document_event_publisher,
    init_document_event_publisher,
    publish_controlled_copy_issued,
    publish_controlled_copy_recalled,
    publish_document_acknowledged,
    publish_document_approved,
    publish_document_created,
    publish_document_effective,
    publish_document_obsolete,
    publish_document_rejected,
    publish_document_submitted,
    publish_document_superseded,
    publish_document_version_created,
)

__all__ = [
    "close_document_event_publisher",
    "get_document_event_publisher",
    "init_document_event_publisher",
    "publish_controlled_copy_issued",
    "publish_controlled_copy_recalled",
    "publish_document_acknowledged",
    "publish_document_approved",
    "publish_document_created",
    "publish_document_effective",
    "publish_document_obsolete",
    "publish_document_rejected",
    "publish_document_submitted",
    "publish_document_superseded",
    "publish_document_version_created",
]
