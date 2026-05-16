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


# ── Phase 4: Job Codes ───────────────────────────────────────────────────────


class JobCodeResponse(BaseModel):
    id: str
    tenant_id: str
    code: str
    title: str
    description: str | None
    department: str | None
    requires_certification: bool
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    course_count: int = 0
    user_count: int = 0
    compliance_pct: float | None = None


class JobCodeCourseResponse(BaseModel):
    id: str
    job_code_id: str
    course_id: str
    course_title: str | None = None
    is_required: bool
    sort_order: int


class JobCodeAssignmentResponse(BaseModel):
    id: str
    tenant_id: str
    job_code_id: str
    user_id: str
    assigned_by: str | None
    assigned_at: datetime
    is_primary: bool


# ── Phase 4: Trainers ────────────────────────────────────────────────────────


class TrainerResponse(BaseModel):
    id: str
    tenant_id: str
    user_id: str
    job_code_id: str | None
    qualification: str | None
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime


# ── Phase 4: Exams ───────────────────────────────────────────────────────────


class ExamResponse(BaseModel):
    id: str
    tenant_id: str
    course_id: str
    course_title: str | None = None
    title: str
    description: str | None
    passing_score: int
    duration_minutes: int | None
    is_active: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    question_count: int = 0


class ExamQuestionResponse(BaseModel):
    id: str
    exam_id: str
    question_text: str
    options: list[str]
    correct_answer: str
    sort_order: int


class ExamAttemptResponse(BaseModel):
    id: str
    tenant_id: str
    exam_id: str
    user_id: str
    score: int | None
    passed: bool | None
    answers: dict | None
    started_at: datetime
    completed_at: datetime | None
    status: str


# ── Phase 4: Dashboard & Status Matrix ───────────────────────────────────────


class TrainingDashboardStats(BaseModel):
    total_courses: int
    total_assignments: int
    completed_assignments: int
    overdue_assignments: int
    in_progress_assignments: int
    pending_assignments: int
    total_job_codes: int
    users_with_overdue: int
    overall_compliance_pct: float
    upcoming_recertifications: int
    total_trainers: int


class JobCodeUserStatus(BaseModel):
    user_id: str
    user_name: str | None = None
    job_code_id: str
    job_code_title: str | None = None
    is_primary: bool
    courses: list["CourseStatusItem"]


class CourseStatusItem(BaseModel):
    course_id: str
    course_title: str
    is_required: bool
    assignment_id: str | None
    status: str | None
    score: int | None
    passed: bool | None
    completed_at: datetime | None
    due_date: datetime | None
