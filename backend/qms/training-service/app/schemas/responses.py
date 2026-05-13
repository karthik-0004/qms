"""Training Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class TrainingCourseResponse(BaseModel):
    id: str
    tenant_id: str
    course_code: str
    title: str
    description: str | None
    course_type: str
    department: str | None
    document_id: str | None
    duration_hours: float | None
    passing_score: int
    requires_certification: bool
    recurrence_days: int | None
    is_mandatory: bool
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


class TrainingAssignmentResponse(BaseModel):
    id: str
    tenant_id: str
    course_id: str
    course_title: str | None = None
    user_id: str
    assigned_by: str | None
    due_date: datetime | None
    status: str
    score: int | None
    passed: bool | None
    completed_at: datetime | None
    cert_expiry_date: datetime | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
