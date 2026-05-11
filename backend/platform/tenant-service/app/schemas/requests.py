"""Tenant Service — Pydantic request schemas."""

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class PrimaryContact(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=50)


class CompanySection(BaseModel):
    website: str | None = Field(default=None, max_length=512)
    industry: str | None = Field(default=None, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)


class Address(BaseModel):
    address_line1: str | None = Field(default=None, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    city: str | None = Field(default=None, max_length=120)
    state: str | None = Field(default=None, max_length=120)
    country: str | None = Field(default=None, max_length=120)
    postal_code: str | None = Field(default=None, max_length=32)


class BillingSection(BaseModel):
    billing_email: EmailStr | None = None
    billing_phone: str | None = Field(default=None, max_length=50)
    tax_id: str | None = Field(default=None, max_length=100)
    billing_address_same_as_address: bool = True
    billing_address: Address | None = None


class TenantDefaults(BaseModel):
    timezone: str = Field(default="UTC", max_length=100)
    locale: str = Field(default="en-US", max_length=20)


class CreateTenantRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=100)
    products: list[str] = Field(min_length=1)
    tier: str = Field(default="starter")
    region: str = Field(default="us-east-1")
    primary_contact: PrimaryContact
    company: CompanySection | None = None
    address: Address | None = None
    billing: BillingSection | None = None
    tenant_defaults: TenantDefaults | None = None

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


class ResendWelcomeEmailRequest(BaseModel):
    """Which tenant’s primary admin should receive the welcome email again."""

    tenant_id: UUID


class UpdateTenantSettingsRequest(BaseModel):
    max_users: int | None = Field(default=None, ge=1, le=10000)
    max_storage_gb: int | None = Field(default=None, ge=1, le=10000)
    features: dict | None = None
    branding: dict | None = None
    smtp_config: dict | None = None
    webhook_urls: list[str] | None = None
    timezone: str | None = None
    locale: str | None = None
