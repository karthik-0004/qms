"""
Phase D — RainerCCV E2E Vertical Slice Tests.

Tests cover the complete CCV business workflow:
  prospect → customer → contract → work order → technician assignment → invoice → paid

Set env var CCV_E2E_ENABLED=true to run.
Ports: crm=8040, contract=8041, workorder=8042, technician=8043, billing=8044
"""

import os
import uuid
import pytest
import httpx

CCV_E2E_ENABLED = os.getenv("CCV_E2E_ENABLED", "false").lower() == "true"

CRM_URL = os.getenv("CRM_SERVICE_URL", "http://localhost:8040")
CONTRACT_URL = os.getenv("CONTRACT_SERVICE_URL", "http://localhost:8041")
WORKORDER_URL = os.getenv("WORKORDER_SERVICE_URL", "http://localhost:8042")
TECHNICIAN_URL = os.getenv("TECHNICIAN_SERVICE_URL", "http://localhost:8043")
BILLING_URL = os.getenv("BILLING_SERVICE_URL", "http://localhost:8044")

TENANT_ID = str(uuid.uuid4())
USER_ID = str(uuid.uuid4())
HEADERS = {"X-Tenant-ID": TENANT_ID, "X-User-ID": USER_ID}

pytestmark = pytest.mark.skipif(
    not CCV_E2E_ENABLED,
    reason="CCV E2E tests disabled. Set CCV_E2E_ENABLED=true to run.",
)


# ─── TC-CCV-001: Health checks ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_crm_health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{CRM_URL}/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"
    assert r.json()["service"] == "crm-service"


@pytest.mark.asyncio
async def test_contract_health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{CONTRACT_URL}/health")
    assert r.status_code == 200
    assert r.json()["service"] == "contract-service"


@pytest.mark.asyncio
async def test_workorder_health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{WORKORDER_URL}/health")
    assert r.status_code == 200
    assert r.json()["service"] == "workorder-service"


@pytest.mark.asyncio
async def test_technician_health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{TECHNICIAN_URL}/health")
    assert r.status_code == 200
    assert r.json()["service"] == "technician-service"


@pytest.mark.asyncio
async def test_billing_health():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{BILLING_URL}/health")
    assert r.status_code == 200
    assert r.json()["service"] == "billing-service"
    assert "currency" in r.json()


# ─── Shared state ─────────────────────────────────────────────────────────────

_state: dict = {}


# ─── TC-CCV-006: Create customer ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_customer():
    payload = {
        "company_name": f"E2E BioPharm Labs {TENANT_ID[:8]}",
        "industry": "pharmaceutical",
        "notes": "E2E test customer",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{CRM_URL}/api/v1/customers", json=payload, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["status"] == "prospect"
    assert data["company_name"] == payload["company_name"]
    _state["customer_id"] = data["id"]


@pytest.mark.asyncio
async def test_add_primary_contact():
    payload = {
        "first_name": "Jane",
        "last_name": "Doe",
        "email": f"jane.doe.{TENANT_ID[:8]}@biopharm.com",
        "is_primary": True,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CRM_URL}/api/v1/customers/{_state['customer_id']}/contacts",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["is_primary"] is True
    _state["contact_id"] = data["id"]


@pytest.mark.asyncio
async def test_log_interaction():
    payload = {
        "interaction_type": "call",
        "subject": "Initial discovery call",
        "outcome": "interested",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CRM_URL}/api/v1/customers/{_state['customer_id']}/interactions",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_qualify_customer():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CRM_URL}/api/v1/customers/{_state['customer_id']}/transition",
            json={"status": "qualified"},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "qualified"


@pytest.mark.asyncio
async def test_convert_to_customer():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CRM_URL}/api/v1/customers/{_state['customer_id']}/transition",
            json={"status": "customer"},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "customer"


# ─── TC-CCV-011: Create contract ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_contract():
    payload = {
        "customer_id": _state["customer_id"],
        "contract_number": f"CCV-E2E-{TENANT_ID[:8]}",
        "title": "Annual Calibration Services Agreement",
        "contract_type": "calibration_contract",
        "payment_terms": "Net 30",
        "billing_frequency": "annual",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{CONTRACT_URL}/api/v1/contracts", json=payload, headers=HEADERS)
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["status"] == "draft"
    _state["contract_id"] = data["id"]


@pytest.mark.asyncio
async def test_add_contract_line_item():
    payload = {
        "description": "Annual calibration service — 10 instruments",
        "unit_price": 5000.0,
        "quantity": 1.0,
        "unit": "year",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CONTRACT_URL}/api/v1/contracts/{_state['contract_id']}/line-items",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201
    assert r.json()["data"]["total_price"] == 5000.0


@pytest.mark.asyncio
async def test_submit_contract_for_review():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CONTRACT_URL}/api/v1/contracts/{_state['contract_id']}/transition",
            json={"status": "under_review"},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "under_review"


@pytest.mark.asyncio
async def test_approve_contract():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CONTRACT_URL}/api/v1/contracts/{_state['contract_id']}/transition",
            json={"status": "approved"},
            headers=HEADERS,
        )
    assert r.status_code == 200


