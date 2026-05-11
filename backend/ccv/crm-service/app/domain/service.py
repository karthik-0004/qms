import uuid
from datetime import datetime, timezone
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.db.repository import CustomerRepository, ContactRepository, InteractionRepository
from app.infra.db.models import Customer, Contact, Interaction

logger = structlog.get_logger()

VALID_CUSTOMER_TRANSITIONS: dict[str, list[str]] = {
    "prospect":   ["qualified", "cancelled"],
    "qualified":  ["customer", "prospect", "cancelled"],
    "customer":   ["inactive", "cancelled"],
    "inactive":   ["customer", "cancelled"],
    "cancelled":  [],
}

VALID_INTERACTION_TYPES = {
    "call", "email", "meeting", "demo", "proposal", "site_visit", "support", "other"
}


class CRMDomainService:
    def __init__(self, session: AsyncSession):
        self._session = session
        self._customers = CustomerRepository(session)
        self._contacts = ContactRepository(session)
        self._interactions = InteractionRepository(session)

    # ─── Customers ──────────────────────────────────────────────────────────

    async def create_customer(
        self,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        company_name: str,
        **kwargs,
    ) -> Customer:
        existing = await self._customers.get_by_company_name(company_name, tenant_id)
        if existing:
            raise ValueError(f"Customer with company name '{company_name}' already exists")

        # API payload includes contact/address convenience fields that are not
        # first-class columns on Customer. Normalize them into billing_address.
        billing_address_fields = {
            "email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
        }
        billing_address: dict | None = None
        for k in list(kwargs.keys()):
            if k in billing_address_fields and kwargs.get(k) is not None:
                billing_address = billing_address or {}
                billing_address[k] = kwargs.pop(k)

        # Only pass valid Customer model fields through to SQLAlchemy.
        allowed_customer_fields = set(Customer.__mapper__.attrs.keys())
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_customer_fields}

        customer = await self._customers.create(
            {
                "tenant_id": tenant_id,
                "created_by": created_by,
                "company_name": company_name,
                "status": "prospect",
                "billing_address": billing_address,
                **filtered_kwargs,
            }
        )
        logger.info("customer.created", tenant_id=str(tenant_id), customer_id=str(customer.id))
        return customer

    async def get_customer(self, customer_id: uuid.UUID, tenant_id: uuid.UUID) -> Customer:
        customer = await self._customers.get_by_id(customer_id, tenant_id)
        if not customer:
            raise LookupError(f"Customer {customer_id} not found")
        return customer

    async def list_customers(
        self,
        tenant_id: uuid.UUID,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[Customer]:
        return await self._customers.list(tenant_id, status=status, skip=skip, limit=limit)

    async def transition_status(
        self,
        customer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        new_status: str,
        changed_by: uuid.UUID,
    ) -> Customer:
        customer = await self.get_customer(customer_id, tenant_id)
        allowed = VALID_CUSTOMER_TRANSITIONS.get(customer.status, [])
        if new_status not in allowed:
            raise ValueError(
                f"Cannot transition customer from '{customer.status}' to '{new_status}'"
            )
        customer = await self._customers.update(
            customer, {"status": new_status, "changed_by": changed_by}
        )
        logger.info(
            "customer.status_changed",
            customer_id=str(customer_id),
            from_status=customer.status,
            to_status=new_status,
        )
        return customer

    async def update_customer(
        self,
        customer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        changed_by: uuid.UUID,
        **kwargs,
    ) -> Customer:
        customer = await self.get_customer(customer_id, tenant_id)
        billing_address_fields = {
            "email",
            "phone",
            "address",
            "city",
            "state",
            "country",
            "postal_code",
        }
        billing_address_updates: dict | None = None
        for k in list(kwargs.keys()):
            if k in billing_address_fields and kwargs.get(k) is not None:
                billing_address_updates = billing_address_updates or {}
                billing_address_updates[k] = kwargs.pop(k)

        allowed_customer_fields = set(Customer.__mapper__.attrs.keys())
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_customer_fields}
        filtered_kwargs["changed_by"] = changed_by

        if billing_address_updates:
            existing = customer.billing_address or {}
            filtered_kwargs["billing_address"] = {**existing, **billing_address_updates}

        return await self._customers.update(customer, filtered_kwargs)

    # ─── Contacts ────────────────────────────────────────────────────────────

    async def add_contact(
        self,
        customer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        first_name: str,
        last_name: str,
        is_primary: bool = False,
        **kwargs,
    ) -> Contact:
        await self.get_customer(customer_id, tenant_id)

        if is_primary:
            await self._contacts.clear_primary_for_customer(customer_id)

        contact = await self._contacts.create({
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "created_by": created_by,
            "first_name": first_name,
            "last_name": last_name,
            "is_primary": is_primary,
            **kwargs,
        })
        logger.info("contact.added", customer_id=str(customer_id), contact_id=str(contact.id))
        return contact

    async def list_contacts(
        self, customer_id: uuid.UUID, tenant_id: uuid.UUID
    ) -> list[Contact]:
        await self.get_customer(customer_id, tenant_id)
        return await self._contacts.list_for_customer(customer_id, tenant_id)

    # ─── Interactions ─────────────────────────────────────────────────────────

    async def log_interaction(
        self,
        customer_id: uuid.UUID,
        tenant_id: uuid.UUID,
        created_by: uuid.UUID,
        interaction_type: str,
        subject: str,
        **kwargs,
    ) -> Interaction:
        if interaction_type not in VALID_INTERACTION_TYPES:
            raise ValueError(f"Invalid interaction_type: {interaction_type}")
        await self.get_customer(customer_id, tenant_id)

        interaction = await self._interactions.create({
            "tenant_id": tenant_id,
            "customer_id": customer_id,
            "created_by": created_by,
            "interaction_type": interaction_type,
            "subject": subject,
            **kwargs,
        })
        logger.info(
            "interaction.logged",
            customer_id=str(customer_id),
            type=interaction_type,
        )
        return interaction

    async def list_interactions(
        self, customer_id: uuid.UUID, tenant_id: uuid.UUID, limit: int = 50
    ) -> list[Interaction]:
        await self.get_customer(customer_id, tenant_id)
        return await self._interactions.list_for_customer(customer_id, tenant_id, limit=limit)
