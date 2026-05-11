"""Map ORM models to API schemas."""

from .responses import TenantPrimaryContact, TenantResponse
from ..infra.db.models import Tenant


def tenant_to_response(tenant: Tenant) -> TenantResponse:
    return TenantResponse(
        id=tenant.id,
        tenant_name=tenant.tenant_name,
        slug=tenant.slug,
        db_name=tenant.db_name,
        status=tenant.status,
        tier=tenant.tier,
        products=list(tenant.products) if tenant.products is not None else [],
        region=tenant.region,
        company_profile=dict(tenant.company_profile or {}),
        billing_profile=dict(tenant.billing_profile or {}),
        primary_contact=TenantPrimaryContact(
            first_name=tenant.primary_contact_first_name,
            last_name=tenant.primary_contact_last_name,
            email=tenant.primary_contact_email,
            phone=tenant.primary_contact_phone,
        ),
        created_at=tenant.created_at,
        updated_at=tenant.updated_at,
    )
