"""Add vault column to documents table.

Adds:
- ``vault`` — String(50), default ``"qa_draft"``, segregates
  QA-released vs QA-draft documents (§7.1).

Revision ID: 005_add_vault_column
Revises: 004_taxonomies_folders_controlled_copies
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa

revision = "005_add_vault_column"
down_revision = "004_taxonomies_folders_controlled_copies"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "documents",
        sa.Column("vault", sa.String(50), nullable=False, server_default="qa_draft"),
    )


def downgrade() -> None:
    op.drop_column("documents", "vault")
