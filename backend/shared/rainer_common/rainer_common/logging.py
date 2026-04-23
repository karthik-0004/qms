"""Rainer Common — Structured logging setup using structlog."""

import logging
import sys
from typing import Any

import structlog
from structlog.types import EventDict, Processor

import contextvars


def add_service_context(
    logger: Any,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """Inject service name/version from context if available."""
    service_name = _service_name_var.get(None)
    service_version = _service_version_var.get(None)
    if service_name:
        event_dict["service"] = service_name
    if service_version:
        event_dict["version"] = service_version
    return event_dict


def mask_sensitive_fields(
    logger: Any,
    method: str,
    event_dict: EventDict,
) -> EventDict:
    """Mask sensitive fields so they never appear in logs."""
    sensitive_keys = {
        "password",
        "password_hash",
        "token",
        "access_token",
        "refresh_token",
        "secret",
        "api_key",
        "mfa_secret",
        "authorization",
        "cookie",
    }
    for key in list(event_dict.keys()):
        if key.lower() in sensitive_keys:
            event_dict[key] = "***REDACTED***"
    return event_dict


_service_name_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "service_name", default=None
)
_service_version_var: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "service_version", default=None
)


def setup_logging(
    service_name: str,
    service_version: str = "0.1.0",
    log_level: str = "INFO",
    json_logs: bool = True,
) -> None:
    """
    Configure structlog for the service.
    Call once at application startup.
    """
    _service_name_var.set(service_name)
    _service_version_var.set(service_version)

    log_level_int = getattr(logging, log_level.upper(), logging.INFO)

    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        add_service_context,
        mask_sensitive_fields,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    renderer: Processor = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level_int),
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
        foreign_pre_chain=shared_processors,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers = [handler]
    root_logger.setLevel(log_level_int)

    for noisy_logger in ["uvicorn.access", "sqlalchemy.engine"]:
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str | None = None) -> structlog.BoundLogger:
    """Get a bound structlog logger."""
    return structlog.get_logger(name)

