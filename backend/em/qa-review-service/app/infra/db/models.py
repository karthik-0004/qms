"""QA Review Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Index


class Base(DeclarativeBase):
    pass


class QAReview(Base):
    """QA review record for a plate analysis result."""

    __tablename__ = "qa_reviews"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    plate_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    analysis_run_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    reviewer_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # pending → in_review → approved | rejected | on_hold
    decision: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # approved, rejected, escalated
    override_colony_count: Mapped[int | None] = mapped_column(nullable=True)
    override_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_result_accepted: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    annotations: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="normal")
    # normal, urgent, critical
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_qa_reviews_tenant_status", "tenant_id", "status"),
        Index("idx_qa_reviews_plate", "plate_id"),
        Index("idx_qa_reviews_reviewer", "reviewer_id", "status"),
        Index("idx_qa_reviews_due_at", "due_at"),
    )


class QAReviewComment(Base):
    """Timestamped comment thread on a QA review."""

    __tablename__ = "qa_review_comments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    review_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    author_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_internal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
