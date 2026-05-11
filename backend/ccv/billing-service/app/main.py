from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.exceptions import ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.database import dispose_engine

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "billing_service.startup",
        service=settings.service_name,
        version=settings.service_version,
        port=settings.port,
        env=settings.rainer_env,
        default_currency=settings.default_currency,
        payment_due_days=settings.payment_due_days,
    )
    yield
    await dispose_engine()
    logger.info("billing_service.shutdown", service=settings.service_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Billing Service",
        description="RainerCCV — Invoice generation, payment tracking, billing lifecycle",
        version=settings.service_version,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

    @app.exception_handler(LookupError)
    async def not_found_handler(request: Request, exc: LookupError):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(ResponseValidationError)
    async def response_validation_handler(request: Request, exc: ResponseValidationError):
        logger.warning(
            "response_validation_failed",
            path=str(request.url.path),
            errors=exc.errors(),
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Response validation failed", "errors": exc.errors()},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_handler(request: Request, exc: SQLAlchemyError):
        logger.exception("database_error", path=str(request.url.path))
        if settings.rainer_env == "development":
            return JSONResponse(
                status_code=500,
                content={"detail": str(exc), "type": type(exc).__name__},
            )
        return JSONResponse(status_code=500, content={"detail": "Database error"})

    @app.get("/health", tags=["ops"])
    async def health():
        return {
            "status": "ok",
            "service": settings.service_name,
            "version": settings.service_version,
            "currency": settings.default_currency,
        }

    @app.get("/ready", tags=["ops"])
    async def ready():
        return {"status": "ready", "service": settings.service_name}

    app.include_router(api_v1_router)
    return app


app = create_app()
