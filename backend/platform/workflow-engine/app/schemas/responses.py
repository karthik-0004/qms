"""Workflow Engine — Pydantic response schemas."""

from datetime import datetime

from pydantic import BaseModel


class WorkflowDefinitionResponse(BaseModel):
    id: str
    name: str
    version: int
    entity_type: str
    states: dict
    transitions: dict
    is_active: bool
    created_at: datetime


class WorkflowInstanceResponse(BaseModel):
    id: str
    definition_id: str
    entity_type: str
    entity_id: str
    current_state: str
    context: dict
    assignee_id: str | None
    due_at: datetime | None
    completed_at: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime


class WorkflowHistoryEntry(BaseModel):
    id: str
    instance_id: str
    from_state: str | None
    to_state: str
    action: str
    actor_id: str
    comment: str | None
    signature: str | None
    metadata: dict
    occurred_at: datetime


class AvailableTransition(BaseModel):
    action: str
    to_state: str
    label: str
    requires_comment: bool
    requires_signature: bool
