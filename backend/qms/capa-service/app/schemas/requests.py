"""CAPA Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class CreateCAPARequest(BaseModel):
    capa_number: str = Field(min_length=1, max_length=50)
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    capa_type: str = "corrective"
    severity: str = "major"
    source_type: str | None = None
    source_id: str | None = None
    owner_id: str | None = None
    department: str | None = None
    due_date: datetime | None = None
    tags: list[str] = []


class UpdateCAPARequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    severity: str | None = None
    owner_id: str | None = None
    department: str | None = None
    root_cause: str | None = None
    root_cause_method: str | None = None
    due_date: datetime | None = None
    target_close_date: datetime | None = None
    tags: list[str] | None = None


class AddCAPAActionRequest(BaseModel):
    action_type: str = Field(min_length=1, max_length=50)
    description: str = Field(min_length=1)
    assigned_to: str | None = None
    due_date: datetime | None = None


class CompleteActionRequest(BaseModel):
    evidence: str | None = None


class VerifyEffectivenessRequest(BaseModel):
    verified: bool
    notes: str | None = None
