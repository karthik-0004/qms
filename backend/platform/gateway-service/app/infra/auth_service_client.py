"""Gateway Service — HTTP client for Auth Service (proxy helper)."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
from rainer_auth_lib.service_auth import ServiceAuthClient


@dataclass(frozen=True)
class AuthServiceClientConfig:
    base_url: str
    master_secret: str
    caller_service_name: str


class AuthServiceClient:
    def __init__(self, config: AuthServiceClientConfig) -> None:
        self._config = config
        self._service_auth = ServiceAuthClient(
            shared_secret=self._config.master_secret,
            service_name=self._config.caller_service_name,
        )

    async def post(
        self,
        path: str,
        *,
        json: dict | None,
        headers: dict[str, str] | None,
        cookies: dict[str, str] | None,
        timeout_s: float = 30.0,
    ) -> httpx.Response:
        url = f"{self._config.base_url.rstrip('/')}/{path.lstrip('/')}"
        merged_headers: dict[str, str] = {}
        if headers:
            merged_headers.update(headers)
        merged_headers.update(self._service_auth.get_auth_headers())

        async with httpx.AsyncClient(timeout=timeout_s) as client:
            return await client.post(url, json=json, headers=merged_headers, cookies=cookies)
