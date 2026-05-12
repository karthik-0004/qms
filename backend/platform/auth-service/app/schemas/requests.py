"""Auth Service — Pydantic request schemas."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ..core.security import is_strong_password
from ..core.validators import validate_request_email


class BootstrapTenantAdminRequest(BaseModel):
    tenant_id: str = Field(min_length=1)
    email: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    role: str = Field(default="tenant_admin", max_length=50)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_request_email(v)


class BootstrapCompanyAdminRequest(BaseModel):
    """Bootstrap a company_admin user (tenant_admin caller only)."""
    email: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    company_id: str = Field(min_length=1, description="The company this admin belongs to")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_request_email(v)


class BootstrapCompanyUserRequest(BaseModel):
    """Bootstrap a company_user (company_admin or tenant_admin caller)."""
    email: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    company_id: str | None = Field(default=None, description="Company to assign; falls back to caller's company_id")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_request_email(v)


class BootstrapTenantUserRequest(BaseModel):
    """Bootstrap a tenant_user auth account (tenant_admin caller only)."""
    email: str
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_request_email(v)


def _normalize_and_validate_mfa_code(value: str) -> str:
    code = value.strip().replace(" ", "")
    if len(code) != 6 or not code.isdigit():
        raise ValueError("MFA code must be exactly 6 digits.")
    return code


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=1)
    mfa_code: str | None = Field(default=None, min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_request_email(v)

    @field_validator("mfa_code")
    @classmethod
    def validate_mfa_code(cls, v: str | None) -> str | None:
        if v is None:
            return None
        return _normalize_and_validate_mfa_code(v)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class MFAVerifyRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        return _normalize_and_validate_mfa_code(v)


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
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        return validate_request_email(v)


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
