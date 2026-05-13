"""Add calibration_records table.

Revision ID: 002_calibration_records
Revises: 001_initial_schema
Create Date: 2026-05-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "002_calibration_records"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "calibration_records",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("equipment_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("calibration_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("performed_by", sa.String(255), nullable=False),
        sa.Column("passed", sa.Boolean(), nullable=False),
        sa.Column("result", sa.String(10), nullable=False),
        sa.Column("standards_used", sa.Text(), nullable=True),
        sa.Column("as_found_readings", sa.Text(), nullable=True),
        sa.Column("as_left_readings", sa.Text(), nullable=True),
        sa.Column("measurement_uncertainty", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("next_due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("certificate_file_id", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["equipment_id"], ["equipment.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("idx_calibration_records_equipment_id", "calibration_records", ["equipment_id"])
    op.create_index("idx_calibration_records_tenant_id", "calibration_records", ["tenant_id"])


def downgrade() -> None:
    op.drop_index("idx_calibration_records_tenant_id", table_name="calibration_records")
    op.drop_index("idx_calibration_records_equipment_id", table_name="calibration_records")
    op.drop_table("calibration_records")
