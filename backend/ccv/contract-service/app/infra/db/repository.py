import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.infra.db.models import Contract, ContractLineItem, ContractHistory


class ContractRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Contract:
        contract = Contract(**data)
        self._session.add(contract)
        await self._session.flush()
        await self._session.refresh(contract)
        return contract

    async def get_by_id(self, contract_id: uuid.UUID, tenant_id: uuid.UUID) -> Contract | None:
        result = await self._session.execute(
            select(Contract).where(
                and_(
                    Contract.id == contract_id,
                    Contract.tenant_id == tenant_id,
                    Contract.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_number(self, contract_number: str, tenant_id: uuid.UUID) -> Contract | None:
        result = await self._session.execute(
            select(Contract).where(
                and_(
                    Contract.contract_number == contract_number,
                    Contract.tenant_id == tenant_id,
                    Contract.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        customer_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Contract]:
        stmt = select(Contract).where(
            and_(Contract.tenant_id == tenant_id, Contract.deleted_at.is_(None))
        )
        if customer_id:
            stmt = stmt.where(Contract.customer_id == customer_id)
        if status:
            stmt = stmt.where(Contract.status == status)
        stmt = stmt.offset(skip).limit(limit).order_by(Contract.created_at.desc())
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, contract: Contract, data: dict) -> Contract:
        for key, value in data.items():
            setattr(contract, key, value)
        await self._session.flush()
        await self._session.refresh(contract)
        return contract

    async def soft_delete(self, contract: Contract) -> None:
        contract.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()


class ContractLineItemRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> ContractLineItem:
        item = ContractLineItem(**data)
        self._session.add(item)
        await self._session.flush()
        await self._session.refresh(item)
        return item

    async def list_for_contract(self, contract_id: uuid.UUID) -> list[ContractLineItem]:
        result = await self._session.execute(
            select(ContractLineItem)
            .where(ContractLineItem.contract_id == contract_id)
            .order_by(ContractLineItem.sort_order)
        )
        return list(result.scalars().all())


class ContractHistoryRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> ContractHistory:
        entry = ContractHistory(**data)
        self._session.add(entry)
        await self._session.flush()
        await self._session.refresh(entry)
        return entry

    async def list_for_contract(self, contract_id: uuid.UUID) -> list[ContractHistory]:
        result = await self._session.execute(
            select(ContractHistory)
            .where(ContractHistory.contract_id == contract_id)
            .order_by(ContractHistory.changed_at.desc())
        )
        return list(result.scalars().all())
