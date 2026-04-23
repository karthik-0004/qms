"""Rainer Events — Shared Kafka event publishing for all Rainer Platform services."""

from .producer import EventProducer, get_event_producer, close_event_producer
from .schemas import DomainEvent, EventEnvelope

__version__ = "0.1.0"

__all__ = [
    "EventProducer",
    "get_event_producer",
    "close_event_producer",
    "DomainEvent",
    "EventEnvelope",
]
