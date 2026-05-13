"""Training Service — SQLAlchemy ORM models (Tenant DB)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


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
    duration_hours: Mapped[float | None] = mapped_column(nullable=True)
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
