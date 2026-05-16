"""Complaints Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Complaint(Base):
    __tablename__ = "complaints"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    complaint_number: Mapped[str] = mapped_column(String(100), nullable=False)
    customer_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    received_via: Mapped[str] = mapped_column(String(50), nullable=False, default="email")
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="minor")
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="open")
    investigator_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    capa_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_complaints_tenant_status", "tenant_id", "status"),
        Index("idx_complaints_tenant_number", "tenant_id", "complaint_number", unique=True),
        Index("idx_complaints_tenant_severity", "tenant_id", "severity"),
        Index("idx_complaints_investigator", "investigator_id"),
    )
