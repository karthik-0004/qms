"""Gateway Service — Reverse proxy for QMS audit-management-service routes."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, Request, Response

from ....core.config import Settings, get_settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/audits", tags=["Audit Management (proxy)"])
checklists_router = APIRouter(prefix="/checklists", tags=["Audit Checklists (proxy)"])


def _join_url(base: str, path: str) -> str:
    if not path:
        return base.rstrip("/")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


async def _proxy(request: Request, upstream_url: str) -> Response:
    headers = dict(request.headers)
    headers.pop("host", None)
    body = await request.body()
    params = dict(request.query_params)

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        upstream_resp = await client.request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            params=params,
            content=body if body else None,
        )

    return Response(
        content=upstream_resp.content,
        status_code=upstream_resp.status_code,
        media_type=upstream_resp.headers.get("content-type"),
        headers={k: v for k, v in upstream_resp.headers.items() if k.lower() not in ("transfer-encoding", "content-encoding")},
    )


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@router.api_route("", methods=["GET", "POST"])
@router.api_route("/", methods=["GET", "POST"])
async def proxy_audits(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str = "",
) -> Response:
    upstream_url = _join_url(settings.audit_management_service_url, f"/api/v1/audits/{full_path}")
    return await _proxy(request, upstream_url)


@checklists_router.api_route("/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@checklists_router.api_route("", methods=["GET", "POST"])
async def proxy_checklists(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str = "",
) -> Response:
    upstream_url = _join_url(settings.audit_management_service_url, f"/api/v1/checklists/{full_path}")
    return await _proxy(request, upstream_url)
