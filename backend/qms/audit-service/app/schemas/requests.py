"""Audit Management Service — Request schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CreateAuditRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    audit_number: str = Field(..., min_length=1, max_length=50)
    audit_type: str = Field(default="internal")
    entity_type: Optional[str] = None
    entity_ref: Optional[str] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    lead_auditor_id: Optional[str] = None
    audit_team: list[str] = Field(default_factory=list)
    auditee_id: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    checklist_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)


class UpdateAuditRequest(BaseModel):
    title: Optional[str] = None
    audit_type: Optional[str] = None
    entity_type: Optional[str] = None
    entity_ref: Optional[str] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    lead_auditor_id: Optional[str] = None
    audit_team: Optional[list[str]] = None
    auditee_id: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    performed_start: Optional[datetime] = None
    performed_end: Optional[datetime] = None
    summary: Optional[str] = None
    status: Optional[str] = None
    checklist_id: Optional[str] = None
    tags: Optional[list[str]] = None


class CreateFindingRequest(BaseModel):
    classification: str = Field(default="observation")
    description: str = Field(..., min_length=1)
    iso_clause: Optional[str] = None
    response_due_date: Optional[datetime] = None


class UpdateFindingRequest(BaseModel):
    classification: Optional[str] = None
    description: Optional[str] = None
    iso_clause: Optional[str] = None
    auditee_response: Optional[str] = None
    response_due_date: Optional[datetime] = None
    capa_id: Optional[str] = None


class CreateChecklistRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    criteria: Optional[str] = None
    description: Optional[str] = None
    items: list[dict] = Field(default_factory=list)


class ChecklistResponseRequest(BaseModel):
    checklist_item_id: str
    response: str = Field(default="pending")
    notes: Optional[str] = None
