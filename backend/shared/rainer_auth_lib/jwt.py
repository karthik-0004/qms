"""Rainer Auth Lib — JWT creation and verification (RS256)."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import ExpiredSignatureError, JWTError, jwt
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class JWTSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


class TokenPayload(BaseModel):
    """JWT token payload."""

    sub: str
    email: str
    tenant_id: str | None = None
    company_id: str | None = None
    role: str = "tenant_user"
    permissions: list[str] = []
    product_access: list[str] = []
    jti: str
    iat: int
    exp: int
    type: Literal["access", "refresh"] = "access"

    @field_validator("jti", mode="before")
    @classmethod
    def ensure_jti(cls, v: str | None) -> str:
        return v or str(uuid.uuid4())


def create_access_token(
    subject: str,
    email: str,
    settings: JWTSettings,
    tenant_id: str | None = None,
    company_id: str | None = None,
    role: str = "tenant_user",
    permissions: list[str] | None = None,
    product_access: list[str] | None = None,
    expires_delta: timedelta | None = None,
) -> tuple[str, str]:
    """
    Create a signed JWT access token.
    Returns (encoded_token, jti) tuple.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        or timedelta(minutes=settings.access_token_expire_minutes)
    )
    jti = str(uuid.uuid4())

    payload = {
        "sub": subject,
        "email": email,
        "tenant_id": tenant_id,
        "company_id": company_id,
        "role": role,
        "permissions": permissions or [],
        "product_access": product_access or [],
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }

    encoded = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return encoded, jti


def create_refresh_token(
    subject: str,
    settings: JWTSettings,
    expires_delta: timedelta | None = None,
) -> tuple[str, str]:
    """
    Create a signed JWT refresh token.
    Returns (encoded_token, jti) tuple.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        or timedelta(days=settings.refresh_token_expire_days)
    )
    jti = str(uuid.uuid4())

    payload = {
        "sub": subject,
        "jti": jti,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }

    encoded = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)
    return encoded, jti


def decode_token(token: str, settings: JWTSettings) -> dict:
    """
    Decode and return raw JWT payload without verification.
    Use only for inspection; use verify_token for security.
    """
    return jwt.decode(
        token,
        settings.secret_key,
        algorithms=[settings.algorithm],
        options={"verify_exp": False},
    )


def verify_token(token: str, settings: JWTSettings) -> TokenPayload:
    """
    Verify and decode a JWT token. Raises InvalidTokenError on failure.
    """
    from rainer_common.exceptions import InvalidTokenError

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        return TokenPayload(**payload)
    except ExpiredSignatureError:
        raise InvalidTokenError("Token has expired")
    except JWTError as exc:
        raise InvalidTokenError(f"Token is invalid: {exc}")
