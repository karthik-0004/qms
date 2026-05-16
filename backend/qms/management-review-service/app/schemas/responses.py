"""Management Review Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class ManagementReviewResponse(BaseModel):
    id: str
    tenant_id: str
    review_number: str
    title: str
    scheduled_date: datetime
    completed_date: datetime | None
    facilitator_id: str | None
    attendees: list
    status: str
    agenda: str | None
    minutes: str | None
    outcomes: list
    action_items: list
    next_review_date: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime
