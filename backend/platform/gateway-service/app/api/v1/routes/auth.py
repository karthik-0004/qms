"""Gateway Service — Auth routes (proxy to Auth Service)."""

from __future__ import annotations

from typing import Annotated, Any

import httpx
from fastapi import APIRouter, Depends, Request, Response, status

from ....core.config import Settings, get_settings
from ....infra.auth_service_client import AuthServiceClient, AuthServiceClientConfig

router = APIRouter(prefix="/auth", tags=["Auth"])


def _get_auth_client(settings: Annotated[Settings, Depends(get_settings)]) -> AuthServiceClient:
    return AuthServiceClient(
        AuthServiceClientConfig(
            base_url=settings.auth_service_url,
            master_secret=settings.rainer_master_secret,
            caller_service_name=settings.service_name,
        )
    )


def _copy_set_cookie_headers(upstream: httpx.Response, downstream: Response) -> None:
    for value in upstream.headers.get_list("set-cookie"):
        downstream.headers.append("set-cookie", value)


@router.post("/login", summary="Proxy: auth-service login")
async def login(
    request: Request,
    client: Annotated[AuthServiceClient, Depends(_get_auth_client)],
) -> Response:
    payload: dict[str, Any] = await request.json()
    upstream = await client.post("/api/v1/auth/login", json=payload, headers=None, cookies=None)

    downstream = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )
    _copy_set_cookie_headers(upstream, downstream)
    return downstream


@router.post("/refresh", summary="Proxy: auth-service refresh")
async def refresh(
    request: Request,
    client: Annotated[AuthServiceClient, Depends(_get_auth_client)],
) -> Response:
    # Prefer cookie-based refresh; also forward body if provided.
    try:
        payload: dict[str, Any] | None = await request.json()
    except Exception:
        payload = None

    upstream = await client.post(
        "/api/v1/auth/refresh",
        json=payload,
        headers=None,
        cookies=request.cookies,
    )

    downstream = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )
    _copy_set_cookie_headers(upstream, downstream)
    return downstream


@router.post("/logout", summary="Proxy: auth-service logout")
async def logout(
    request: Request,
    client: Annotated[AuthServiceClient, Depends(_get_auth_client)],
) -> Response:
    try:
        payload: dict[str, Any] | None = await request.json()
    except Exception:
        payload = None

    upstream = await client.post(
        "/api/v1/auth/logout",
        json=payload,
        headers=None,
        cookies=request.cookies,
    )

    downstream = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )
    _copy_set_cookie_headers(upstream, downstream)
    return downstream


@router.post(
    "/logout-all",
    status_code=status.HTTP_200_OK,
    summary="Proxy: auth-service logout all devices",
)
async def logout_all(
    request: Request,
    client: Annotated[AuthServiceClient, Depends(_get_auth_client)],
) -> Response:
    upstream = await client.post(
        "/api/v1/auth/logout-all",
        json=None,
        headers={
            # Forward user JWT for CurrentUser dependency in auth-service
            "authorization": request.headers.get("authorization", ""),
        },
        cookies=request.cookies,
    )

    downstream = Response(
        content=upstream.content,
        status_code=upstream.status_code,
        media_type=upstream.headers.get("content-type", "application/json"),
    )
    _copy_set_cookie_headers(upstream, downstream)
    return downstream
