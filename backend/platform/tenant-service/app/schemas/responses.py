"""Tenant Service — Pydantic response schemas."""

from datetime import datetime

from pydantic import BaseModel


class TenantResponse(BaseModel):
    id: str
    tenant_name: str
    slug: str
    db_name: str
    status: str
    tier: str
    products: list[str]
    region: str
    created_at: datetime
    updated_at: datetime


class TenantSettingsResponse(BaseModel):
    id: str
    tenant_id: str
    max_users: int
    max_storage_gb: int
    features: dict
    branding: dict
    webhook_urls: list[str]
    timezone: str
    locale: str
    created_at: datetime
    updated_at: datetime
