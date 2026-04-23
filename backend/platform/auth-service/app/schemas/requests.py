"""Auth Service — Pydantic request schemas."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from ..core.security import is_strong_password


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=6)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class MFAVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class MFADisableRequest(BaseModel):
    password: str = Field(min_length=1)


class CreateAccessKeyRequest(BaseModel):
    service_name: str = Field(min_length=1, max_length=100)
    scopes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not is_strong_password(v):
            raise ValueError(
                "Password must be at least 8 characters with uppercase, lowercase, "
                "digit, and special character."
            )
        return v


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1)
    new_password: str = Field(min_length=8)

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not is_strong_password(v):
            raise ValueError(
                "Password must be at least 8 characters with uppercase, lowercase, "
                "digit, and special character."
            )
        return v
