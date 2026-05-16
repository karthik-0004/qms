"""Audit Management Service — SQLAlchemy ORM models."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AuditChecklist(Base):
    __tablename__ = "audit_checklists"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    items: Mapped[list["AuditChecklistItem"]] = relationship("AuditChecklistItem", back_populates="checklist", cascade="all, delete-orphan")

    __table_args__ = (Index("idx_checklist_tenant", "tenant_id"),)


class AuditChecklistItem(Base):
    __tablename__ = "audit_checklist_items"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    checklist_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("audit_checklists.id", ondelete="CASCADE"), nullable=False
    )
    iso_clause: Mapped[str | None] = mapped_column(String(50), nullable=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_evidence: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    checklist: Mapped["AuditChecklist"] = relationship("AuditChecklist", back_populates="items")


class Audit(Base):
    __tablename__ = "audits"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    audit_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    audit_type: Mapped[str] = mapped_column(String(100), nullable=False, default="internal")
    entity_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    entity_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    criteria: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="scheduled")
    lead_auditor_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    audit_team: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    auditee_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    scheduled_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    performed_start: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    performed_end: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    checklist_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("audit_checklists.id", ondelete="SET NULL"), nullable=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    report_file_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    findings: Mapped[list["AuditFinding"]] = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")
    checklist_responses: Mapped[list["AuditChecklistResponse"]] = relationship("AuditChecklistResponse", back_populates="audit", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_audit_tenant_status", "tenant_id", "status"),
        Index("idx_audit_tenant_number", "tenant_id", "audit_number", unique=True),
        Index("idx_audit_scheduled", "scheduled_start"),
    )


class AuditFinding(Base):
    __tablename__ = "audit_findings"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    audit_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False
    )
    finding_number: Mapped[str] = mapped_column(String(50), nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False, default="observation")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    iso_clause: Mapped[str | None] = mapped_column(String(50), nullable=True)
    evidence_file_ids: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    capa_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    auditee_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    audit: Mapped["Audit"] = relationship("Audit", back_populates="findings")

    __table_args__ = (Index("idx_finding_audit", "audit_id"),)


class AuditChecklistResponse(Base):
    __tablename__ = "audit_checklist_responses"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    audit_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("audits.id", ondelete="CASCADE"), nullable=False
    )
    checklist_item_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    response: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_file_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    responded_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    audit: Mapped["Audit"] = relationship("Audit", back_populates="checklist_responses")
