"""Notification Service — FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from rainer_common.exceptions import RainerException
from rainer_common.health import create_health_router
from rainer_common.logging import setup_logging
from rainer_common.middleware import (
    CorrelationMiddleware, LoggingMiddleware, RequestIDMiddleware, SecurityHeadersMiddleware
)
from rainer_common.responses import ErrorResponse

from .api.v1 import api_v1_router
from .core.config import get_settings
from .core.database import check_db_health, dispose_engine
from .kafka_consumer import start_document_consumer, stop_document_consumer

logger = structlog.get_logger(__name__)
settings = get_settings()


def _safe_rainer_details(raw: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """ErrorDetail requires `message`; tolerate legacy detail dicts."""
    out: list[dict[str, Any]] = []
    for item in raw or []:
        if not isinstance(item, dict):
            out.append({"message": str(item)})
            continue
        if item.get("message") is not None:
            d: dict[str, Any] = {"message": str(item["message"])}
            if item.get("field") is not None:
                d["field"] = str(item["field"])
            if item.get("code") is not None:
                d["code"] = str(item["code"])
            out.append(d)
            continue
        upstream = item.get("upstream")
        if upstream is not None:
            out.append({"message": str(upstream)})
        else:
            parts = ", ".join(f"{k}={v}" for k, v in sorted(item.items()))
            out.append({"message": parts or "unknown detail"})
    return out


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.service_name, settings.service_version, settings.log_level, settings.json_logs)
    logger.info("service_starting", service=settings.service_name)
    await start_document_consumer()
    yield
    await stop_document_consumer()
    await dispose_engine()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Rainer Notification Service",
        description="Multi-channel notifications: email, SMS, push, webhooks, WebSocket",
        version=settings.service_version,
        lifespan=lifespan,
    )
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_allowed_origins,
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(RainerException)
    async def rainer_handler(request: Request, exc: RainerException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.of(
                exc.code,
                exc.message,
                _safe_rainer_details(exc.details),
                getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content=ErrorResponse.of(
            "VALIDATION_ERROR", "Validation failed", details, getattr(request.state, "request_id", None)).model_dump())

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        details: list[dict[str, str]] = []
        if settings.rainer_env != "production":
            details = [{"message": f"{type(exc).__name__}: {str(exc)[:800]}"}]
        return JSONResponse(
            status_code=500,
            content=ErrorResponse.of(
                "INTERNAL_SERVER_ERROR",
                "An unexpected error occurred",
                details,
                getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    app.include_router(create_health_router(settings.service_name, settings.service_version,
                                            readiness_checks={"database": check_db_health}))
    app.include_router(api_v1_router)
    return app


app = create_app()
