"""Async Kafka producer for domain event publishing."""

from __future__ import annotations

import json
from typing import Any

import structlog
from aiokafka import AIOKafkaProducer

from .schemas import DomainEvent, EventEnvelope

logger = structlog.get_logger(__name__)

_producer: AIOKafkaProducer | None = None


async def get_event_producer(
    bootstrap_servers: str = "localhost:9092",
    client_id: str = "rainer-service",
) -> AIOKafkaProducer:
    """Get or create a singleton Kafka producer."""
    global _producer
    if _producer is None:
        _producer = AIOKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            client_id=client_id,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            key_serializer=lambda k: k.encode("utf-8") if k else None,
            acks="all",
            enable_idempotence=True,
            max_request_size=1_048_576,
            compression_type="gzip",
        )
        await _producer.start()
        logger.info("kafka_producer_started", bootstrap_servers=bootstrap_servers)
    return _producer


async def close_event_producer() -> None:
    """Gracefully close the Kafka producer."""
    global _producer
    if _producer is not None:
        await _producer.stop()
        _producer = None
        logger.info("kafka_producer_stopped")


class EventPublisher:
    """High-level event publisher with topic routing and error handling."""

    def __init__(self, producer: AIOKafkaProducer, default_topic: str = "rainer.events"):
        self._producer = producer
        self._default_topic = default_topic

    async def publish(
        self,
        event: DomainEvent,
        topic: str | None = None,
    ) -> None:
        """Publish a domain event to Kafka."""
        envelope = EventEnvelope.from_domain_event(event)
        target_topic = topic or f"rainer.{event.aggregate_type}.events"

        try:
            await self._producer.send_and_wait(
                topic=target_topic,
                key=event.aggregate_id,
                value=envelope.model_dump(mode="json"),
            )
            logger.info(
                "event_published",
                event_id=envelope.event_id,
                event_type=event.event_type,
                topic=target_topic,
                aggregate_id=event.aggregate_id,
            )
        except Exception:
            logger.error(
                "event_publish_failed",
                event_type=event.event_type,
                topic=target_topic,
                aggregate_id=event.aggregate_id,
                exc_info=True,
            )
            raise

    async def publish_batch(
        self,
        events: list[DomainEvent],
        topic: str | None = None,
    ) -> None:
        """Publish multiple events in a batch."""
        batch = self._producer.create_batch()
        for event in events:
            envelope = EventEnvelope.from_domain_event(event)
            target_topic = topic or f"rainer.{event.aggregate_type}.events"
            metadata = batch.append(
                key=event.aggregate_id.encode("utf-8") if event.aggregate_id else None,
                value=json.dumps(envelope.model_dump(mode="json"), default=str).encode("utf-8"),
                timestamp=None,
            )
            if metadata is None:
                # Batch is full, send it and create a new one
                await self._producer.send_and_wait(target_topic, value=batch)
                batch = self._producer.create_batch()

        if batch.record_count() > 0:
            target_topic = topic or self._default_topic
            await self._producer.send_and_wait(target_topic, value=batch)

        logger.info("event_batch_published", count=len(events))
