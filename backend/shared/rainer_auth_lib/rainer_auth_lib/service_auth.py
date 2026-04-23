"""Service-to-service authentication for internal Rainer Platform calls.

Supports two modes:
1. Internal JWT — signed with a shared secret, audience="rainer-internal"
2. API Key — static pre-shared key per service (for simpler setups)

Usage (caller side):
    from rainer_auth_lib.service_auth import ServiceAuthClient
    client = ServiceAuthClient(shared_secret="...", service_name="capa-service")
    headers = client.get_auth_headers()
    # Pass headers to httpx/aiohttp calls

Usage (receiver side — FastAPI dependency):
    from rainer_auth_lib.service_auth import require_service_auth
    @router.get("/internal/sync", dependencies=[Depends(require_service_auth)])
    async def internal_endpoint(): ...
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Annotated

import structlog
from fastapi import Depends, Header, HTTPException, status

logger = structlog.get_logger(__name__)

_INTERNAL_AUDIENCE = "rainer-internal"
_TOKEN_VALIDITY_SECONDS = 300  # 5 minutes


class ServiceAuthClient:
    """Generate auth headers for service-to-service calls."""

    def __init__(self, shared_secret: str, service_name: str):
        self._secret = shared_secret.encode()
        self._service_name = service_name

    def get_auth_headers(self) -> dict[str, str]:
        """Generate HMAC-signed service auth headers."""
        timestamp = str(int(time.time()))
        payload = f"{self._service_name}:{timestamp}:{_INTERNAL_AUDIENCE}"
        signature = hmac.new(self._secret, payload.encode(), hashlib.sha256).hexdigest()
        return {
            "X-Service-Name": self._service_name,
            "X-Service-Timestamp": timestamp,
            "X-Service-Signature": signature,
        }


def _verify_service_signature(
    service_name: str,
    timestamp: str,
    signature: str,
    shared_secret: str,
) -> bool:
    """Verify the HMAC signature from an internal service call."""
    # Reject if timestamp is too old
    try:
        ts = int(timestamp)
    except ValueError:
        return False

    if abs(time.time() - ts) > _TOKEN_VALIDITY_SECONDS:
        logger.warning("service_auth_expired", service=service_name, age=time.time() - ts)
        return False

    expected_payload = f"{service_name}:{timestamp}:{_INTERNAL_AUDIENCE}"
    expected_sig = hmac.new(shared_secret.encode(), expected_payload.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected_sig)


async def require_service_auth(
    x_service_name: Annotated[str | None, Header()] = None,
    x_service_timestamp: Annotated[str | None, Header()] = None,
    x_service_signature: Annotated[str | None, Header()] = None,
) -> str:
    """FastAPI dependency that validates service-to-service auth headers.

    Requires RAINER_MASTER_SECRET env var to be set.
    Returns the calling service name on success.
    """
    import os

    shared_secret = os.environ.get("RAINER_MASTER_SECRET", "")

    if not all([x_service_name, x_service_timestamp, x_service_signature]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing service auth headers",
        )

    if not shared_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service auth not configured",
        )

    if not _verify_service_signature(
        x_service_name, x_service_timestamp, x_service_signature, shared_secret
    ):
        logger.warning("service_auth_failed", caller=x_service_name)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid service credentials",
        )

    logger.debug("service_auth_ok", caller=x_service_name)
    return x_service_name
