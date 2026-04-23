"""Initial schema — workflow_definitions, workflow_instances, workflow_history.

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
        "workflow_definitions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("states", postgresql.JSONB(), nullable=False),
        sa.Column("transitions", postgresql.JSONB(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workflow_instances",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("definition_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("current_state", sa.String(100), nullable=False),
        sa.Column("context", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["definition_id"], ["workflow_definitions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_workflow_instances_entity", "workflow_instances", ["entity_type", "entity_id"])
    op.create_index("idx_workflow_instances_assignee", "workflow_instances", ["assignee_id", "current_state"])

    op.create_table(
        "workflow_history",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("instance_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("from_state", sa.String(100), nullable=True),
        sa.Column("to_state", sa.String(100), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("signature", sa.String(255), nullable=True),
        sa.Column("metadata", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["instance_id"], ["workflow_instances.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_workflow_history_instance", "workflow_history", ["instance_id", "occurred_at"])


def downgrade() -> None:
    op.drop_index("idx_workflow_history_instance", table_name="workflow_history")
    op.drop_table("workflow_history")
    op.drop_index("idx_workflow_instances_assignee", table_name="workflow_instances")
    op.drop_index("idx_workflow_instances_entity", table_name="workflow_instances")
    op.drop_table("workflow_instances")
    op.drop_table("workflow_definitions")
