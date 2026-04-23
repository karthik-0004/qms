"""OpenTelemetry tracing instrumentation for Rainer Platform services.

Usage in service main.py:
    from rainer_common.tracing import setup_tracing
    setup_tracing(service_name="capa-service", otlp_endpoint="http://jaeger:4317")
"""

from __future__ import annotations

import structlog
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import set_global_textmap
from opentelemetry.propagators.b3 import B3MultiFormat
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

logger = structlog.get_logger(__name__)


def setup_tracing(
    service_name: str,
    service_version: str = "0.1.0",
    otlp_endpoint: str = "http://jaeger:4317",
    environment: str = "development",
    console_export: bool = False,
) -> TracerProvider:
    """Initialize OpenTelemetry tracing with OTLP exporter to Jaeger.

    Args:
        service_name: Name of the service (e.g. "capa-service").
        service_version: Semantic version of the service.
        otlp_endpoint: OTLP gRPC collector endpoint (Jaeger).
        environment: Deployment environment tag.
        console_export: Also export spans to console (for dev).

    Returns:
        Configured TracerProvider.
    """
    resource = Resource.create(
        {
            SERVICE_NAME: service_name,
            SERVICE_VERSION: service_version,
            "deployment.environment": environment,
        }
    )

    provider = TracerProvider(resource=resource)

    # OTLP exporter → Jaeger
    otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

    if console_export:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)

    # B3 propagation (compatible with Kong, Envoy, Istio)
    set_global_textmap(B3MultiFormat())

    logger.info(
        "tracing_initialized",
        service=service_name,
        endpoint=otlp_endpoint,
        environment=environment,
    )

    return provider


def instrument_fastapi(app, excluded_urls: str = "health,readiness,liveness") -> None:
    """Instrument a FastAPI application for automatic span creation."""
    FastAPIInstrumentor.instrument_app(app, excluded_urls=excluded_urls)
    logger.info("fastapi_instrumented")


def instrument_sqlalchemy(engine) -> None:
    """Instrument a SQLAlchemy engine for DB query tracing."""
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
    logger.info("sqlalchemy_instrumented")


def instrument_httpx() -> None:
    """Instrument httpx client for outbound HTTP call tracing."""
    HTTPXClientInstrumentor().instrument()
    logger.info("httpx_instrumented")
