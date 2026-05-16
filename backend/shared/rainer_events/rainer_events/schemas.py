"""Domain event schemas for Kafka publishing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class DomainEvent(BaseModel):
    """Base domain event — subclass for specific event types."""

    event_type: str
    aggregate_type: str
    aggregate_id: str
    tenant_id: str
    actor_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EventEnvelope(BaseModel):
    """Wire-format wrapper for domain events."""

    event_id: str = Field(default_factory=lambda: str(uuid4()))
    event_type: str
    aggregate_type: str
    aggregate_id: str
    tenant_id: str
    actor_id: str | None = None
    data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    schema_version: int = 1

    @classmethod
    def from_domain_event(cls, event: DomainEvent) -> EventEnvelope:
        return cls(
            event_type=event.event_type,
            aggregate_type=event.aggregate_type,
            aggregate_id=event.aggregate_id,
            tenant_id=event.tenant_id,
            actor_id=event.actor_id,
            data=event.data,
            metadata=event.metadata,
        )
