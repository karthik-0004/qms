"""Add EFFECTIVE/SUPERSEDED states and editor-integration columns.

Adds:
- authoring_mode, content_ast, html_snapshot, editor_nonce to documents
- authoring_mode, content_ast, html_snapshot to document_versions

These columns are needed for D-4 (state machine expansion) and
§4.3 editor integration (content_ast/html_snapshot per-version snapshots).

Revision ID: 003_effective_superseded_and_editor_columns
Revises: 002_document_distribution
Create Date: 2026-05-15
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "003_effective_superseded_and_editor_columns"
down_revision = "002_document_distribution"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Widen alembic version column to support longer revision IDs
    op.execute("ALTER TABLE alembic_version_document_service ALTER COLUMN version_num TYPE VARCHAR(255)")

    # Document table — editor integration columns
    op.add_column("documents", sa.Column("authoring_mode", sa.String(20), nullable=False, server_default="upload"))
    op.add_column("documents", sa.Column("content_ast", postgresql.JSONB(), nullable=True))
    op.add_column("documents", sa.Column("html_snapshot", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("editor_nonce", sa.String(64), nullable=True))

    # DocumentVersion table — per-version snapshots
    op.add_column("document_versions", sa.Column("authoring_mode", sa.String(20), nullable=False, server_default="upload"))
    op.add_column("document_versions", sa.Column("content_ast", postgresql.JSONB(), nullable=True))
    op.add_column("document_versions", sa.Column("html_snapshot", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("document_versions", "html_snapshot")
    op.drop_column("document_versions", "content_ast")
    op.drop_column("document_versions", "authoring_mode")
    op.drop_column("documents", "editor_nonce")
    op.drop_column("documents", "html_snapshot")
    op.drop_column("documents", "content_ast")
    op.drop_column("documents", "authoring_mode")
