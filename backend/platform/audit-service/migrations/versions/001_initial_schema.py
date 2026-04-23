"""Initial schema — platform_audit_logs.

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
        "platform_audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(100), nullable=True),
        sa.Column("resource_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("ip_address", postgresql.INET(), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="info"),
        sa.Column("source_service", sa.String(100), nullable=True),
        sa.Column("event_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_audit_logs_tenant_time", "platform_audit_logs", ["tenant_id", "created_at"])
    op.create_index("idx_audit_logs_user_time", "platform_audit_logs", ["user_id", "created_at"])
    op.create_index("idx_audit_logs_action", "platform_audit_logs", ["action"])


def downgrade() -> None:
    op.drop_index("idx_audit_logs_action", table_name="platform_audit_logs")
    op.drop_index("idx_audit_logs_user_time", table_name="platform_audit_logs")
    op.drop_index("idx_audit_logs_tenant_time", table_name="platform_audit_logs")
    op.drop_table("platform_audit_logs")
