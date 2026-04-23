"""Initial schema — analysis_runs, analysis_results.

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
        "analysis_runs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("plate_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("image_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("model_name", sa.String(200), nullable=False),
        sa.Column("model_version", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("duration_seconds", sa.Numeric(10, 3), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("triggered_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_analysis_runs_plate", "analysis_runs", ["plate_id"])
    op.create_index("idx_analysis_runs_image", "analysis_runs", ["image_id"])
    op.create_index("idx_analysis_runs_tenant_status", "analysis_runs", ["tenant_id", "status"])

    op.create_table(
        "analysis_results",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("analysis_run_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("plate_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("colony_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("colony_positions", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("confidence_score", sa.Numeric(5, 4), nullable=False),
        sa.Column("contamination_detected", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("contamination_type", sa.String(200), nullable=True),
        sa.Column("anomaly_flags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("raw_output", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_analysis_results_run", "analysis_results", ["analysis_run_id"])
    op.create_index("idx_analysis_results_plate", "analysis_results", ["plate_id"])


def downgrade() -> None:
    op.drop_index("idx_analysis_results_plate", table_name="analysis_results")
    op.drop_index("idx_analysis_results_run", table_name="analysis_results")
    op.drop_table("analysis_results")
    op.drop_index("idx_analysis_runs_tenant_status", table_name="analysis_runs")
    op.drop_index("idx_analysis_runs_image", table_name="analysis_runs")
    op.drop_index("idx_analysis_runs_plate", table_name="analysis_runs")
    op.drop_table("analysis_runs")
