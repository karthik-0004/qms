"""Rainer Common — Shared base library for all Rainer Platform services."""

from .exceptions import (
    RainerException,
    NotFoundError,
    ForbiddenError,
    UnauthorizedError,
    ConflictError,
    ValidationError,
    ServiceUnavailableError,
    TooManyRequestsError,
)
from .responses import (
    SuccessResponse,
    ErrorResponse,
    PaginatedResponse,
    PaginationMeta,
    ResponseMeta,
)
from .models import BaseEntity, TimestampMixin
from .logging import setup_logging, get_logger
from .middleware import (
    RequestIDMiddleware,
    LoggingMiddleware,
    CorrelationMiddleware,
)

__version__ = "0.1.0"

__all__ = [
    "RainerException",
    "NotFoundError",
    "ForbiddenError",
    "UnauthorizedError",
    "ConflictError",
    "ValidationError",
    "ServiceUnavailableError",
    "TooManyRequestsError",
    "SuccessResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "PaginationMeta",
    "ResponseMeta",
    "BaseEntity",
    "TimestampMixin",
    "setup_logging",
    "get_logger",
    "RequestIDMiddleware",
    "LoggingMiddleware",
    "CorrelationMiddleware",
]
