"""Document Service — SQLAlchemy ORM models (Tenant DB)."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    doc_number: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    doc_type: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    current_version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    owner_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    approver_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    effective_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    workflow_instance_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    file_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    tags: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    regulatory_frameworks: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    is_controlled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    authoring_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="upload")
    content_ast: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    html_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    editor_nonce: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # §7.1 — Document vault (segregates QA-released vs QA-draft)
    vault: Mapped[str] = mapped_column(String(50), nullable=False, default="qa_draft")

    # §7.1 — Taxonomy & folder associations
    taxonomy_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("taxonomies.id", ondelete="SET NULL"), nullable=True
    )
    folder_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("folders.id", ondelete="SET NULL"), nullable=True
    )
    category_path: Mapped[str | None] = mapped_column(Text, nullable=True)

    # §7.1 — Review lifecycle
    review_interval_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_review_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    obsolete_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_documents_tenant_status", "tenant_id", "status"),
        Index("idx_documents_tenant_number", "tenant_id", "doc_number", unique=True),
        Index("idx_documents_owner", "owner_id"),
        Index("idx_documents_review_date", "review_date"),
        Index("idx_documents_taxonomy", "taxonomy_id"),
        Index("idx_documents_folder", "folder_id"),
    )


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    file_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    authoring_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="upload")
    content_ast: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    html_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    signature_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class DocumentAcknowledgment(Base):
    __tablename__ = "document_acknowledgments"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    document_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    signature_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(String(50), nullable=True)


class DocumentDistribution(Base):
    __tablename__ = "document_distribution"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    added_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (Index("idx_document_distribution_document", "document_id"),)


class Taxonomy(Base):
    """Document taxonomy/category — e.g. "Quality Manual", "SOPs", "Forms"."""

    __tablename__ = "taxonomies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_taxonomies_tenant", "tenant_id"),
    )


class Folder(Base):
    """Hierarchical folders within a taxonomy."""

    __tablename__ = "folders"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    taxonomy_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("taxonomies.id", ondelete="CASCADE"), nullable=False
    )
    parent_id: Mapped[str | None] = mapped_column(
        UUID(as_uuid=False), ForeignKey("folders.id", ondelete="CASCADE"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    path: Mapped[str] = mapped_column(Text, nullable=False, default="")
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_folders_tenant", "tenant_id"),
        Index("idx_folders_taxonomy", "taxonomy_id"),
        Index("idx_folders_parent", "parent_id"),
    )


class ControlledCopy(Base):
    """Issued controlled copies of a document version."""

    __tablename__ = "controlled_copies"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False
    )
    version: Mapped[str] = mapped_column(String(20), nullable=False)
    copy_number: Mapped[str] = mapped_column(String(50), nullable=False)
    issued_to: Mapped[str] = mapped_column(String(255), nullable=False)
    issued_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recalled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("idx_cc_document", "document_id"),
        Index("idx_cc_status", "status"),
    )
