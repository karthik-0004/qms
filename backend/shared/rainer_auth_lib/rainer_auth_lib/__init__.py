"""Rainer Auth Lib — JWT verification, access key validation, current user dependency."""

from .jwt import (
    JWTSettings,
    TokenPayload,
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_token,
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_permission,
    require_role,
    require_super_admin,
    OptionalCurrentUser,
)
from .access_keys import (
    generate_access_key,
    hash_access_key,
    verify_access_key,
)
from .permissions import Permission, UserRole, has_permission

__version__ = "0.1.0"

__all__ = [
    "JWTSettings",
    "TokenPayload",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "verify_token",
    "get_current_user",
    "get_current_active_user",
    "require_permission",
    "require_role",
    "require_super_admin",
    "OptionalCurrentUser",
    "generate_access_key",
    "hash_access_key",
    "verify_access_key",
    "Permission",
    "UserRole",
    "has_permission",
]

