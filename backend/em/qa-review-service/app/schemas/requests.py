"""QA Review Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateReviewRequest(BaseModel):
    plate_id: str
    analysis_run_id: str
    priority: str = "normal"
    due_at: datetime | None = None


class AssignReviewerRequest(BaseModel):
    reviewer_id: str


class TransitionStatusRequest(BaseModel):
    new_status: str = Field(min_length=1)
    decision: str | None = None
    review_notes: str | None = None
    override_colony_count: int | None = None
    override_reason: str | None = None
    ai_result_accepted: bool | None = None


class AddCommentRequest(BaseModel):
    body: str = Field(min_length=1)
    is_internal: bool = False
