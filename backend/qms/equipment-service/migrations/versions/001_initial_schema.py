"""Initial schema — equipment.

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
        "equipment",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("asset_tag", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("equipment_type", sa.String(100), nullable=False),
        sa.Column("manufacturer", sa.String(255), nullable=True),
        sa.Column("model", sa.String(255), nullable=True),
        sa.Column("serial_number", sa.String(100), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("requires_calibration", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("calibration_frequency_days", sa.Integer(), nullable=True),
        sa.Column("last_calibration_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_calibration_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("requires_pm", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("pm_frequency_days", sa.Integer(), nullable=True),
        sa.Column("last_pm_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_pm_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purchase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("warranty_expiry", sa.DateTime(timezone=True), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_equipment_tenant_tag", "equipment", ["tenant_id", "asset_tag"], unique=True)
    op.create_index("idx_equipment_tenant_status", "equipment", ["tenant_id", "status"])
    op.create_index("idx_equipment_calibration_due", "equipment", ["next_calibration_date"])


def downgrade() -> None:
    op.drop_index("idx_equipment_calibration_due", table_name="equipment")
    op.drop_index("idx_equipment_tenant_status", table_name="equipment")
    op.drop_index("idx_equipment_tenant_tag", table_name="equipment")
    op.drop_table("equipment")
