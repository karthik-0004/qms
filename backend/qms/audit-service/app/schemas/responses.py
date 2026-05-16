"""Audit Management Service — Response schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AuditFindingResponse(BaseModel):
    id: str
    audit_id: str
    finding_number: str
    classification: str
    description: str
    iso_clause: Optional[str] = None
    evidence_file_ids: list[str] = []
    capa_id: Optional[str] = None
    auditee_response: Optional[str] = None
    response_due_date: Optional[datetime] = None
    created_by: str
    created_at: datetime
    updated_at: datetime


class ChecklistItemResponse(BaseModel):
    id: str
    checklist_id: str
    iso_clause: Optional[str] = None
    question: str
    expected_evidence: Optional[str] = None
    sort_order: int


class AuditChecklistResponse(BaseModel):
    id: str
    tenant_id: str
    name: str
    criteria: Optional[str] = None
    description: Optional[str] = None
    is_active: bool
    items: list[ChecklistItemResponse] = []
    created_by: str
    created_at: datetime
    updated_at: datetime


class ChecklistResponseRecord(BaseModel):
    id: str
    audit_id: str
    checklist_item_id: str
    response: str
    notes: Optional[str] = None
    evidence_file_id: Optional[str] = None
    responded_by: Optional[str] = None
    responded_at: Optional[datetime] = None


class AuditResponse(BaseModel):
    id: str
    tenant_id: str
    audit_number: str
    title: str
    audit_type: str
    entity_type: Optional[str] = None
    entity_ref: Optional[str] = None
    scope: Optional[str] = None
    criteria: Optional[str] = None
    status: str
    lead_auditor_id: Optional[str] = None
    audit_team: list[str] = []
    auditee_id: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    performed_start: Optional[datetime] = None
    performed_end: Optional[datetime] = None
    checklist_id: Optional[str] = None
    summary: Optional[str] = None
    report_file_id: Optional[str] = None
    score: Optional[int] = None
    tags: list[str] = []
    findings: list[AuditFindingResponse] = []
    finding_count: int = 0
    major_nc_count: int = 0
    minor_nc_count: int = 0
    created_by: str
    created_at: datetime
    updated_at: datetime


class AuditSummaryResponse(BaseModel):
    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    open_findings: int
