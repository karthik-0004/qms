"""Contract Service — Pydantic response schemas."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ContractResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    customer_id: UUID
    contract_number: str
    title: str
    contract_type: str
    description: str | None
    status: str
    start_date: datetime | None
    end_date: datetime | None
    total_value: float | None
    currency: str
    payment_terms: str | None
    notes: str | None
    approved_at: datetime | None
    approved_by: UUID | None
    signed_at: datetime | None
    signed_by: UUID | None
    terminated_at: datetime | None
    termination_reason: str | None
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, contract: "Contract") -> "ContractResponse":
        """Build response from ORM model (maps `value` → total_value, metadata notes)."""
        meta = contract.metadata_ if isinstance(contract.metadata_, dict) else {}
        notes = meta.get("notes") if meta else None
        total = contract.value
        return cls(
            id=contract.id,
            tenant_id=contract.tenant_id,
            customer_id=contract.customer_id,
            contract_number=contract.contract_number,
            title=contract.title,
            contract_type=contract.contract_type,
            description=contract.description,
            status=contract.status,
            start_date=contract.start_date,
            end_date=contract.end_date,
            total_value=float(total) if total is not None else None,
            currency=contract.currency,
            payment_terms=contract.payment_terms,
            notes=notes,
            approved_at=contract.approved_at,
            approved_by=contract.approved_by,
            signed_at=contract.signed_at,
            signed_by=contract.signed_by,
            terminated_at=contract.terminated_at,
            termination_reason=contract.termination_reason,
            created_by=contract.created_by,
            created_at=contract.created_at,
            updated_at=contract.updated_at,
        )


class ContractLineItemResponse(BaseModel):
    id: UUID
    contract_id: UUID
    description: str
    unit_price: float
    quantity: float
    unit: str | None
    total_price: float
    sort_order: int
    created_at: datetime


class ContractHistoryResponse(BaseModel):
    id: UUID
    contract_id: UUID
    from_status: str | None
    to_status: str
    changed_by: UUID
    comment: str | None
    created_at: datetime
