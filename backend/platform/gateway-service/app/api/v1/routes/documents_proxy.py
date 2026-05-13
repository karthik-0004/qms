"""Gateway Service — Reverse proxy for QMS document-service routes."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, Request, Response

from ....core.config import Settings, get_settings

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["Documents (proxy)"])


def _join_url(base: str, path: str) -> str:
    if not path:
        return base.rstrip("/")
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


@router.api_route("/{full_path:path}", methods=["GET", "POST", "PATCH", "DELETE"])
@router.api_route("", methods=["GET", "POST"])
@router.api_route("/", methods=["GET", "POST"])
async def proxy_documents(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str = "",
) -> Response:
    upstream_base = settings.document_service_url
    upstream_url = _join_url(upstream_base, f"/api/v1/documents/{full_path}")

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

    logger.info(
        "gateway_proxy",
        upstream="document-service",
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

