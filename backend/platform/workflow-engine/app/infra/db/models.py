"""Workflow Engine — SQLAlchemy ORM models (Tenant DB via TenantResolver)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class WorkflowDefinition(Base):
    __tablename__ = "workflow_definitions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False, default=1)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    states: Mapped[dict] = mapped_column(JSONB, nullable=False)
    transitions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WorkflowInstance(Base):
    __tablename__ = "workflow_instances"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    definition_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workflow_definitions.id"),
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    current_state: Mapped[str] = mapped_column(String(100), nullable=False)
    context: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    assignee_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_workflow_instances_entity", "entity_type", "entity_id"),
        Index("idx_workflow_instances_assignee", "assignee_id", "current_state"),
    )


class WorkflowHistory(Base):
    __tablename__ = "workflow_history"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    instance_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("workflow_instances.id"),
        nullable=False,
    )
    from_state: Mapped[str | None] = mapped_column(String(100), nullable=True)
    to_state: Mapped[str] = mapped_column(String(100), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    actor_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    signature: Mapped[str | None] = mapped_column(String(255), nullable=True)
    metadata_: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    __table_args__ = (
        Index("idx_workflow_history_instance", "instance_id", "occurred_at"),
    )
