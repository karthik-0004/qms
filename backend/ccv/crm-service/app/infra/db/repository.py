import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.infra.db.models import Customer, Contact, Interaction


class CustomerRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Customer:
        customer = Customer(**data)
        self._session.add(customer)
        await self._session.flush()
        await self._session.refresh(customer)
        return customer

    async def get_by_id(self, customer_id: uuid.UUID, tenant_id: uuid.UUID) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(
                and_(
                    Customer.id == customer_id,
                    Customer.tenant_id == tenant_id,
                    Customer.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_by_company_name(self, company_name: str, tenant_id: uuid.UUID) -> Customer | None:
        result = await self._session.execute(
            select(Customer).where(
                and_(
                    Customer.company_name == company_name,
                    Customer.tenant_id == tenant_id,
                    Customer.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        tenant_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Customer]:
        stmt = select(Customer).where(
            and_(Customer.tenant_id == tenant_id, Customer.deleted_at.is_(None))
        )
        if status:
            stmt = stmt.where(Customer.status == status)
        stmt = stmt.offset(skip).limit(limit).order_by(Customer.company_name)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, customer: Customer, data: dict) -> Customer:
        for key, value in data.items():
            setattr(customer, key, value)
        await self._session.flush()
        await self._session.refresh(customer)
        return customer

    async def soft_delete(self, customer: Customer) -> None:
        customer.deleted_at = datetime.now(timezone.utc)
        await self._session.flush()


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Contact:
        contact = Contact(**data)
        self._session.add(contact)
        await self._session.flush()
        await self._session.refresh(contact)
        return contact

    async def get_by_id(self, contact_id: uuid.UUID, tenant_id: uuid.UUID) -> Contact | None:
        result = await self._session.execute(
            select(Contact).where(
                and_(
                    Contact.id == contact_id,
                    Contact.tenant_id == tenant_id,
                    Contact.deleted_at.is_(None),
                )
            )
        )
        return result.scalar_one_or_none()

    async def list_for_customer(self, customer_id: uuid.UUID, tenant_id: uuid.UUID) -> list[Contact]:
        result = await self._session.execute(
            select(Contact).where(
                and_(
                    Contact.customer_id == customer_id,
                    Contact.tenant_id == tenant_id,
                    Contact.deleted_at.is_(None),
                )
            ).order_by(Contact.last_name)
        )
        return list(result.scalars().all())

    async def clear_primary_for_customer(self, customer_id: uuid.UUID) -> None:
        await self._session.execute(
            update(Contact)
            .where(Contact.customer_id == customer_id, Contact.deleted_at.is_(None))
            .values(is_primary=False)
        )


class InteractionRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, data: dict) -> Interaction:
        interaction = Interaction(**data)
        self._session.add(interaction)
        await self._session.flush()
        await self._session.refresh(interaction)
        return interaction

    async def list_for_customer(
        self, customer_id: uuid.UUID, tenant_id: uuid.UUID, limit: int = 50
    ) -> list[Interaction]:
        result = await self._session.execute(
            select(Interaction)
            .where(
                and_(
                    Interaction.customer_id == customer_id,
                    Interaction.tenant_id == tenant_id,
                    Interaction.deleted_at.is_(None),
                )
            )
            .order_by(Interaction.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
