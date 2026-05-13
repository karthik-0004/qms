"""Equipment Service — SQLAlchemy ORM models (Tenant DB)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Equipment(Base):
    __tablename__ = "equipment"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    asset_tag: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    equipment_type: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(255), nullable=True)
    model: Mapped[str | None] = mapped_column(String(255), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    requires_calibration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    calibration_frequency_days: Mapped[int | None] = mapped_column(nullable=True)
    last_calibration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_calibration_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    requires_pm: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pm_frequency_days: Mapped[int | None] = mapped_column(nullable=True)
    last_pm_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    next_pm_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    purchase_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    warranty_expiry: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    calibration_records: Mapped[list[CalibrationRecord]] = relationship(
        back_populates="equipment",
        cascade="all, delete-orphan",
        order_by="CalibrationRecord.calibration_date.desc()",
    )

    __table_args__ = (
        Index("idx_equipment_tenant_tag", "tenant_id", "asset_tag", unique=True),
        Index("idx_equipment_tenant_status", "tenant_id", "status"),
        Index("idx_equipment_calibration_due", "next_calibration_date"),
    )


class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    equipment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("equipment.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False, index=True)
    calibration_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    performed_by: Mapped[str] = mapped_column(String(255), nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    standards_used: Mapped[str | None] = mapped_column(Text, nullable=True)
    as_found_readings: Mapped[str | None] = mapped_column(Text, nullable=True)
    as_left_readings: Mapped[str | None] = mapped_column(Text, nullable=True)
    result: Mapped[str] = mapped_column(String(10), nullable=False)
    measurement_uncertainty: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    next_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    certificate_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    equipment: Mapped[Equipment] = relationship(back_populates="calibration_records")
