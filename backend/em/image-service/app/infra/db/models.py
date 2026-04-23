"""Image Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class PlateImage(Base):
    """Captured image for an environmental monitoring plate."""

    __tablename__ = "plate_images"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    plate_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    image_key: Mapped[str] = mapped_column(String(500), nullable=False)
    image_type: Mapped[str] = mapped_column(String(50), nullable=False)  # brightfield, fluorescence, uv
    file_size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    width_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height_px: Mapped[int | None] = mapped_column(Integer, nullable=True)
    resolution_dpi: Mapped[int | None] = mapped_column(Integer, nullable=True)
    magnification: Mapped[float | None] = mapped_column(Numeric(8, 2), nullable=True)
    camera_settings: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    is_primary: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="uploaded")
    processing_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    uploaded_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        __import__("sqlalchemy").Index("idx_plate_images_plate", "plate_id"),
        __import__("sqlalchemy").Index("idx_plate_images_tenant_status", "tenant_id", "status"),
    )
