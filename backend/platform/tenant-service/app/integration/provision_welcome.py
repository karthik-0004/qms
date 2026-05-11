"""Post-provisioning: auth user, directory profile, RBAC assignment, welcome email."""

from __future__ import annotations

import json
from typing import Any

import httpx
import structlog

from rainer_common.exceptions import ConflictError, RainerException

from ..core.config import Settings
from ..infra.db.models import Tenant

logger = structlog.get_logger(__name__)


def _auth_header(authorization: str) -> dict[str, str]:
    auth = authorization.strip()
    if not auth.lower().startswith("bearer "):
        auth = f"Bearer {auth}"
    return {"Authorization": auth, "Content-Type": "application/json"}


def _format_address_summary(company_profile: dict[str, Any], billing_profile: dict[str, Any]) -> str:
    lines: list[str] = []
    addr = company_profile.get("address") or {}
    if any(addr.values()):
        lines.append("Primary address:")
        for label, key in (
            ("Line 1", "address_line1"),
            ("Line 2", "address_line2"),
            ("City", "city"),
            ("State", "state"),
            ("Country", "country"),
            ("Postal", "postal_code"),
        ):
            val = addr.get(key)
            if val:
                lines.append(f"  {label}: {val}")
    bill = billing_profile or {}
    if bill.get("billing_email") or bill.get("billing_phone") or bill.get("tax_id"):
        lines.append("Billing:")
        if bill.get("billing_email"):
            lines.append(f"  Email: {bill['billing_email']}")
        if bill.get("billing_phone"):
            lines.append(f"  Phone: {bill['billing_phone']}")
        if bill.get("tax_id"):
            lines.append(f"  Tax ID: {bill['tax_id']}")
        bad = bill.get("billing_address") or {}
        if any(bad.values()):
            lines.append("  Billing address:")
            for label, key in (
                ("Line 1", "address_line1"),
                ("Line 2", "address_line2"),
                ("City", "city"),
                ("State", "state"),
                ("Country", "country"),
                ("Postal", "postal_code"),
            ):
                val = bad.get(key)
                if val:
                    lines.append(f"    {label}: {val}")
    return "\n".join(lines) if lines else "Address / billing: (not provided)"


def welcome_email_variables(
    *,
    settings: Settings,
    tenant: Tenant,
    admin_email: str,
    temporary_password: str,
) -> dict[str, Any]:
    """Variables for the tenant_admin_welcome template (same shape as initial provision)."""
    first = tenant.primary_contact_first_name or ""
    last = tenant.primary_contact_last_name or ""
    return {
        "tenant_name": tenant.tenant_name,
        "slug": tenant.slug,
        "login_url": settings.public_web_login_url,
        "admin_email": admin_email,
        "temporary_password": temporary_password,
        "admin_first_name": first,
        "admin_last_name": last,
        "tier": tenant.tier,
        "region": tenant.region,
        "products": ", ".join(list(tenant.products or [])),
        "address_summary": _format_address_summary(
            tenant.company_profile or {}, tenant.billing_profile or {}
        ),
    }


async def provision_tenant_admin_and_notify(
    *,
    settings: Settings,
    authorization: str,
    tenant: Tenant,
) -> None:
    headers = _auth_header(authorization)
    base_auth = settings.auth_service_url.rstrip("/")
    base_users = settings.user_service_url.rstrip("/")
    base_notify = settings.notification_service_url.rstrip("/")

    pc_email = (tenant.primary_contact_email or "").strip()
    if not pc_email:
        raise RainerException(
            code="PRIMARY_CONTACT_EMAIL_MISSING",
            message="Primary contact email is required to provision the tenant admin",
            status_code=400,
            details=[{"message": f"tenant_id={tenant.id}"}],
        )

    first_name = tenant.primary_contact_first_name or ""
    last_name = tenant.primary_contact_last_name or ""

    async with httpx.AsyncClient(timeout=60.0) as client:
        br = await client.post(
            f"{base_auth}/api/v1/auth/bootstrap/tenant-admin",
            headers=headers,
            json={
                "tenant_id": tenant.id,
                "email": pc_email,
                "first_name": first_name,
                "last_name": last_name,
                "role": "tenant_admin",
            },
        )
        if br.status_code == 409:
            raise ConflictError("Email already registered")
        if br.status_code >= 400:
            msg = _extract_error_message(br)
            logger.error("bootstrap_auth_failed", tenant_id=tenant.id, status=br.status_code, msg=msg)
            raise RainerException(
                code="TENANT_PROVISIONED_ADMIN_FAILED",
                message="Tenant was provisioned but creating the admin login failed",
                status_code=500,
                details=[{"message": msg, "code": "auth_bootstrap"}],
            )
        boot = br.json()
        platform_user_id = boot["data"]["platform_user_id"]
        temporary_password = boot["data"]["temporary_password"]

        ur = await client.post(
            f"{base_users}/api/v1/users",
            headers=headers,
            json={
                "platform_user_id": platform_user_id,
                "tenant_id": tenant.id,
                "first_name": first_name,
                "last_name": last_name,
                "phone": tenant.primary_contact_phone,
            },
        )
        if ur.status_code >= 400:
            msg = _extract_error_message(ur)
            logger.error("directory_user_failed", tenant_id=tenant.id, status=ur.status_code, msg=msg)
            raise RainerException(
                code="TENANT_PROVISIONED_ADMIN_FAILED",
                message="Tenant was provisioned but directory user creation failed",
                status_code=500,
                details=[{"message": msg, "code": "user_service"}],
            )
        user_body = ur.json()
        directory_user_id = user_body["data"]["id"]

        rr = await client.get(f"{base_users}/api/v1/roles", headers=headers)
        if rr.status_code == 200:
            roles = rr.json().get("data") or []
            admin = next((r for r in roles if r.get("name") == "Admin"), None)
            if admin:
                ar = await client.post(
                    f"{base_users}/api/v1/users/{directory_user_id}/roles",
                    headers=headers,
                    json={"role_id": admin["id"]},
                )
                if ar.status_code >= 400:
                    logger.warning(
                        "assign_admin_role_failed",
                        tenant_id=tenant.id,
                        status=ar.status_code,
                        body=ar.text,
                    )
        else:
            logger.warning("list_roles_failed", tenant_id=tenant.id, status=rr.status_code)

        variables = welcome_email_variables(
            settings=settings,
            tenant=tenant,
            admin_email=pc_email,
            temporary_password=temporary_password,
        )

        nr = await client.post(
            f"{base_notify}/api/v1/notifications/send-from-template",
            headers=headers,
            json={
                "template_name": "tenant_admin_welcome",
                "recipient_email": pc_email,
                "variables": variables,
                "tenant_id": tenant.id,
                "user_id": platform_user_id,
            },
        )
        if nr.status_code >= 400:
            logger.error(
                "welcome_email_failed",
                tenant_id=tenant.id,
                status=nr.status_code,
                body=nr.text,
            )


