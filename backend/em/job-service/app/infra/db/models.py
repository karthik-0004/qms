"""Job Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Index


class Base(DeclarativeBase):
    pass


class Job(Base):
    """Async background job record."""

    __tablename__ = "jobs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    job_type: Mapped[str] = mapped_column(String(100), nullable=False)
    # ai_analysis, report_generation, data_export, etc.
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    # 1=highest, 10=lowest
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # pending → running → complete | failed | retrying | cancelled
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    worker_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    queued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_retry_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_jobs_tenant_status", "tenant_id", "status"),
        Index("idx_jobs_type_status", "job_type", "status"),
        Index("idx_jobs_queued_at", "queued_at"),
        Index("idx_jobs_next_retry", "next_retry_at"),
    )
