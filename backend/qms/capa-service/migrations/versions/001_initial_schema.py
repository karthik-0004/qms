"""Initial schema — capas, capa_actions.

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
        "capas",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("capa_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("capa_type", sa.String(50), nullable=False, server_default="corrective"),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("severity", sa.String(50), nullable=False, server_default="major"),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("root_cause_method", sa.String(100), nullable=True),
        sa.Column("source_type", sa.String(100), nullable=True),
        sa.Column("source_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("target_close_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_close_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effectiveness_check_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("effectiveness_verified", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("workflow_instance_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("attachments", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_capas_tenant_status", "capas", ["tenant_id", "status"])
    op.create_index("idx_capas_tenant_number", "capas", ["tenant_id", "capa_number"], unique=True)
    op.create_index("idx_capas_owner", "capas", ["owner_id"])
    op.create_index("idx_capas_due_date", "capas", ["due_date"])

    op.create_table(
        "capa_actions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("capa_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("action_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("evidence", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["capa_id"], ["capas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("capa_actions")
    op.drop_index("idx_capas_due_date", table_name="capas")
    op.drop_index("idx_capas_owner", table_name="capas")
    op.drop_index("idx_capas_tenant_number", table_name="capas")
    op.drop_index("idx_capas_tenant_status", table_name="capas")
    op.drop_table("capas")
