from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from app.api.v1 import api_v1_router
from app.core.config import settings
from app.core.database import dispose_engine

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(
        "workorder_service.startup",
        service=settings.service_name,
        version=settings.service_version,
        port=settings.port,
        env=settings.rainer_env,
    )
    yield
    await dispose_engine()
    logger.info("workorder_service.shutdown", service=settings.service_name)


def create_app() -> FastAPI:
    app = FastAPI(
        title="Work Order Service",
        description="RainerCCV — Field work order management and technician dispatch",
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

    @app.get("/health", tags=["ops"])
    async def health():
        return {"status": "ok", "service": settings.service_name, "version": settings.service_version}

    @app.get("/ready", tags=["ops"])
    async def ready():
        return {"status": "ready", "service": settings.service_name}

    app.include_router(api_v1_router)
    return app


app = create_app()
