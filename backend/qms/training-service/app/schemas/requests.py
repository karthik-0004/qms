"""Training Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateCourseRequest(BaseModel):
    course_code: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    course_type: str = "online"
    description: str | None = None
    department: str | None = None
    document_id: str | None = None
    duration_hours: float | None = None
    passing_score: int = 80
    requires_certification: bool = False
    recurrence_days: int | None = None
    is_mandatory: bool = False


class AssignTrainingRequest(BaseModel):
    user_id: str
    due_date: datetime | None = None


class CompleteTrainingRequest(BaseModel):
    score: int | None = None
    notes: str | None = None
    e_signature: str | None = Field(
        default=None,
        min_length=1,
        description="Required when the course requires certification",
    )
