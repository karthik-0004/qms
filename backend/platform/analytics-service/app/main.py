"""Analytics Service — FastAPI application factory."""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from rainer_common.exceptions import RainerException
from rainer_common.health import create_health_router
from rainer_common.logging import setup_logging
from rainer_common.middleware import CorrelationMiddleware, LoggingMiddleware, RequestIDMiddleware, SecurityHeadersMiddleware
from rainer_common.responses import ErrorResponse

from .api.v1 import api_v1_router
from .core.config import get_settings

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.service_name, settings.service_version, settings.log_level, settings.json_logs)
    logger.info("service_starting", service=settings.service_name)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Rainer Analytics Service",
                  description="Cross-module KPIs, dashboards, and time-series analytics",
                  version=settings.service_version, lifespan=lifespan)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationMiddleware)
    app.add_middleware(RequestIDMiddleware)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_allowed_origins,
                       allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

    @app.exception_handler(RainerException)
    async def rainer_handler(request: Request, exc: RainerException) -> JSONResponse:
        return JSONResponse(status_code=exc.status_code, content=ErrorResponse.of(
            exc.code, exc.message, exc.details, getattr(request.state, "request_id", None)).model_dump())

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(status_code=500, content=ErrorResponse.of("INTERNAL_SERVER_ERROR", "An unexpected error occurred").model_dump())

    app.include_router(create_health_router(settings.service_name, settings.service_version))
    app.include_router(api_v1_router)
    return app


app = create_app()
