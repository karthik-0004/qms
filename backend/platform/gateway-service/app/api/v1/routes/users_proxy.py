"""Gateway Service — Reverse proxy for user-service user + role routes."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, Request, Response

from ....core.config import Settings, get_settings

logger = structlog.get_logger(__name__)

users_router = APIRouter(prefix="/users", tags=["Users (proxy)"])
roles_router = APIRouter(prefix="/roles", tags=["Roles (proxy)"])


def _join_url(base: str, path: str) -> str:
    if not path:
        return base.rstrip("/")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


async def _forward(
    *,
    upstream_base: str,
    request: Request,
    full_path: str,
    upstream_label: str,
) -> Response:
    upstream_url = _join_url(upstream_base, full_path)

    headers = dict(request.headers)
    headers.pop("host", None)

    body = await request.body()
    params = dict(request.query_params)

    async with httpx.AsyncClient(timeout=60.0) as client:
        upstream_resp = await client.request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            params=params,
            content=body if body else None,
        )

    logger.info(
        "gateway_proxy",
        upstream=upstream_label,
        method=request.method,
        path=str(request.url.path),
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


@users_router.api_route("/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@users_router.api_route("", methods=["GET", "POST"])
@users_router.api_route("/", methods=["GET", "POST"])
async def proxy_users(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str = "",
) -> Response:
    upstream_base = _join_url(settings.user_service_url, "/api/v1/users")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path=full_path,
        upstream_label="user-service",
    )


@roles_router.api_route("/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@roles_router.api_route("", methods=["GET", "POST"])
@roles_router.api_route("/", methods=["GET", "POST"])
async def proxy_roles(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str = "",
) -> Response:
    upstream_base = _join_url(settings.user_service_url, "/api/v1/roles")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path=full_path,
        upstream_label="user-service",
    )


router = APIRouter()
router.include_router(users_router)
router.include_router(roles_router)
