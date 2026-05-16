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


# ── Phase 4: Job Codes ───────────────────────────────────────────────────────


class CreateJobCodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    department: str | None = None
    requires_certification: bool = False


class UpdateJobCodeRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    department: str | None = None
    requires_certification: bool | None = None
    is_active: bool | None = None


class LinkCourseToJobCodeRequest(BaseModel):
    course_id: str
    is_required: bool = True
    sort_order: int = 0


class AssignJobCodeRequest(BaseModel):
    user_id: str
    is_primary: bool = False


# ── Phase 4: Trainers ────────────────────────────────────────────────────────


class CreateTrainerRequest(BaseModel):
    user_id: str
    job_code_id: str | None = None
    qualification: str | None = None


class UpdateTrainerRequest(BaseModel):
    job_code_id: str | None = None
    qualification: str | None = None
    is_active: bool | None = None


# ── Phase 4: Exams ───────────────────────────────────────────────────────────


class CreateExamRequest(BaseModel):
    course_id: str
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    passing_score: int = 80
    duration_minutes: int | None = None


class CreateExamQuestionRequest(BaseModel):
    question_text: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
    correct_answer: str = Field(min_length=1, max_length=10)
    sort_order: int = 0


class SubmitExamAttemptRequest(BaseModel):
    answers: dict[str, str]  # question_id -> selected answer
