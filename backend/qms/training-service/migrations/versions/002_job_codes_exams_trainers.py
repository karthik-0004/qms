"""Phase 4 — job_codes, job_code_courses, job_code_assignments, trainers, exams, exam_questions, exam_attempts.

Revision ID: 002_job_codes_exams_trainers
Revises: 001_initial_schema
Create Date: 2026-05-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_job_codes_exams_trainers"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ── Job Codes ──────────────────────────────────────────────────────────
    op.create_table(
        "job_codes",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("code", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("requires_certification", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_jc_tenant_code", "job_codes", ["tenant_id", "code"], unique=True)

    op.create_table(
        "job_code_courses",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("job_code_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("is_required", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["job_code_id"], ["job_codes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["training_courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_jcc_job_code", "job_code_courses", ["job_code_id"])
    op.create_index("idx_jcc_unique", "job_code_courses", ["job_code_id", "course_id"], unique=True)

    op.create_table(
        "job_code_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("job_code_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["job_code_id"], ["job_codes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_jca_tenant", "job_code_assignments", ["tenant_id"])
    op.create_index("idx_jca_user_job", "job_code_assignments", ["user_id", "job_code_id"], unique=True)

    # ── Trainers ───────────────────────────────────────────────────────────
    op.create_table(
        "trainers",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("job_code_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("qualification", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["job_code_id"], ["job_codes.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_tr_tenant_user", "trainers", ["tenant_id", "user_id"], unique=True)

    # ── Exams ──────────────────────────────────────────────────────────────
    op.create_table(
        "exams",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("course_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default="80"),
        sa.Column("duration_minutes", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["course_id"], ["training_courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "exam_questions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("correct_answer", sa.String(10), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "exam_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("exam_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("score", sa.Integer(), nullable=True),
        sa.Column("passed", sa.Boolean(), nullable=True),
        sa.Column("answers", postgresql.JSONB(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="in_progress"),
        sa.ForeignKeyConstraint(["exam_id"], ["exams.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("exam_attempts")
    op.drop_table("exam_questions")
    op.drop_table("exams")
    op.drop_index("idx_tr_tenant_user", table_name="trainers")
    op.drop_table("trainers")
    op.drop_index("idx_jca_user_job", table_name="job_code_assignments")
    op.drop_index("idx_jca_tenant", table_name="job_code_assignments")
    op.drop_table("job_code_assignments")
    op.drop_index("idx_jcc_unique", table_name="job_code_courses")
    op.drop_index("idx_jcc_job_code", table_name="job_code_courses")
    op.drop_table("job_code_courses")
    op.drop_index("idx_jc_tenant_code", table_name="job_codes")
    op.drop_table("job_codes")
