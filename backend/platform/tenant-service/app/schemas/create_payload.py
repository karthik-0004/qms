"""Derive persisted profile payloads from CreateTenantRequest."""

from .requests import CreateTenantRequest


def company_and_billing_profiles(payload: CreateTenantRequest) -> tuple[dict, dict]:
    company = payload.company.model_dump(exclude_none=True) if payload.company else {}
    address = payload.address.model_dump(exclude_none=True) if payload.address else {}
    company_profile = {"company": company, "address": address}

    billing_profile: dict = {}
    if payload.billing:
        bill = payload.billing
        if bill.billing_address_same_as_address:
            billing_addr_part = dict(address)
        elif bill.billing_address:
            billing_addr_part = bill.billing_address.model_dump(exclude_none=True)
        else:
            billing_addr_part = {}

        billing_profile = {
            "billing_email": bill.billing_email,
            "billing_phone": bill.billing_phone,
            "tax_id": bill.tax_id,
            "billing_address_same_as_address": bill.billing_address_same_as_address,
            "billing_address": billing_addr_part,
        }
        billing_profile = {k: v for k, v in billing_profile.items() if v is not None}

    return company_profile, billing_profile
