"""Gateway Service — Reverse proxy for tenant-service routes."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import JSONResponse
from rainer_common.responses import ErrorResponse

from ....core.config import Settings, get_settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/tenants", tags=["Tenants (proxy)"])


def _join_url(base: str, path: str) -> str:
    if not path:
        return base.rstrip("/")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


async def _forward_to_tenant_service(
    request: Request,
    settings: Settings,
    path_after_tenants_prefix: str,
) -> Response:
    """Proxy to tenant-service /api/v1/tenants/{path_after_tenants_prefix}."""
    upstream_base = _join_url(settings.tenant_service_url, "/api/v1/tenants")
    upstream_url = _join_url(upstream_base, path_after_tenants_prefix)

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()
    params = dict(request.query_params)
    rid = getattr(request.state, "request_id", None)

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            upstream_resp = await client.request(
                method=request.method,
                url=upstream_url,
                headers=headers,
                params=params,
                content=body if body else None,
            )
    except httpx.RequestError as e:
        logger.error(
            "gateway_tenant_upstream_failed",
            upstream_url=upstream_url,
            error=str(e),
        )
        return JSONResponse(
            status_code=502,
            content=ErrorResponse.of(
                "UPSTREAM_UNREACHABLE",
                "Could not reach tenant-service. Ensure it is running and TENANT_SERVICE_URL is correct.",
                [{"message": str(e)}],
                rid,
            ).model_dump(),
        )

    logger.info(
        "gateway_proxy",
        upstream="tenant-service",
        method=request.method,
        path=str(request.url.path),
        upstream_url=upstream_url,
        upstream_status=upstream_resp.status_code,
    )

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type"),
        headers={
            k: v
            for k, v in upstream_resp.headers.items()
            if k.lower() in {"content-type", "cache-control", "location"}
        },
    )


# Static path so OpenAPI and clients never confuse this with GET /{tenant_id}.
@router.post("/resend-welcome-email")
async def proxy_resend_welcome_email(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    return await _forward_to_tenant_service(request, settings, "resend-welcome-email")


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@router.api_route("", methods=["GET", "POST"])
@router.api_route("/", methods=["GET", "POST"])
async def proxy_tenants(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str = "",
) -> Response:
    return await _forward_to_tenant_service(request, settings, full_path)
