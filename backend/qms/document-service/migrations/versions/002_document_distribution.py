"""Add document_distribution and last_rejection_reason.

Revision ID: 002_document_distribution
Revises: 001_initial_schema
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_document_distribution"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("documents", sa.Column("last_rejection_reason", sa.Text(), nullable=True))
    op.create_table(
        "document_distribution",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("added_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("document_id", "user_id", name="uq_document_distribution_doc_user"),
    )
    op.create_index("idx_document_distribution_document", "document_distribution", ["document_id"])


def downgrade() -> None:
    op.drop_index("idx_document_distribution_document", table_name="document_distribution")
    op.drop_table("document_distribution")
    op.drop_column("documents", "last_rejection_reason")
