"""QA Review Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class ReviewResponse(BaseModel):
    id: str
    tenant_id: str
    plate_id: str
    analysis_run_id: str
    status: str
    priority: str
    reviewer_id: str | None
    assigned_at: datetime | None
    review_started_at: datetime | None
    review_completed_at: datetime | None
    decision: str | None
    review_notes: str | None
    override_colony_count: int | None
    override_reason: str | None
    ai_result_accepted: bool | None
    due_at: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class CommentResponse(BaseModel):
    id: str
    review_id: str
    tenant_id: str
    author_id: str
    body: str
    is_internal: bool
    created_at: datetime
