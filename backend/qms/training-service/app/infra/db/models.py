"""Training Service — SQLAlchemy ORM models (Tenant DB)."""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ── Existing tables (Phase 1) ───────────────────────────────────────────────


class TrainingCourse(Base):
    __tablename__ = "training_courses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    course_code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    course_type: Mapped[str] = mapped_column(String(100), nullable=False, default="online")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    duration_hours: Mapped[float | None] = mapped_column(Float, nullable=True)
    passing_score: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    requires_certification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    recurrence_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_tc_tenant_code", "tenant_id", "course_code", unique=True),
    )

    assignments: Mapped[list["TrainingAssignment"]] = relationship(
        "TrainingAssignment", back_populates="course"
    )


class TrainingAssignment(Base):
    __tablename__ = "training_assignments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    course_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("training_courses.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    assigned_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="assigned")
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cert_expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    course: Mapped["TrainingCourse"] = relationship("TrainingCourse", back_populates="assignments")

    __table_args__ = (
        Index("idx_ta_tenant_user", "tenant_id", "user_id", "status"),
        Index("idx_ta_course_user", "course_id", "user_id", unique=True),
    )

    @property
    def course_title(self) -> str | None:
        c = self.course
        return c.title if c is not None else None


# ── Phase 4 — Job Codes ─────────────────────────────────────────────────────


class JobCode(Base):
    """A job code defines a role with required training courses."""

    __tablename__ = "job_codes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    requires_certification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_jc_tenant_code", "tenant_id", "code", unique=True),
    )

    courses: Mapped[list["JobCodeCourse"]] = relationship("JobCodeCourse", back_populates="job_code")


class JobCodeCourse(Base):
    """Links a required course to a job code."""

    __tablename__ = "job_code_courses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    job_code_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("job_codes.id", ondelete="CASCADE"), nullable=False
    )
    course_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("training_courses.id", ondelete="CASCADE"), nullable=False
    )
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    job_code: Mapped["JobCode"] = relationship("JobCode", back_populates="courses")
    course: Mapped["TrainingCourse"] = relationship()

    __table_args__ = (
        Index("idx_jcc_job_code", "job_code_id"),
        Index("idx_jcc_unique", "job_code_id", "course_id", unique=True),
    )


class JobCodeAssignment(Base):
    """Assigns a user to a job code (tracks their compliance status)."""

    __tablename__ = "job_code_assignments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    job_code_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("job_codes.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    assigned_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    __table_args__ = (
        Index("idx_jca_tenant", "tenant_id"),
        Index("idx_jca_user_job", "user_id", "job_code_id", unique=True),
    )


# ── Phase 4 — Trainers ──────────────────────────────────────────────────────


class Trainer(Base):
    """Registered trainers who can assign and assess training."""

    __tablename__ = "trainers"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    job_code_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("job_codes.id", ondelete="SET NULL"), nullable=True
    )
    qualification: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_tr_tenant_user", "tenant_id", "user_id", unique=True),
    )


# ── Phase 4 — Exams ─────────────────────────────────────────────────────────


class Exam(Base):
    """An exam linked to a training course."""

    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    course_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("training_courses.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    passing_score: Mapped[int] = mapped_column(Integer, nullable=False, default=80)
    duration_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    questions: Mapped[list["ExamQuestion"]] = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")


class ExamQuestion(Base):
    """A question within an exam."""

    __tablename__ = "exam_questions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    exam_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False
    )
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    options: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    correct_answer: Mapped[str] = mapped_column(String(10), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    exam: Mapped["Exam"] = relationship("Exam", back_populates="questions")


class ExamAttempt(Base):
    """Records a user's attempt at an exam."""

    __tablename__ = "exam_attempts"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    exam_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    answers: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="in_progress")
