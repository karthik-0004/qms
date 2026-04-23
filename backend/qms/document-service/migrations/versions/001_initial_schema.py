"""Initial schema — documents, document_versions, document_acknowledgments.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-03-06
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("doc_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("doc_type", sa.String(100), nullable=False),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="draft"),
        sa.Column("current_version", sa.String(20), nullable=False, server_default="1.0"),
        sa.Column("owner_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("approver_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("file_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("regulatory_frameworks", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("is_controlled", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_documents_tenant_status", "documents", ["tenant_id", "status"])
    op.create_index("idx_documents_tenant_number", "documents", ["tenant_id", "doc_number"], unique=True)
    op.create_index("idx_documents_owner", "documents", ["owner_id"])
    op.create_index("idx_documents_review_date", "documents", ["review_date"])

    op.create_table(
        "document_versions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("file_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("change_summary", sa.Text(), nullable=True),
        sa.Column("approved_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("signature_hash", sa.String(255), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "document_acknowledgments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("ip_address", sa.String(50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("document_acknowledgments")
    op.drop_table("document_versions")
    op.drop_index("idx_documents_review_date", table_name="documents")
    op.drop_index("idx_documents_owner", table_name="documents")
    op.drop_index("idx_documents_tenant_number", table_name="documents")
    op.drop_index("idx_documents_tenant_status", table_name="documents")
    op.drop_table("documents")
