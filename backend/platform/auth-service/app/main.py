"""Auth Service — FastAPI application factory."""

from contextlib import asynccontextmanager
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError

from rainer_common.exceptions import RainerException
from rainer_common.health import create_health_router
from rainer_common.logging import setup_logging
from rainer_common.middleware import (
    CorrelationMiddleware,
    LoggingMiddleware,
    RequestIDMiddleware,
    SecurityHeadersMiddleware,
)
from rainer_common.responses import ErrorResponse, ResponseMeta

from .api.v1 import api_v1_router
from .core.config import get_settings
from .core.database import check_db_health, dispose_engine

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(
        service_name=settings.service_name,
        service_version=settings.service_version,
        log_level=settings.log_level,
        json_logs=settings.json_logs,
    )
    logger.info(
        "service_starting",
        service=settings.service_name,
        version=settings.service_version,
        env=settings.rainer_env,
    )
    yield
    await dispose_engine()
    logger.info("service_stopped", service=settings.service_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Rainer Auth Service",
        description="Authentication, JWT issuance, MFA, and access key management",
        version=settings.service_version,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── Middleware (order matters — outermost applied last) ──────────────────
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ───────────────────────────────────────────────────
    @app.exception_handler(RainerException)
    async def rainer_exception_handler(
        request: Request, exc: RainerException
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse.of(
                code=exc.code,
                message=exc.message,
                details=exc.details,
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        request_id = getattr(request.state, "request_id", None)
        details = [
            {
                "field": ".".join(str(loc) for loc in e["loc"]),
                "message": e["msg"],
                "code": e["type"],
            }
            for e in exc.errors()
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse.of(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                details=details,
                request_id=request_id,
            ).model_dump(),
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        request_id = getattr(request.state, "request_id", None)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse.of(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occurred",
                request_id=request_id,
            ).model_dump(),
        )

    # ── Health endpoints ─────────────────────────────────────────────────────
    health_router = create_health_router(
        service_name=settings.service_name,
        service_version=settings.service_version,
        readiness_checks={"database": check_db_health},
    )
    app.include_router(health_router)

    # ── API routes ───────────────────────────────────────────────────────────
    app.include_router(api_v1_router)

    return app


app = create_app()