@pytest.mark.asyncio
async def test_activate_contract():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{CONTRACT_URL}/api/v1/contracts/{_state['contract_id']}/transition",
            json={"status": "active"},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "active"


# ─── TC-CCV-016: Register technician ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_technician():
    payload = {
        "employee_number": f"EMP-E2E-{TENANT_ID[:8]}",
        "first_name": "Alice",
        "last_name": "Smith",
        "email": f"alice.smith.{TENANT_ID[:8]}@rainer.com",
        "specializations": ["calibration", "validation"],
        "hourly_rate": 95.0,
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TECHNICIAN_URL}/api/v1/technicians", json=payload, headers=HEADERS
        )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["status"] == "available"
    _state["technician_id"] = data["id"]


@pytest.mark.asyncio
async def test_add_technician_certification():
    payload = {
        "certification_name": "Certified Quality Engineer (CQE)",
        "issuing_body": "ASQ",
        "certificate_number": f"CQE-{TENANT_ID[:8]}",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{TECHNICIAN_URL}/api/v1/technicians/{_state['technician_id']}/certifications",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201
    assert r.json()["data"]["is_active"] is True


# ─── TC-CCV-018: Create work order ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_work_order():
    payload = {
        "customer_id": _state["customer_id"],
        "contract_id": _state["contract_id"],
        "work_order_number": f"WO-E2E-{TENANT_ID[:8]}",
        "title": "Initial calibration run — 10 instruments",
        "work_order_type": "calibration",
        "priority": "normal",
        "site_contact": "Jane Doe",
        "site_phone": "+1-555-0100",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{WORKORDER_URL}/api/v1/work-orders", json=payload, headers=HEADERS
        )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["status"] == "pending"
    _state["work_order_id"] = data["id"]


@pytest.mark.asyncio
async def test_add_work_order_task():
    payload = {"title": "Calibrate analytical balance", "sort_order": 1}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{WORKORDER_URL}/api/v1/work-orders/{_state['work_order_id']}/tasks",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201
    _state["task_id"] = r.json()["data"]["id"]


@pytest.mark.asyncio
async def test_assign_technician_to_work_order():
    payload = {"technician_id": _state["technician_id"]}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{WORKORDER_URL}/api/v1/work-orders/{_state['work_order_id']}/assign",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "assigned"


@pytest.mark.asyncio
async def test_start_work_order():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{WORKORDER_URL}/api/v1/work-orders/{_state['work_order_id']}/transition",
            json={"status": "in_progress"},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "in_progress"


@pytest.mark.asyncio
async def test_complete_task():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{WORKORDER_URL}/api/v1/work-orders/{_state['work_order_id']}/tasks/{_state['task_id']}/complete",
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["is_completed"] is True


@pytest.mark.asyncio
async def test_complete_work_order():
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{WORKORDER_URL}/api/v1/work-orders/{_state['work_order_id']}/transition",
            json={"status": "completed", "completion_notes": "All 10 instruments calibrated."},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "completed"


# ─── TC-CCV-024: Invoice & payment ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_invoice():
    payload = {
        "customer_id": _state["customer_id"],
        "contract_id": _state["contract_id"],
        "work_order_id": _state["work_order_id"],
        "invoice_number": f"INV-E2E-{TENANT_ID[:8]}",
        "payment_terms": "Net 30",
        "currency": "USD",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BILLING_URL}/api/v1/invoices", json=payload, headers=HEADERS
        )
    assert r.status_code == 201
    data = r.json()["data"]
    assert data["status"] == "draft"
    _state["invoice_id"] = data["id"]


@pytest.mark.asyncio
async def test_add_invoice_line_item():
    payload = {
        "description": "Calibration services — 10 instruments",
        "unit_price": 5000.0,
        "quantity": 1.0,
        "unit": "service",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BILLING_URL}/api/v1/invoices/{_state['invoice_id']}/line-items",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201
    assert r.json()["data"]["line_total"] == 5000.0


@pytest.mark.asyncio
async def test_send_invoice():
    from datetime import date, timedelta
    due = (date.today() + timedelta(days=30)).isoformat()
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BILLING_URL}/api/v1/invoices/{_state['invoice_id']}/send",
            json={"due_date": due},
            headers=HEADERS,
        )
    assert r.status_code == 200
    assert r.json()["data"]["status"] == "sent"


@pytest.mark.asyncio
async def test_record_full_payment():
    from datetime import date
    payload = {
        "payment_method": "bank_transfer",
        "amount": 5000.0,
        "payment_date": date.today().isoformat(),
        "reference_number": f"TXN-{TENANT_ID[:8]}",
    }
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BILLING_URL}/api/v1/invoices/{_state['invoice_id']}/payments",
            json=payload,
            headers=HEADERS,
        )
    assert r.status_code == 201


@pytest.mark.asyncio
async def test_invoice_status_is_paid():
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{BILLING_URL}/api/v1/invoices/{_state['invoice_id']}", headers=HEADERS
        )
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["status"] == "paid"
    assert float(data["balance_due"]) == 0.0