async def resend_tenant_admin_welcome_email(
    *,
    settings: Settings,
    authorization: str,
    tenant: Tenant,
) -> None:
    """Reset tenant admin password and send tenant_admin_welcome again to the login email."""
    headers = _auth_header(authorization)
    base_auth = settings.auth_service_url.rstrip("/")
    base_notify = settings.notification_service_url.rstrip("/")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            ar = await client.post(
                f"{base_auth}/api/v1/auth/tenants/{tenant.id}/tenant-admin/resend-welcome-credentials",
                headers=headers,
            )
            if ar.status_code >= 400:
                msg = _extract_error_message(ar)
                logger.error(
                    "resend_welcome_auth_failed",
                    tenant_id=tenant.id,
                    status=ar.status_code,
                    msg=msg,
                )
                code = "TENANT_ADMIN_RESEND_FAILED"
                message = "Could not reset tenant admin credentials"
                if ar.status_code == 404:
                    code = "TENANT_ADMIN_NOT_FOUND"
                    message = "No tenant admin login exists for this tenant"
                raise RainerException(
                    code=code,
                    message=message,
                    status_code=502 if ar.status_code != 404 else 404,
                    details=[{"message": msg}],
                )

            try:
                body = ar.json()
                data = body.get("data") if isinstance(body, dict) else None
                if not isinstance(data, dict):
                    raise KeyError("missing data envelope")
                platform_user_id = str(data["platform_user_id"])
                temporary_password = str(data["temporary_password"])
                admin_email = str(data["admin_email"])
            except (KeyError, TypeError, ValueError) as exc:
                logger.error("resend_welcome_auth_bad_json", tenant_id=tenant.id, error=str(exc))
                raise RainerException(
                    code="AUTH_RESPONSE_INVALID",
                    message="Auth service returned an unexpected response when resetting credentials",
                    status_code=502,
                    details=[{"message": str(exc)}],
                ) from exc

            variables = welcome_email_variables(
                settings=settings,
                tenant=tenant,
                admin_email=admin_email,
                temporary_password=temporary_password,
            )

            nr = await client.post(
                f"{base_notify}/api/v1/notifications/send-from-template",
                headers=headers,
                json={
                    "template_name": "tenant_admin_welcome",
                    "recipient_email": admin_email,
                    "variables": variables,
                    "tenant_id": str(tenant.id),
                    "user_id": platform_user_id,
                },
            )
            if nr.status_code >= 400:
                nmsg = _extract_error_message(nr)
                logger.error(
                    "resend_welcome_email_failed",
                    tenant_id=tenant.id,
                    status=nr.status_code,
                    body=nr.text,
                )
                raise RainerException(
                    code="WELCOME_EMAIL_SEND_FAILED",
                    message="Credentials were reset but the welcome email could not be sent",
                    status_code=502,
                    details=[{"message": nmsg}],
                )
    except RainerException:
        raise
    except httpx.RequestError as exc:
        logger.error("resend_welcome_upstream_unavailable", error=str(exc))
        raise RainerException(
            code="UPSTREAM_UNREACHABLE",
            message=(
                "Could not reach auth-service or notification-service. "
                "Check AUTH_SERVICE_URL, NOTIFICATION_SERVICE_URL, and that containers are running."
            ),
            status_code=502,
            details=[{"message": str(exc)}],
        ) from exc


def _extract_error_message(resp: httpx.Response) -> str:
    try:
        body = resp.json()
        err = body.get("error") or body.get("detail")
        if isinstance(err, dict):
            main = str(err.get("message") or err)
            details = err.get("details")
            if isinstance(details, list) and details:
                first = details[0]
                if isinstance(first, dict) and first.get("message"):
                    dmsg = str(first["message"])
                    if dmsg and dmsg not in main:
                        return f"{main} — {dmsg}"
            return main
        if isinstance(err, list):
            return json.dumps(err)
        return str(err or body)
    except Exception:
        return resp.text or resp.reason_phrase
