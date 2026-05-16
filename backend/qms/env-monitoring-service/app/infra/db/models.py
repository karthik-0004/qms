"""Env Monitoring Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class MonitoringPoint(Base):
    __tablename__ = "monitoring_points"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    point_id: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str] = mapped_column(String(255), nullable=False)
    parameter: Mapped[str] = mapped_column(String(100), nullable=False)
    alert_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    action_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    frequency_type: Mapped[str] = mapped_column(String(50), nullable=False)
    frequency_value: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    last_reading_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_reading_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_monitoring_points_tenant_status", "tenant_id", "status"),
        Index("idx_monitoring_points_tenant_point_id", "tenant_id", "point_id", unique=True),
    )


class MonitoringReading(Base):
    __tablename__ = "monitoring_readings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    point_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("monitoring_points.id", ondelete="CASCADE"), nullable=False
    )
    value: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_by_user_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="within_limits")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_monitoring_readings_point_id", "point_id"),
        Index("idx_monitoring_readings_tenant_status", "tenant_id", "status"),
        Index("idx_monitoring_readings_recorded_at", "recorded_at"),
    )
