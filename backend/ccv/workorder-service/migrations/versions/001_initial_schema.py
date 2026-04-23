"""Initial schema — work_orders, work_order_tasks, work_order_notes.

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
        "work_orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("work_order_number", sa.String(100), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="normal"),
        sa.Column("work_order_type", sa.String(100), nullable=False),
        sa.Column("site_address", sa.JSON(), nullable=True),
        sa.Column("site_contact", sa.String(255), nullable=True),
        sa.Column("site_phone", sa.String(50), nullable=True),
        sa.Column("assigned_technician_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("estimated_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("actual_hours", sa.Numeric(8, 2), nullable=True),
        sa.Column("labour_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("parts_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("total_cost", sa.Numeric(12, 2), nullable=True),
        sa.Column("completion_notes", sa.Text(), nullable=True),
        sa.Column("customer_signature", sa.Text(), nullable=True),
        sa.Column("customer_signed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("changed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("work_order_number"),
    )
    op.create_index("idx_wo_tenant", "work_orders", ["tenant_id"])
    op.create_index("idx_wo_customer", "work_orders", ["customer_id"])
    op.create_index("idx_wo_contract", "work_orders", ["contract_id"])
    op.create_index("idx_wo_number", "work_orders", ["work_order_number"])
    op.create_index("idx_wo_technician", "work_orders", ["assigned_technician_id"])

    op.create_table(
        "work_order_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_wot_work_order", "work_order_tasks", ["work_order_id"])

    op.create_table(
        "work_order_notes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("work_order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_internal", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["work_order_id"], ["work_orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_won_work_order", "work_order_notes", ["work_order_id"])


def downgrade() -> None:
    op.drop_index("idx_won_work_order", table_name="work_order_notes")
    op.drop_table("work_order_notes")
    op.drop_index("idx_wot_work_order", table_name="work_order_tasks")
    op.drop_table("work_order_tasks")
    op.drop_index("idx_wo_technician", table_name="work_orders")
    op.drop_index("idx_wo_number", table_name="work_orders")
    op.drop_index("idx_wo_contract", table_name="work_orders")
    op.drop_index("idx_wo_customer", table_name="work_orders")
    op.drop_index("idx_wo_tenant", table_name="work_orders")
    op.drop_table("work_orders")
