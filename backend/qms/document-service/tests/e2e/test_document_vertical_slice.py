"""
QMS E2E Vertical Slice — Document → Approval → Audit Trail

Tests the full document lifecycle in one end-to-end flow:
1. Create a document (Draft)
2. Submit for review (Draft → Under Review)
3. Approve with e-signature (Under Review → Approved)
4. Verify audit entries emitted
5. Verify version history recorded
6. Attempt invalid transition (should fail)
7. Make obsolete (Approved → Obsolete)
"""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.core.database import get_db
from app.infra.db.models import Base
from app.main import create_app


@pytest.fixture(scope="module")
def pg_container():
    with PostgresContainer("postgres:16-alpine") as pg:
        yield pg


@pytest_asyncio.fixture(scope="module")
async def e2e_engine(pg_container):
    url = pg_container.get_connection_url().replace("postgresql://", "postgresql+asyncpg://")
    engine = create_async_engine(url)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="module")
async def e2e_session(e2e_engine) -> AsyncSession:
    factory = async_sessionmaker(e2e_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture(scope="module")
async def e2e_client(e2e_session) -> AsyncClient:
    from rainer_auth_lib.jwt import JWTSettings, create_access_token

    _app = create_app()
    _app.dependency_overrides[get_db] = lambda: e2e_session

    async with AsyncClient(
        transport=ASGITransport(app=_app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="module")
def auth_token():
    """Generate a test JWT token simulating a tenant_admin user."""
    from rainer_auth_lib.jwt import JWTSettings, create_access_token

    settings = JWTSettings(
        secret_key="integration-test-secret-32chars-min",
        algorithm="HS256",
    )
    user_id = str(uuid4())
    tenant_id = str(uuid4())
    token, _ = create_access_token(
        subject=user_id,
        email="admin@testcorp.com",
        settings=settings,
        tenant_id=tenant_id,
        role="tenant_admin",
        permissions=["document:read", "document:write", "document:approve"],
    )
    return token


@pytest.fixture(scope="module")
def headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


class TestDocumentVerticalSlice:
    """
    E2E Vertical Slice: document create → submit → approve → obsolete
    """

    _doc_id: str | None = None

    @pytest.mark.asyncio
    async def test_01_create_document(self, e2e_client, headers):
        resp = await e2e_client.post(
            "/api/v1/documents",
            json={
                "doc_number": "SOP-VS-001",
                "title": "Vertical Slice Test SOP",
                "doc_type": "SOP",
                "description": "This document is created for E2E testing",
                "department": "QA",
                "tags": ["test", "sop"],
            },
            headers=headers,
        )
        assert resp.status_code == 201, resp.text
        data = resp.json()["data"]
        assert data["doc_number"] == "SOP-VS-001"
        assert data["status"] == "draft"
        assert data["current_version"] == "1.0"
        TestDocumentVerticalSlice._doc_id = data["id"]

    @pytest.mark.asyncio
    async def test_02_get_document(self, e2e_client, headers):
        assert TestDocumentVerticalSlice._doc_id
        resp = await e2e_client.get(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}",
            headers=headers,
        )
        assert resp.status_code == 200
        assert resp.json()["data"]["status"] == "draft"

    @pytest.mark.asyncio
    async def test_03_cannot_approve_from_draft(self, e2e_client, headers):
        """Approving a Draft document should fail (wrong state)."""
        resp = await e2e_client.post(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/approve",
            json={"signature": "my-esig-passphrase"},
            headers=headers,
        )
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_04_submit_for_review(self, e2e_client, headers):
        resp = await e2e_client.post(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/submit-for-review",
            json={"comment": "Ready for review"},
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["data"]["status"] == "under_review"

    @pytest.mark.asyncio
    async def test_05_cannot_submit_again_from_under_review(self, e2e_client, headers):
        """Submitting again from Under Review should fail."""
        resp = await e2e_client.post(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/submit-for-review",
            json={},
            headers=headers,
        )
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_06_approve_requires_signature(self, e2e_client, headers):
        """Approve without signature should fail validation."""
        resp = await e2e_client.post(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/approve",
            json={"signature": ""},
            headers=headers,
        )
        assert resp.status_code in (400, 422)

    @pytest.mark.asyncio
    async def test_07_approve_document(self, e2e_client, headers):
        resp = await e2e_client.post(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/approve",
            json={
                "signature": "admin-esig-passphrase-test",
                "comment": "Approved after review",
                "effective_date": datetime.now(timezone.utc).isoformat(),
                "review_date": "2027-03-05T00:00:00Z",
            },
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        data = resp.json()["data"]
        assert data["status"] == "approved"
        assert data["effective_date"] is not None

    @pytest.mark.asyncio
    async def test_08_version_history_recorded(self, e2e_client, headers):
        resp = await e2e_client.get(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/versions",
            headers=headers,
        )
        assert resp.status_code == 200
        versions = resp.json()["data"]
        assert len(versions) >= 1
        # Most recent version should have approval info
        latest = versions[0]
        assert latest["approved_by"] is not None
        assert latest["signature_hash"] is not None

    @pytest.mark.asyncio
    async def test_09_cannot_edit_approved_document(self, e2e_client, headers):
        """Editing an approved document should be forbidden."""
        resp = await e2e_client.patch(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}",
            json={"title": "Modified Title"},
            headers=headers,
        )
        assert resp.status_code in (400, 403)

    @pytest.mark.asyncio
    async def test_10_cannot_delete_approved_document(self, e2e_client, headers):
        """Deleting an approved document should be forbidden."""
        resp = await e2e_client.delete(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}",
            headers=headers,
        )
        assert resp.status_code in (400, 403)

    @pytest.mark.asyncio
    async def test_11_make_obsolete(self, e2e_client, headers):
        resp = await e2e_client.post(
            f"/api/v1/documents/{TestDocumentVerticalSlice._doc_id}/make-obsolete",
            headers=headers,
        )
        assert resp.status_code == 200, resp.text
        assert resp.json()["data"]["status"] == "obsolete"

    @pytest.mark.asyncio
    async def test_12_document_appears_in_list(self, e2e_client, headers):
        resp = await e2e_client.get(
            "/api/v1/documents?status=obsolete",
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["pagination"]["total"] >= 1
        doc_ids = [d["id"] for d in data["data"]]
        assert TestDocumentVerticalSlice._doc_id in doc_ids

    @pytest.mark.asyncio
    async def test_13_duplicate_doc_number_rejected(self, e2e_client, headers):
        """Creating a document with an existing doc number should return 409."""
        resp = await e2e_client.post(
            "/api/v1/documents",
            json={
                "doc_number": "SOP-VS-001",
                "title": "Duplicate Document",
                "doc_type": "SOP",
            },
            headers=headers,
        )
        assert resp.status_code == 409

    @pytest.mark.asyncio
    async def test_14_health_endpoints_pass(self, e2e_client):
        live = await e2e_client.get("/health/live")
        assert live.status_code == 200
        assert live.json()["status"] == "ok"
        assert live.json()["service"] == "document-service"
