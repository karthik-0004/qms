"""Gateway Service — Core routing and auth validation domain service."""

import structlog

from rainer_auth_lib.jwt import JWTSettings, verify_token
from rainer_common.exceptions import InvalidTokenError, TooManyRequestsError, UnauthorizedError

logger = structlog.get_logger(__name__)


class GatewayDomainService:
    """
    API Gateway business logic:
    - JWT validation and tenant context extraction
    - Rate limiting checks
    - Request routing headers
    """

    def __init__(self, jwt_settings: JWTSettings) -> None:
        self._jwt_settings = jwt_settings

    def validate_token(self, token: str) -> dict:
        """Validate JWT and return payload dict."""
        try:
            payload = verify_token(token, self._jwt_settings)
            return {
                "user_id": payload.sub,
                "email": payload.email,
                "tenant_id": payload.tenant_id,
                "role": payload.role,
                "permissions": payload.permissions,
                "product_access": payload.product_access,
                "jti": payload.jti,
            }
        except InvalidTokenError as exc:
            logger.warning("gateway_token_invalid", error=str(exc))
            raise UnauthorizedError(str(exc))

    def extract_bearer_token(self, authorization: str | None) -> str | None:
        """Extract token from 'Bearer <token>' header."""
        if not authorization:
            return None
        parts = authorization.split(" ", 1)
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return None
        return parts[1]

    def build_upstream_headers(self, token_payload: dict) -> dict[str, str]:
        """Build headers to inject into upstream requests."""
        headers: dict[str, str] = {}
        if token_payload.get("tenant_id"):
            headers["X-Tenant-ID"] = token_payload["tenant_id"]
        if token_payload.get("user_id"):
            headers["X-User-ID"] = token_payload["user_id"]
        if token_payload.get("role"):
            headers["X-User-Role"] = token_payload["role"]
        return headers
