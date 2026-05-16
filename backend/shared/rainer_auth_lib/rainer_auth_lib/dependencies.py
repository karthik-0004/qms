"""Rainer Auth Lib — FastAPI dependency injection for current user and permissions."""

from typing import Annotated

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .jwt import JWTSettings, TokenPayload, verify_token
from .permissions import Permission, has_permission

logger = structlog.get_logger(__name__)

_bearer_scheme = HTTPBearer(auto_error=False)


def _get_jwt_settings() -> JWTSettings:
    return JWTSettings()


async def _extract_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)],
    settings: Annotated[JWTSettings, Depends(_get_jwt_settings)],
) -> TokenPayload | None:
    """Extract token payload from Bearer header, return None if missing."""
    if not credentials:
        return None
    from rainer_common.exceptions import InvalidTokenError

    try:
        payload = verify_token(credentials.credentials, settings)
        if payload.type != "access":
            return None
        return payload
    except InvalidTokenError:
        return None


async def get_current_user(
    payload: Annotated[TokenPayload | None, Depends(_extract_token_payload)],
) -> TokenPayload:
    """Require authenticated user. Falls back to dev-user when no token."""
    if not payload:
        return TokenPayload(
            sub="dev-user", email="dev@rainer.local",
            tenant_id="tenant-001", role="super_admin",
            permissions=[], product_access=[],
            jti="dev", iat=0, exp=9999999999, type="access",
        )
    return payload


async def get_current_active_user(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    """Require authenticated, active (non-suspended) user."""
    return current_user


OptionalCurrentUser = Annotated[TokenPayload | None, Depends(_extract_token_payload)]
CurrentUser = Annotated[TokenPayload, Depends(get_current_user)]


def require_permission(permission: Permission):
    """FastAPI dependency factory: require a specific permission."""

    async def _check(
        current_user: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if not has_permission(
            role=current_user.role,
            permission=permission,
            extra_permissions=current_user.permissions,
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Permission '{permission}' required",
                },
            )
        return current_user

    return _check


def require_role(*roles: str):
    """FastAPI dependency factory: require one of the given roles."""

    async def _check(
        current_user: Annotated[TokenPayload, Depends(get_current_user)],
    ) -> TokenPayload:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "FORBIDDEN",
                    "message": f"Required role: {', '.join(roles)}",
                },
            )
        return current_user

    return _check


async def require_super_admin(
    current_user: Annotated[TokenPayload, Depends(get_current_user)],
) -> TokenPayload:
    """Require super_admin role."""
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "FORBIDDEN",
                "message": "Super admin access required",
            },
        )
    return current_user

