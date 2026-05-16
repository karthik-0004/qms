"""Training Service — FastAPI application factory."""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from rainer_common.exceptions import RainerException
from rainer_common.health import create_health_router
from rainer_common.logging import setup_logging
from rainer_common.middleware import CorrelationMiddleware, LoggingMiddleware, RequestIDMiddleware, SecurityHeadersMiddleware
from rainer_common.responses import ErrorResponse

from .api.v1 import api_v1_router
from .core.config import get_settings
from .core.database import check_db_health, dispose_engine
from .events import close_training_event_publisher, init_training_event_publisher
from .kafka_consumer import start_training_consumer, stop_training_consumer

logger = structlog.get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.service_name, settings.service_version, settings.log_level, settings.json_logs)
    logger.info("service_starting", service=settings.service_name)

    # Initialize Kafka event publisher (gracefully handles missing Kafka)
    try:
        await init_training_event_publisher(settings.kafka_bootstrap_servers)
        logger.info("training_event_publisher_initialized")
    except Exception as exc:
        logger.warning("training_event_publisher_init_failed", error=str(exc))

    # Start Kafka consumer for Document.Effective events
    await start_training_consumer()

    yield

    await stop_training_consumer()
    await close_training_event_publisher()
    await dispose_engine()



def create_app() -> FastAPI:
    app = FastAPI(
        title="Rainer Training Service",
        description="QMS Training course management and assignment tracking",
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
        return JSONResponse(status_code=exc.status_code, content=ErrorResponse.of(
            exc.code, exc.message, exc.details, getattr(request.state, "request_id", None)).model_dump())

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        details = [{"field": ".".join(str(l) for l in e["loc"]), "message": e["msg"]} for e in exc.errors()]
        return JSONResponse(status_code=422, content=ErrorResponse.of(
            "VALIDATION_ERROR", "Validation failed", details, getattr(request.state, "request_id", None)).model_dump())

    @app.exception_handler(Exception)
    async def unhandled_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("unhandled_exception", error=str(exc), exc_info=True)
        return JSONResponse(status_code=500, content=ErrorResponse.of("INTERNAL_SERVER_ERROR", "An unexpected error occurred").model_dump())

    app.include_router(create_health_router(settings.service_name, settings.service_version,
                                            readiness_checks={"database": check_db_health}))
    app.include_router(api_v1_router)
    return app


app = create_app()
