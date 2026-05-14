"""Tenant Service — FastAPI application factory."""

import os
from contextlib import asynccontextmanager
from typing import Any

# MUST be imported before any rainer_auth_lib usage
from .core.config import ensure_jwt_environment

ensure_jwt_environment()

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from rainer_common.exceptions import RainerException
from rainer_common.health import create_health_router
from rainer_common.logging import setup_logging
from rainer_common.middleware import (
    CorrelationMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from rainer_common.responses import ErrorResponse

from .api.v1 import api_v1_router
from .core.config import get_settings
from .core.database import check_db_health, dispose_engine

logger = structlog.get_logger(__name__)
settings = get_settings()


def _safe_rainer_details(raw: list[dict[str, Any]] | None) -> list[dict[str, Any]]:
    """ErrorResponse.ErrorDetail requires `message`; legacy details used tenant_id/upstream only."""
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
    setup_logging(
        service_name=settings.service_name,
        service_version=settings.service_version,
        log_level=settings.log_level,
        json_logs=settings.json_logs,
    )
    logger.info("service_starting", service=settings.service_name, env=settings.rainer_env)
    yield
    await dispose_engine()
    logger.info("service_stopped", service=settings.service_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Rainer Tenant Service",
        description="Tenant provisioning, lifecycle, and configuration management",
        version=settings.service_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RainerException)
    async def rainer_handler(request: Request, exc: RainerException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.of(
                code=exc.code,
                message=exc.message,
                details=_safe_rainer_details(exc.details),
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]}
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse.of(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=details,
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        details: list[dict[str, str]] = []
        if settings.rainer_env != "production":
            details = [{"message": f"{type(exc).__name__}: {str(exc)[:800]}"}]
        return JSONResponse(
            status_code=500,
            content=ErrorResponse.of(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                details=details,
                request_id=getattr(request.state, "request_id", None),
            ).model_dump(),
        )

    health_router = create_health_router(
        service_name=settings.service_name,
        service_version=settings.service_version,
        readiness_checks={"database": check_db_health},
    )
    app.include_router(health_router)
    app.include_router(api_v1_router)

    return app


app = create_app()
