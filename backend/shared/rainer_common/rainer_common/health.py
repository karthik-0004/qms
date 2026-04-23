"""Rainer Common — Standard health check endpoints factory."""

from collections.abc import Callable, Coroutine
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel


class HealthStatus(BaseModel):
    status: str
    service: str
    version: str
    timestamp: str
    checks: dict[str, str] = {}


def create_health_router(
    service_name: str,
    service_version: str = "0.1.0",
    readiness_checks: dict[str, Callable[[], Coroutine[Any, Any, bool]]] | None = None,
) -> APIRouter:
    """
    Factory that creates /health/live and /health/ready endpoints.

    Args:
        service_name: Name of the service
        service_version: Version string
        readiness_checks: Dict of check name → async callable returning bool
    """
    router = APIRouter(tags=["Health"])

    @router.get("/health/live", response_model=HealthStatus, include_in_schema=False)
    async def liveness() -> HealthStatus:
        return HealthStatus(
            status="ok",
            service=service_name,
            version=service_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    @router.get("/health/ready", response_model=HealthStatus, include_in_schema=False)
    async def readiness() -> HealthStatus:
        checks: dict[str, str] = {}
        all_healthy = True

        for check_name, check_fn in (readiness_checks or {}).items():
            try:
                healthy = await check_fn()
                checks[check_name] = "ok" if healthy else "degraded"
                if not healthy:
                    all_healthy = False
            except Exception:
                checks[check_name] = "error"
                all_healthy = False

        from fastapi import HTTPException

        status = HealthStatus(
            status="ok" if all_healthy else "degraded",
            service=service_name,
            version=service_version,
            timestamp=datetime.now(timezone.utc).isoformat(),
            checks=checks,
        )

        if not all_healthy:
            raise HTTPException(status_code=503, detail=status.model_dump())

        return status

    return router

