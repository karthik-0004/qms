"""Initial schema — plates, plate_status_history.

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
        "plates",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("barcode", sa.String(100), nullable=False),
        sa.Column("sample_type", sa.String(100), nullable=False),
        sa.Column("media_type", sa.String(100), nullable=False),
        sa.Column("incubation_temp_celsius", sa.Numeric(5, 2), nullable=True),
        sa.Column("incubation_hours", sa.Integer(), nullable=True),
        sa.Column("location_code", sa.String(200), nullable=True),
        sa.Column("lot_number", sa.String(100), nullable=True),
        sa.Column("operator_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="registered"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("sampled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("incubation_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("incubation_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_plates_tenant_status", "plates", ["tenant_id", "status"])
    op.create_index("idx_plates_barcode", "plates", ["tenant_id", "barcode"])
    op.create_index("idx_plates_sampled_at", "plates", ["tenant_id", "sampled_at"])

    op.create_table(
        "plate_status_history",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("plate_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("from_status", sa.String(50), nullable=True),
        sa.Column("to_status", sa.String(50), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("plate_status_history")
    op.drop_index("idx_plates_sampled_at", table_name="plates")
    op.drop_index("idx_plates_barcode", table_name="plates")
    op.drop_index("idx_plates_tenant_status", table_name="plates")
    op.drop_table("plates")
