"""PT Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PTProgram(Base):
    __tablename__ = "pt_programs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    scheme_name: Mapped[str] = mapped_column(String(255), nullable=False)
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)
    frequency_months: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_pt_programs_tenant", "tenant_id"),
        Index("idx_pt_programs_tenant_active", "tenant_id", "is_active"),
    )


class PTRound(Base):
    __tablename__ = "pt_rounds"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    program_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("pt_programs.id", ondelete="CASCADE"), nullable=False
    )
    round_id: Mapped[str] = mapped_column(String(100), nullable=False)
    sample_received_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    result_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reported_result: Mapped[float | None] = mapped_column(Float, nullable=True)
    reference_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    z_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    en_number: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    capa_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_pt_rounds_program_id", "program_id"),
        Index("idx_pt_rounds_tenant_status", "tenant_id", "status"),
    )
