"""Gateway Service — Reverse proxies for RainerCCV domain services."""

from typing import Annotated

import httpx
import structlog
from fastapi import APIRouter, Depends, Request, Response

from ....core.config import Settings, get_settings

logger = structlog.get_logger(__name__)


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


_CONTRACT_METHODS = ["GET", "POST", "PATCH", "DELETE", "PUT", "OPTIONS"]

contracts_router = APIRouter(prefix="/contracts", tags=["Contracts (proxy)"])
workorders_router = APIRouter(prefix="/workorders", tags=["Work orders (proxy)"])
technicians_router = APIRouter(prefix="/technicians", tags=["Technicians (proxy)"])
invoices_router = APIRouter(prefix="/invoices", tags=["Billing / invoices (proxy)"])


@contracts_router.api_route("/{full_path:path}", methods=_CONTRACT_METHODS)
async def proxy_contracts_path(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str,
) -> Response:
    upstream_base = _join_url(settings.contract_service_url, "/api/v1/contracts")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path=full_path,
        upstream_label="contract-service",
    )


@contracts_router.api_route("", methods=_CONTRACT_METHODS)
@contracts_router.api_route("/", methods=_CONTRACT_METHODS)
async def proxy_contracts_root(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    upstream_base = _join_url(settings.contract_service_url, "/api/v1/contracts")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path="",
        upstream_label="contract-service",
    )


@workorders_router.api_route("/{full_path:path}", methods=_CONTRACT_METHODS)
async def proxy_workorders_path(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str,
) -> Response:
    upstream_base = _join_url(settings.workorder_service_url, "/api/v1/workorders")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path=full_path,
        upstream_label="workorder-service",
    )


@workorders_router.api_route("", methods=_CONTRACT_METHODS)
@workorders_router.api_route("/", methods=_CONTRACT_METHODS)
async def proxy_workorders_root(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    upstream_base = _join_url(settings.workorder_service_url, "/api/v1/workorders")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path="",
        upstream_label="workorder-service",
    )


@technicians_router.api_route("/{full_path:path}", methods=_CONTRACT_METHODS)
async def proxy_technicians_path(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str,
) -> Response:
    upstream_base = _join_url(settings.technician_service_url, "/api/v1/technicians")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path=full_path,
        upstream_label="technician-service",
    )


@technicians_router.api_route("", methods=_CONTRACT_METHODS)
@technicians_router.api_route("/", methods=_CONTRACT_METHODS)
async def proxy_technicians_root(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    upstream_base = _join_url(settings.technician_service_url, "/api/v1/technicians")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path="",
        upstream_label="technician-service",
    )


@invoices_router.api_route("/{full_path:path}", methods=_CONTRACT_METHODS)
async def proxy_invoices_path(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
    full_path: str,
) -> Response:
    upstream_base = _join_url(settings.billing_service_url, "/api/v1/invoices")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path=full_path,
        upstream_label="billing-service",
    )


@invoices_router.api_route("", methods=_CONTRACT_METHODS)
@invoices_router.api_route("/", methods=_CONTRACT_METHODS)
async def proxy_invoices_root(
    request: Request,
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    upstream_base = _join_url(settings.billing_service_url, "/api/v1/invoices")
    return await _forward(
        upstream_base=upstream_base,
        request=request,
        full_path="",
        upstream_label="billing-service",
    )


router = APIRouter()
router.include_router(contracts_router)
router.include_router(workorders_router)
router.include_router(technicians_router)
router.include_router(invoices_router)
