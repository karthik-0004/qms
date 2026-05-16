"""Audit Service — Kafka consumer integration."""

from .document_events import start_document_consumer, stop_document_consumer

__all__ = [
    "start_document_consumer",
    "stop_document_consumer",
]
