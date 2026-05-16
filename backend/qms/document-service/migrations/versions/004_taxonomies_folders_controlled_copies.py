"""Add taxonomies, folders, controlled_copies tables + Document taxonomy/review columns.

Creates:
- ``taxonomies``  — Document taxonomy/category groups
- ``folders``     — Hierarchical folders within a taxonomy
- ``controlled_copies`` — Issued/recalled controlled copy tracking
- New columns on ``documents``: taxonomy_id, folder_id, category_path,
  review_interval_days, next_review_date, obsolete_reason

Revision ID: 004_taxonomies_folders_controlled_copies
Revises: 003_effective_superseded_and_editor_columns
Create Date: 2026-05-16
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "004_taxonomies_folders_controlled_copies"
down_revision = "003_effective_superseded_and_editor_columns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── taxonomies ──────────────────────────────────────────────────────
    op.create_table(
        "taxonomies",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_taxonomies_tenant", "taxonomies", ["tenant_id"])

    # ── folders ─────────────────────────────────────────────────────────
    op.create_table(
        "folders",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("taxonomy_id", sa.String(36), nullable=False),
        sa.Column("parent_id", sa.String(36), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("path", sa.Text(), nullable=False, server_default=""),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_by", sa.String(36), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["taxonomy_id"], ["taxonomies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["folders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_folders_tenant", "folders", ["tenant_id"])
    op.create_index("idx_folders_taxonomy", "folders", ["taxonomy_id"])
    op.create_index("idx_folders_parent", "folders", ["parent_id"])

    # ── controlled_copies ───────────────────────────────────────────────
    op.create_table(
        "controlled_copies",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("version", sa.String(20), nullable=False),
        sa.Column("copy_number", sa.String(50), nullable=False),
        sa.Column("issued_to", sa.String(255), nullable=False),
        sa.Column("issued_by", sa.String(36), nullable=False),
        sa.Column("issued_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recalled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_cc_document", "controlled_copies", ["document_id"])
    op.create_index("idx_cc_status", "controlled_copies", ["status"])

    # ── New columns on documents ────────────────────────────────────────
    op.add_column("documents", sa.Column("taxonomy_id", sa.String(36), nullable=True))
    op.add_column("documents", sa.Column("folder_id", sa.String(36), nullable=True))
    op.add_column("documents", sa.Column("category_path", sa.Text(), nullable=True))
    op.add_column("documents", sa.Column("review_interval_days", sa.Integer(), nullable=True))
    op.add_column("documents", sa.Column("next_review_date", sa.DateTime(timezone=True), nullable=True))
    op.add_column("documents", sa.Column("obsolete_reason", sa.Text(), nullable=True))

    op.create_index("idx_documents_taxonomy", "documents", ["taxonomy_id"])
    op.create_index("idx_documents_folder", "documents", ["folder_id"])

    # Foreign keys (added after columns exist)
    op.create_foreign_key(
        "fk_documents_taxonomy", "documents", "taxonomies",
        ["taxonomy_id"], ["id"], ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_documents_folder", "documents", "folders",
        ["folder_id"], ["id"], ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("fk_documents_folder", "documents", type_="foreignkey")
    op.drop_constraint("fk_documents_taxonomy", "documents", type_="foreignkey")
    op.drop_index("idx_documents_folder", table_name="documents")
    op.drop_index("idx_documents_taxonomy", table_name="documents")
    op.drop_column("documents", "obsolete_reason")
    op.drop_column("documents", "next_review_date")
    op.drop_column("documents", "review_interval_days")
    op.drop_column("documents", "category_path")
    op.drop_column("documents", "folder_id")
    op.drop_column("documents", "taxonomy_id")
    op.drop_table("controlled_copies")
    op.drop_table("folders")
    op.drop_table("taxonomies")
