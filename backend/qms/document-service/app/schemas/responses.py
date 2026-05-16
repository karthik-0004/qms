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
    last_rejection_reason: str | None = None
    authoring_mode: str = "upload"
    content_ast: dict | None = None
    html_snapshot: str | None = None
    editor_nonce: str | None = None
    vault: str = "qa_draft"
    taxonomy_id: str | None = None
    folder_id: str | None = None
    category_path: str | None = None
    review_interval_days: int | None = None
    next_review_date: datetime | None = None
    obsolete_reason: str | None = None
    created_by: str
    created_at: datetime
    updated_at: datetime


class DocumentVersionResponse(BaseModel):
    id: str
    document_id: str
    version: str
    file_id: str | None
    authoring_mode: str = "upload"
    content_ast: dict | None = None
    html_snapshot: str | None = None
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


class DocumentAcknowledgmentResponse(BaseModel):
    id: str
    document_id: str
    user_id: str
    acknowledged_at: datetime
    version: str
    signature_hash: str | None = None
    ip_address: str | None = None


class PendingAcknowledgmentResponse(BaseModel):
    document_id: str
    doc_number: str
    title: str
    version: str
    status: str


class ComplianceStatsResponse(BaseModel):
    total_distribution: int
    acknowledged: int
    pending: int
    compliance_pct: float


# ── §7.1 Taxonomy / Folder / ControlledCopy ─────────────────────────────────

class TaxonomyResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    description: str | None = None
    sort_order: int = 0
    created_by: str
    created_at: datetime
    updated_at: datetime


class FolderResponse(BaseModel):
    id: str
    tenant_id: str
    taxonomy_id: str
    parent_id: str | None = None
    name: str
    description: str | None = None
    path: str
    sort_order: int = 0
    created_by: str
    created_at: datetime
    updated_at: datetime


class ControlledCopyResponse(BaseModel):
    id: str
    document_id: str
    version: str
    copy_number: str
    issued_to: str
    issued_by: str
    issued_at: datetime
    recalled_at: datetime | None = None
    status: str = "active"
    notes: str | None = None


# ── Editor content ──────────────────────────────────────────────────────────

class ContentResponse(BaseModel):
    authoring_mode: str
    content_ast: dict | None = None
    html_snapshot: str | None = None
    editor_nonce: str | None = None
