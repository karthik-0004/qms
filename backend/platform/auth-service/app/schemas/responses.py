"""Auth Service — Pydantic response schemas."""

from datetime import datetime

from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    email: str
    role: str
    tenant_id: str | None
    mfa_enabled: bool


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserInfo


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class MFASetupResponse(BaseModel):
    secret: str
    provisioning_uri: str
    qr_code_url: str


class AccessKeyResponse(BaseModel):
    id: str
    raw_key: str
    key_prefix: str
    service_name: str
    scopes: list[str]
    expires_at: str | None
    warning: str


class AccessKeyListItem(BaseModel):
    id: str
    key_prefix: str
    service_name: str
    scopes: list[str]
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None
    expires_at: datetime | None
