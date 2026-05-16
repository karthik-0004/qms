"""Document Service — Pydantic request schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateDocumentRequest(BaseModel):
    doc_number: str | None = Field(default=None, min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    doc_type: str = Field(min_length=1, max_length=100)
    description: str | None = None
    department: str | None = None
    owner_id: str | None = None
    tags: list[str] = []
    regulatory_frameworks: list[str] = []
    file_id: str | None = None


class UpdateDocumentRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    department: str | None = None
    owner_id: str | None = None
    approver_id: str | None = None
    tags: list[str] | None = None
    regulatory_frameworks: list[str] | None = None
    file_id: str | None = None


class SubmitForReviewRequest(BaseModel):
    approver_id: str | None = None
    comment: str | None = None


class ApproveDocumentRequest(BaseModel):
    signature: str = Field(min_length=1, description="E-signature passphrase or token")
    comment: str | None = None
    effective_date: datetime | None = None
    review_date: datetime | None = None


class RejectDocumentRequest(BaseModel):
    reason: str = Field(min_length=1)


class AddDistributionMemberRequest(BaseModel):
    user_id: str = Field(min_length=1)


class CreateVersionRequest(BaseModel):
    change_type: str = Field(default="major", pattern=r"^(major|minor)$")
    change_summary: str = Field(min_length=1, max_length=1000)
    file_id: str | None = None


class AcknowledgeDocumentRequest(BaseModel):
    signature: str = Field(min_length=1, description="E-signature passphrase")
    ip_address: str | None = None


# ── §7.1 Taxonomy / Folder / ControlledCopy ─────────────────────────────────

class CreateTaxonomyRequest(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    sort_order: int = 0


class UpdateTaxonomyRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    sort_order: int | None = None


class CreateFolderRequest(BaseModel):
    taxonomy_id: str = Field(min_length=1)
    name: str = Field(min_length=1, max_length=200)
    parent_id: str | None = None
    description: str | None = None
    path: str = ""
    sort_order: int = 0


class UpdateFolderRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    parent_id: str | None = None
    path: str | None = None
    sort_order: int | None = None


class IssueControlledCopyRequest(BaseModel):
    copy_number: str = Field(min_length=1, max_length=50)
    issued_to: str = Field(min_length=1, max_length=255)
    notes: str | None = None


# ── Editor content (Mode A) ─────────────────────────────────────────────────

class SaveContentRequest(BaseModel):
    authoring_mode: str = Field(default="editor", pattern=r"^(editor|upload)$")
    content_ast: dict | None = None
    html_snapshot: str | None = None
