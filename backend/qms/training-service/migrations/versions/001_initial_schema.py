"""Initial schema — training_courses, training_assignments.

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
        "training_courses",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("course_type", sa.String(100), nullable=False, server_default="online"),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("document_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("duration_hours", sa.Numeric(5, 2), nullable=True),
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("requires_certification", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("recurrence_days", sa.Integer(), nullable=True),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tc_tenant_code", "training_courses", ["tenant_id", "course_code"], unique=True)

    op.create_table(
        "training_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="assigned"),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cert_expiry_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["course_id"], ["training_courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_ta_tenant_user", "training_assignments", ["tenant_id", "user_id", "status"])
    op.create_index("idx_ta_course_user", "training_assignments", ["course_id", "user_id"], unique=True)


def downgrade() -> None:
    op.drop_index("idx_ta_course_user", table_name="training_assignments")
    op.drop_index("idx_ta_tenant_user", table_name="training_assignments")
    op.drop_table("training_assignments")
    op.drop_index("idx_tc_tenant_code", table_name="training_courses")
    op.drop_table("training_courses")
