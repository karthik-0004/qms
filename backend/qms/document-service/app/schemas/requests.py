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
