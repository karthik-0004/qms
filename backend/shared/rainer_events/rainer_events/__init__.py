"""Rainer Events — Shared Kafka event publishing for all Rainer Platform services."""

from rainer_events.producer import EventPublisher, get_event_producer, close_event_producer
from rainer_events.schemas import DomainEvent, EventEnvelope

__version__ = "0.1.0"

__all__ = [
    "EventPublisher",
    "get_event_producer",
    "close_event_producer",
    "DomainEvent",
    "EventEnvelope",
]
