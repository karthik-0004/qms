"""Management Review Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateManagementReviewRequest(BaseModel):
    review_number: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=1, max_length=255)
    scheduled_date: datetime
    facilitator_id: str | None = None
    attendees: list = []
    agenda: str | None = None
    next_review_date: datetime | None = None


class UpdateManagementReviewRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    scheduled_date: datetime | None = None
    facilitator_id: str | None = None
    attendees: list | None = None
    status: str | None = None
    agenda: str | None = None
    minutes: str | None = None
    outcomes: list | None = None
    action_items: list | None = None
    next_review_date: datetime | None = None
