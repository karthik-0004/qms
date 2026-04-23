"""CAPA Service — SQLAlchemy ORM models (Tenant DB)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class CAPA(Base):
    __tablename__ = "capas"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    capa_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    capa_type: Mapped[str] = mapped_column(String(50), nullable=False, default="corrective")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="major")
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause_method: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    owner_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    target_close_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    actual_close_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effectiveness_check_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    effectiveness_verified: Mapped[bool] = mapped_column(nullable=False, default=False)
    workflow_instance_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    attachments: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_capas_tenant_status", "tenant_id", "status"),
        Index("idx_capas_tenant_number", "tenant_id", "capa_number", unique=True),
        Index("idx_capas_owner", "owner_id"),
        Index("idx_capas_due_date", "due_date"),
    )


class CAPAAction(Base):
    __tablename__ = "capa_actions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    capa_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("capas.id", ondelete="CASCADE"), nullable=False
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    assigned_to: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
