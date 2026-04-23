"""Plate Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Plate(Base):
    """Environmental monitoring sample plate."""

    __tablename__ = "plates"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    barcode: Mapped[str] = mapped_column(String(100), nullable=False)
    sample_type: Mapped[str] = mapped_column(String(100), nullable=False)
    media_type: Mapped[str] = mapped_column(String(100), nullable=False)
    incubation_temp_celsius: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    incubation_hours: Mapped[int | None] = mapped_column(nullable=True)
    location_code: Mapped[str | None] = mapped_column(String(200), nullable=True)
    lot_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    operator_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="registered")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    sampled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    incubation_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    incubation_completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_plates_tenant_status", "tenant_id", "status"),
        Index("idx_plates_barcode", "tenant_id", "barcode"),
        Index("idx_plates_sampled_at", "tenant_id", "sampled_at"),
    )


class PlateStatusHistory(Base):
    """Immutable plate status transition log."""

    __tablename__ = "plate_status_history"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    plate_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(50), nullable=True)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)
    changed_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
