"""Training Service — Kafka consumer integration."""
from .document_events import start_training_consumer, stop_training_consumer

__all__ = ["start_training_consumer", "stop_training_consumer"]
