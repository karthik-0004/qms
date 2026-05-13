"""Document Service — Pydantic response schemas."""

from datetime import datetime

from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    tenant_id: str
    doc_number: str
    title: str
    doc_type: str
    department: str | None
    description: str | None
    status: str
    current_version: str
    owner_id: str | None
    approver_id: str | None
    effective_date: datetime | None
    review_date: datetime | None
    expiry_date: datetime | None
    workflow_instance_id: str | None
    file_id: str | None
    tags: list[str]
    regulatory_frameworks: list[str]
    is_controlled: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class DocumentVersionResponse(BaseModel):
    id: str
    document_id: str
    version: str
    file_id: str | None
    change_summary: str | None
    approved_by: str | None
    approved_at: datetime | None
    signature_hash: str | None
    created_by: str
    created_at: datetime


class DocumentDistributionResponse(BaseModel):
    id: str
    document_id: str
    user_id: str
    added_by: str
    created_at: datetime
