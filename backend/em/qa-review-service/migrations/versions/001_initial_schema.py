"""Initial schema — qa_reviews, qa_review_comments.

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
        "qa_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("plate_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("decision", sa.String(50), nullable=True),
        sa.Column("override_colony_count", sa.Integer(), nullable=True),
        sa.Column("override_reason", sa.Text(), nullable=True),
        sa.Column("ai_result_accepted", sa.Boolean(), nullable=True),
        sa.Column("annotations", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_qa_reviews_tenant_status", "qa_reviews", ["tenant_id", "status"])
    op.create_index("idx_qa_reviews_plate", "qa_reviews", ["plate_id"])
    op.create_index("idx_qa_reviews_reviewer", "qa_reviews", ["reviewer_id", "status"])
    op.create_index("idx_qa_reviews_due_at", "qa_reviews", ["due_at"])

    op.create_table(
        "qa_review_comments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("review_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("qa_review_comments")
    op.drop_index("idx_qa_reviews_due_at", table_name="qa_reviews")
    op.drop_index("idx_qa_reviews_reviewer", table_name="qa_reviews")
    op.drop_index("idx_qa_reviews_plate", table_name="qa_reviews")
    op.drop_index("idx_qa_reviews_tenant_status", table_name="qa_reviews")
    op.drop_table("qa_reviews")
