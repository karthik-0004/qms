"""CRM Service — Pydantic request schemas."""

from uuid import UUID
from pydantic import BaseModel, Field


class CreateCustomerRequest(BaseModel):
    company_name: str = Field(min_length=1, max_length=255)
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    notes: str | None = None
    tags: list[str] = []


class UpdateCustomerRequest(BaseModel):
    company_name: str | None = Field(default=None, min_length=1, max_length=255)
    industry: str | None = None
    website: str | None = None
    phone: str | None = None
    email: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    country: str | None = None
    postal_code: str | None = None
    notes: str | None = None
    tags: list[str] | None = None


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)


class AddContactRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    is_primary: bool = False
    title: str | None = None
    email: str | None = None
    phone: str | None = None
    mobile: str | None = None


class LogInteractionRequest(BaseModel):
    interaction_type: str = Field(min_length=1)
    subject: str = Field(min_length=1, max_length=255)
    body: str | None = None
    contact_id: UUID | None = None
    scheduled_at: str | None = None
    duration_minutes: int | None = None
