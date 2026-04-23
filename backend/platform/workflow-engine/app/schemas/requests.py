"""Workflow Engine — Pydantic request schemas."""

from datetime import datetime

from pydantic import BaseModel, Field


class CreateWorkflowDefinitionRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    entity_type: str = Field(min_length=1, max_length=100)
    states: dict
    transitions: dict


class StartWorkflowRequest(BaseModel):
    entity_type: str = Field(min_length=1, max_length=100)
    entity_id: str
    assignee_id: str | None = None
    due_at: datetime | None = None
    context: dict | None = None


class TransitionRequest(BaseModel):
    action: str = Field(min_length=1, max_length=100)
    comment: str | None = None
    signature: str | None = None
    new_assignee_id: str | None = None
    metadata: dict | None = None
