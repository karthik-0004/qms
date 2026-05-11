"""Rainer Common — FastAPI middleware for request ID, logging, correlation."""

import time
import uuid
from collections.abc import Callable

import structlog
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = structlog.get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Injects a unique X-Request-ID into every request.
    Reads from incoming header or generates a new UUID.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Request-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.request_id = request_id

        structlog.contextvars.bind_contextvars(request_id=request_id)

        response = await call_next(request)
        response.headers[self.header_name] = request_id
        return response


class CorrelationMiddleware(BaseHTTPMiddleware):
    """
    Propagates X-Correlation-ID for distributed tracing across services.
    """

    def __init__(self, app: ASGIApp, header_name: str = "X-Correlation-ID") -> None:
        super().__init__(app)
        self.header_name = header_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = request.headers.get(self.header_name) or str(uuid.uuid4())
        request.state.correlation_id = correlation_id

        structlog.contextvars.bind_contextvars(correlation_id=correlation_id)

        response = await call_next(request)
        response.headers[self.header_name] = correlation_id
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every HTTP request with method, path, status, duration.
    Respects health check endpoints to avoid log spam.
    """

    SKIP_PATHS = {"/health/live", "/health/ready", "/metrics"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        start_time = time.perf_counter()

        structlog.contextvars.bind_contextvars(
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
        )

        try:
            response = await call_next(request)
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            log_fn = logger.warning if response.status_code >= 400 else logger.info
            log_fn(
                "http_request",
                status_code=response.status_code,
                duration_ms=duration_ms,
            )
            response.headers["X-Response-Time"] = f"{duration_ms}ms"
            return response

        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.error(
                "http_request_error",
                error=str(exc),
                duration_ms=duration_ms,
                exc_info=True,
            )
            raise

        finally:
            structlog.contextvars.unbind_contextvars("method", "path", "client_ip")


class TenantContextMiddleware(BaseHTTPMiddleware):
    """
    Extracts tenant context from JWT / headers and binds to structlog context.
    Services that use rainer_tenant_lib can override this with richer logic.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        tenant_id = request.headers.get("X-Tenant-ID")
        if tenant_id:
            request.state.tenant_id = tenant_id
            structlog.contextvars.bind_contextvars(tenant_id=tenant_id)

        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds standard security headers to all responses."""
    # Swagger/Redoc use inline scripts + external CDN assets; strict CSP will blank the page.
    # Use prefix matches so both `/docs` and `/docs/` (and oauth redirect) are covered.
    _SKIP_PREFIXES = ("/docs", "/redoc", "/openapi.json")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Skip security headers for documentation endpoints
        if request.url.path.startswith(self._SKIP_PREFIXES):
            return response
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=()"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        return response
