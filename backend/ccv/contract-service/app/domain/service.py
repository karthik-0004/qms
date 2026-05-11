import uuid
from datetime import datetime, timezone
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.repository import (
    ContractRepository,
    ContractLineItemRepository,
    ContractHistoryRepository,
)
from app.infra.db.models import Contract, ContractLineItem, ContractHistory

logger = structlog.get_logger()

VALID_CONTRACT_TRANSITIONS: dict[str, list[str]] = {
    "draft":          ["under_review", "cancelled"],
    "under_review":   ["approved", "draft", "cancelled"],
    "approved":       ["active", "cancelled"],
    "active":         ["expired", "terminated"],
    "expired":        [],
    "terminated":     [],
    "cancelled":      [],
}

VALID_CONTRACT_TYPES = {
    "service_agreement", "maintenance_contract", "calibration_contract",
    "validation_contract", "supply_agreement", "nda", "other"
}


def _map_api_fields_to_contract_columns(extra: dict) -> dict:
    """Map CreateContractRequest keys to SQLAlchemy Contract column names."""
    row = dict(extra)
    if "total_value" in row:
        row["value"] = row.pop("total_value")
    notes = row.pop("notes", None)
    if notes is not None:
        metadata = row.get("metadata_")
        if not isinstance(metadata, dict):
            metadata = {}
        else:
            metadata = dict(metadata)
        metadata["notes"] = notes
        row["metadata_"] = metadata
    return row


class ContractDomainService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._contracts = ContractRepository(session)
        self._line_items = ContractLineItemRepository(session)
        self._history = ContractHistoryRepository(session)

    # ─── Contracts ──────────────────────────────────────────────────────────

    async def create_contract(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID,
        created_by: uuid.UUID,
        contract_number: str,
        title: str,
        contract_type: str,
        **kwargs,
    ) -> Contract:
        if contract_type not in VALID_CONTRACT_TYPES:
            raise ValueError(f"Invalid contract_type: {contract_type}")
        existing = await self._contracts.get_by_number(contract_number, tenant_id)
        if existing:
            raise ValueError(f"Contract number '{contract_number}' already exists")

        row = _map_api_fields_to_contract_columns(kwargs)
        contract = await self._contracts.create({
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "created_by": created_by,
            "contract_number": contract_number,
            "title": title,
            "contract_type": contract_type,
            "status": "draft",
            **row,
        })
        await self._history.create({
            "contract_id": contract.id,
            "from_status": None,
            "to_status": "draft",
            "changed_by": created_by,
            "comment": "Contract created",
        })
        logger.info("contract.created", contract_id=str(contract.id))
        return contract

    async def get_contract(self, contract_id: uuid.UUID, tenant_id: uuid.UUID) -> Contract:
        contract = await self._contracts.get_by_id(contract_id, tenant_id)
        if not contract:
            raise LookupError(f"Contract {contract_id} not found")
        return contract

    async def list_contracts(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Contract]:
        return await self._contracts.list(
            tenant_id, customer_id=customer_id, status=status, skip=skip, limit=limit
        )

    async def transition_status(
        self,
        contract_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_status: str,
        changed_by: uuid.UUID,
        comment: str | None = None,
    ) -> Contract:
        contract = await self.get_contract(contract_id, tenant_id)
        allowed = VALID_CONTRACT_TRANSITIONS.get(contract.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition contract from '{contract.status}' to '{new_status}'"
            )

        update_data: dict = {"status": new_status, "changed_by": changed_by}
        now = datetime.now(timezone.utc)

        if new_status == "approved":
            update_data["approved_at"] = now
            update_data["approved_by"] = changed_by
        elif new_status == "active":
            update_data["signed_at"] = now
            update_data["signed_by"] = changed_by
        elif new_status in ("terminated",):
            update_data["terminated_at"] = now
            if comment:
                update_data["termination_reason"] = comment

        old_status = contract.status
        contract = await self._contracts.update(contract, update_data)
        await self._history.create({
            "contract_id": contract_id,
            "from_status": old_status,
            "to_status": new_status,
            "changed_by": changed_by,
            "comment": comment,
        })
        logger.info(
            "contract.status_changed",
            contract_id=str(contract_id),
            from_status=old_status,
            to_status=new_status,
        )
        return contract

    async def get_history(self, contract_id: uuid.UUID, tenant_id: uuid.UUID) -> list[ContractHistory]:
        await self.get_contract(contract_id, tenant_id)
        return await self._history.list_for_contract(contract_id)

    # ─── Line Items ──────────────────────────────────────────────────────────

    async def add_line_item(
        self,
        contract_id: uuid.UUID,
        tenant_id: uuid.UUID,
        description: str,
        unit_price: float,
        quantity: float = 1.0,
        unit: str | None = None,
        sort_order: int = 0,
    ) -> ContractLineItem:
        contract = await self.get_contract(contract_id, tenant_id)
        if contract.status not in ("draft",):
            raise ValueError("Can only add line items to contracts in draft status")

        line_item = await self._line_items.create({
            "contract_id": contract_id,
            "description": description,
            "unit_price": unit_price,
            "quantity": quantity,
            "unit": unit,
            "total_price": round(unit_price * quantity, 2),
            "sort_order": sort_order,
        })
        return line_item

    async def list_line_items(
        self, contract_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[ContractLineItem]:
        await self.get_contract(contract_id, tenant_id)
        return await self._line_items.list_for_contract(contract_id)
