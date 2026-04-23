"""CRM Service — Pydantic response schemas."""

from datetime import datetime
from uuid import UUID
from pydantic import BaseModel


class CustomerResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    company_name: str
    status: str
    industry: str | None
    website: str | None
    phone: str | None
    email: str | None
    address: str | None
    city: str | None
    state: str | None
    country: str | None
    postal_code: str | None
    notes: str | None
    tags: list
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class ContactResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    first_name: str
    last_name: str
    title: str | None
    email: str | None
    phone: str | None
    mobile: str | None
    is_primary: bool
    created_at: datetime
    updated_at: datetime


class InteractionResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    interaction_type: str
    subject: str
    body: str | None
    contact_id: UUID | None
    created_by: UUID
    created_at: datetime
