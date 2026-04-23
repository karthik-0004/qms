"""Initial schema — quality_events.

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
        "quality_events",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("event_number", sa.String(50), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("event_type", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("severity", sa.String(50), nullable=False, server_default="minor"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("department", sa.String(100), nullable=True),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("detected_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("root_cause", sa.Text(), nullable=True),
        sa.Column("immediate_action", sa.Text(), nullable=True),
        sa.Column("capa_required", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("capa_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tags", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("attachments", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_qe_tenant_status", "quality_events", ["tenant_id", "status"])
    op.create_index("idx_qe_tenant_number", "quality_events", ["tenant_id", "event_number"], unique=True)
    op.create_index("idx_qe_assigned_to", "quality_events", ["assigned_to"])


def downgrade() -> None:
    op.drop_index("idx_qe_assigned_to", table_name="quality_events")
    op.drop_index("idx_qe_tenant_number", table_name="quality_events")
    op.drop_index("idx_qe_tenant_status", table_name="quality_events")
    op.drop_table("quality_events")
