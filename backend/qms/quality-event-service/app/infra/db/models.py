"""Quality Event Service — SQLAlchemy ORM models (Tenant DB)."""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class QualityEvent(Base):
    __tablename__ = "quality_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    event_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="minor")
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium")
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    detected_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    immediate_action: Mapped[str | None] = mapped_column(Text, nullable=True)
    capa_required: Mapped[bool] = mapped_column(nullable=False, default=False)
    capa_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    attachments: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_qe_tenant_status", "tenant_id", "status"),
        Index("idx_qe_tenant_number", "tenant_id", "event_number", unique=True),
        Index("idx_qe_assigned_to", "assigned_to"),
    )
