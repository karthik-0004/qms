"""AI Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Index


class Base(DeclarativeBase):
    pass


class AnalysisRun(Base):
    """AI analysis execution record for a plate image."""

    __tablename__ = "analysis_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    plate_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    image_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    job_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    # pending → running → complete | failed
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    triggered_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_analysis_runs_plate", "plate_id"),
        Index("idx_analysis_runs_image", "image_id"),
        Index("idx_analysis_runs_tenant_status", "tenant_id", "status"),
    )


class AnalysisResult(Base):
    """AI detection outcome for a completed analysis run."""

    __tablename__ = "analysis_results"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    analysis_run_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    plate_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    colony_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    colony_positions: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    confidence_score: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    contamination_detected: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    contamination_type: Mapped[str | None] = mapped_column(String(200), nullable=True)
    anomaly_flags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    raw_output: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_analysis_results_run", "analysis_run_id"),
        Index("idx_analysis_results_plate", "plate_id"),
    )
