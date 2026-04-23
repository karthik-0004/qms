"""Tenant Service — Pydantic request schemas."""

from pydantic import BaseModel, Field, field_validator


class CreateTenantRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=100)
    products: list[str] = Field(min_length=1)
    tier: str = Field(default="starter")
    region: str = Field(default="us-east-1")

    @field_validator("products")
    @classmethod
    def validate_products(cls, v: list[str]) -> list[str]:
        allowed = {"qms", "em", "ccv"}
        for p in v:
            if p not in allowed:
                raise ValueError(f"Invalid product '{p}'. Allowed: {allowed}")
        return v

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str) -> str:
        allowed = {"starter", "professional", "enterprise"}
        if v not in allowed:
            raise ValueError(f"Invalid tier '{v}'. Allowed: {allowed}")
        return v


class UpdateTenantRequest(BaseModel):
    tenant_name: str | None = Field(default=None, min_length=2, max_length=100)
    tier: str | None = None
    products: list[str] | None = None

    @field_validator("tier")
    @classmethod
    def validate_tier(cls, v: str | None) -> str | None:
        if v is None:
            return v
        allowed = {"starter", "professional", "enterprise"}
        if v not in allowed:
            raise ValueError(f"Invalid tier '{v}'. Allowed: {allowed}")
        return v


class UpdateTenantSettingsRequest(BaseModel):
    max_users: int | None = Field(default=None, ge=1, le=10000)
    max_storage_gb: int | None = Field(default=None, ge=1, le=10000)
    features: dict | None = None
    branding: dict | None = None
    smtp_config: dict | None = None
    webhook_urls: list[str] | None = None
    timezone: str | None = None
    locale: str | None = None
