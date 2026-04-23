"""
Phase C — EndGameBiotech EM Vertical Slice E2E Tests

Tests the full EM workflow:
  register_plate → sampling → incubation → imaging → AI analysis → QA review → approve

These tests assume a running stack (docker-compose up) and use httpx for HTTP calls.
Skipped automatically if EM_E2E_BASE_URL is not set.
"""

import os
import pytest
import httpx

PLATE_URL = os.getenv("EM_PLATE_URL", "http://localhost:8030")
IMAGE_URL = os.getenv("EM_IMAGE_URL", "http://localhost:8031")
AI_URL = os.getenv("EM_AI_URL", "http://localhost:8032")
JOB_URL = os.getenv("EM_JOB_URL", "http://localhost:8033")
QA_URL = os.getenv("EM_QA_URL", "http://localhost:8034")

RUN_E2E = os.getenv("EM_E2E_ENABLED", "false").lower() == "true"

pytestmark = pytest.mark.skipif(not RUN_E2E, reason="EM_E2E_ENABLED not set — skipping E2E tests")

TENANT_ID = "00000000-0000-0000-0000-000000000001"
USER_ID   = "00000000-0000-0000-0000-000000000002"
HEADERS   = {
    "X-Tenant-ID": TENANT_ID,
    "X-User-ID": USER_ID,
    "Content-Type": "application/json",
}

# Shared state across test cases (collected via pytest ordering)
_state: dict = {}


# ─── Health Checks ─────────────────────────────────────────────────────────────

class TestHealthChecks:
    """TC-EM-001 through TC-EM-005: All 5 services must be healthy."""

    def test_tc_em_001_plate_service_healthy(self):
        r = httpx.get(f"{PLATE_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_tc_em_002_image_service_healthy(self):
        r = httpx.get(f"{IMAGE_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_tc_em_003_ai_service_healthy(self):
        r = httpx.get(f"{AI_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_tc_em_004_job_service_healthy(self):
        r = httpx.get(f"{JOB_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"

    def test_tc_em_005_qa_review_service_healthy(self):
        r = httpx.get(f"{QA_URL}/health", timeout=5)
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


# ─── Plate Registration ─────────────────────────────────────────────────────────

class TestPlateRegistration:
    """TC-EM-006 through TC-EM-008: Plate registration."""

    def test_tc_em_006_register_plate(self):
        r = httpx.post(
            f"{PLATE_URL}/api/v1/plates",
            json={
                "barcode": "PLATE-E2E-001",
                "sample_type": "settle_plate",
                "media_type": "TSA",
                "incubation_temp_celsius": 32.5,
                "incubation_hours": 72,
                "location_code": "CLEANROOM-A1",
                "lot_number": "LOT-2024-001",
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 201
        plate = r.json()
        assert plate["barcode"] == "PLATE-E2E-001"
        assert plate["status"] == "registered"
        _state["plate_id"] = plate["id"]

    def test_tc_em_007_duplicate_barcode_rejected(self):
        r = httpx.post(
            f"{PLATE_URL}/api/v1/plates",
            json={
                "barcode": "PLATE-E2E-001",  # duplicate
                "sample_type": "settle_plate",
                "media_type": "TSA",
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 409

    def test_tc_em_008_get_plate(self):
        plate_id = _state["plate_id"]
        r = httpx.get(f"{PLATE_URL}/api/v1/plates/{plate_id}", headers=HEADERS, timeout=10)
        assert r.status_code == 200
        assert r.json()["id"] == plate_id


# ─── Plate Status Transitions ──────────────────────────────────────────────────

class TestPlateWorkflow:
    """TC-EM-009 through TC-EM-012: Plate lifecycle transitions."""

    def test_tc_em_009_start_sampling(self):
        plate_id = _state["plate_id"]
        r = httpx.patch(
            f"{PLATE_URL}/api/v1/plates/{plate_id}/status",
            json={"new_status": "sampling_in_progress"},
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "sampling_in_progress"

    def test_tc_em_010_complete_sampling(self):
        plate_id = _state["plate_id"]
        r = httpx.patch(
            f"{PLATE_URL}/api/v1/plates/{plate_id}/status",
            json={"new_status": "sampled"},
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "sampled"
        # sampled_at should be set
        assert r.json().get("sampled_at") is not None

    def test_tc_em_011_invalid_transition_rejected(self):
        plate_id = _state["plate_id"]
        r = httpx.patch(
            f"{PLATE_URL}/api/v1/plates/{plate_id}/status",
            json={"new_status": "approved"},  # invalid from sampled
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 422

    def test_tc_em_012_start_incubation(self):
        plate_id = _state["plate_id"]
        r = httpx.patch(
            f"{PLATE_URL}/api/v1/plates/{plate_id}/status",
            json={"new_status": "incubation_started"},
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "incubation_started"


# ─── Image Capture ─────────────────────────────────────────────────────────────

class TestImageCapture:
    """TC-EM-013 through TC-EM-015: Image registration."""

    def test_tc_em_013_register_primary_image(self):
        plate_id = _state["plate_id"]
        r = httpx.post(
            f"{IMAGE_URL}/api/v1/images",
            json={
                "plate_id": plate_id,
                "image_key": f"tenants/{TENANT_ID}/plates/{plate_id}/brightfield.tiff",
                "image_type": "brightfield",
                "file_size_bytes": 5242880,
                "width_px": 4096,
                "height_px": 4096,
                "resolution_dpi": 600,
                "magnification": 1.5,
                "camera_settings": {"exposure_ms": 100, "gain": 2},
                "is_primary": True,
                "captured_at": "2025-03-05T09:00:00Z",
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 201
        image = r.json()
        assert image["image_type"] == "brightfield"
        assert image["is_primary"] is True
        _state["image_id"] = image["id"]

    def test_tc_em_014_invalid_image_type_rejected(self):
        r = httpx.post(
            f"{IMAGE_URL}/api/v1/images",
            json={
                "plate_id": _state["plate_id"],
                "image_key": "img.png",
                "image_type": "xray",  # invalid
                "captured_at": "2025-03-05T09:00:00Z",
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 422

    def test_tc_em_015_list_images_for_plate(self):
        plate_id = _state["plate_id"]
        r = httpx.get(
            f"{IMAGE_URL}/api/v1/plates/{plate_id}/images",
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        images = r.json()
        assert len(images) >= 1


# ─── AI Analysis ───────────────────────────────────────────────────────────────

class TestAIAnalysis:
    """TC-EM-016 through TC-EM-019: AI analysis run lifecycle."""

    def test_tc_em_016_enqueue_ai_job(self):
        plate_id = _state["plate_id"]
        image_id = _state["image_id"]
        r = httpx.post(
            f"{JOB_URL}/api/v1/jobs",
            json={
                "job_type": "ai_analysis",
                "payload": {"plate_id": plate_id, "image_id": image_id},
                "priority": 3,
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 201
        job = r.json()
        assert job["status"] == "pending"
        _state["job_id"] = job["id"]

    def test_tc_em_017_create_analysis_run(self):
        r = httpx.post(
            f"{AI_URL}/api/v1/analysis-runs",
            json={
                "plate_id": _state["plate_id"],
                "image_id": _state["image_id"],
                "job_id": _state["job_id"],
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 201
        run = r.json()
        assert run["status"] == "pending"
        _state["run_id"] = run["id"]

    def test_tc_em_018_complete_analysis_with_results(self):
        run_id = _state["run_id"]
        # Start run
        r = httpx.patch(
            f"{AI_URL}/api/v1/analysis-runs/{run_id}/start",
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "running"

        # Complete run with results
        r = httpx.patch(
            f"{AI_URL}/api/v1/analysis-runs/{run_id}/complete",
            json={
                "colony_count": 42,
                "colony_positions": [{"x": 100, "y": 200}, {"x": 300, "y": 400}],
                "confidence_score": 0.97,
                "contamination_detected": False,
                "anomaly_flags": [],
                "raw_output": {"model_version": "1.0.0"},
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "complete"

    def test_tc_em_019_get_analysis_result(self):
        run_id = _state["run_id"]
        r = httpx.get(
            f"{AI_URL}/api/v1/analysis-runs/{run_id}/result",
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        result = r.json()
        assert result["colony_count"] == 42
        assert result["confidence_score"] == 0.97
        assert result["contamination_detected"] is False


# ─── QA Review ─────────────────────────────────────────────────────────────────

class TestQAReview:
    """TC-EM-020 through TC-EM-025: QA review workflow."""

    REVIEWER_ID = "00000000-0000-0000-0000-000000000099"

    def test_tc_em_020_create_qa_review(self):
        r = httpx.post(
            f"{QA_URL}/api/v1/reviews",
            json={
                "plate_id": _state["plate_id"],
                "analysis_run_id": _state["run_id"],
                "priority": "normal",
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 201
        review = r.json()
        assert review["status"] == "pending"
        _state["review_id"] = review["id"]

    def test_tc_em_021_assign_reviewer(self):
        review_id = _state["review_id"]
        r = httpx.patch(
            f"{QA_URL}/api/v1/reviews/{review_id}/assign",
            json={"reviewer_id": self.REVIEWER_ID},
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["reviewer_id"] == self.REVIEWER_ID

    def test_tc_em_022_start_review(self):
        review_id = _state["review_id"]
        r = httpx.patch(
            f"{QA_URL}/api/v1/reviews/{review_id}/status",
            json={"new_status": "in_review"},
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        assert r.json()["status"] == "in_review"
        assert r.json()["review_started_at"] is not None

    def test_tc_em_023_add_comment(self):
        review_id = _state["review_id"]
        r = httpx.post(
            f"{QA_URL}/api/v1/reviews/{review_id}/comments",
            json={
                "body": "Colony count confirmed. Results within specification.",
                "is_internal": False,
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 201
        assert r.json()["body"] == "Colony count confirmed. Results within specification."

    def test_tc_em_024_approve_review(self):
        review_id = _state["review_id"]
        r = httpx.patch(
            f"{QA_URL}/api/v1/reviews/{review_id}/status",
            json={
                "new_status": "approved",
                "decision": "approved",
                "ai_result_accepted": True,
                "review_notes": "AI colony detection accurate. No contamination observed.",
            },
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 200
        review = r.json()
        assert review["status"] == "approved"
        assert review["ai_result_accepted"] is True
        assert review["review_completed_at"] is not None

    def test_tc_em_025_approved_cannot_transition(self):
        review_id = _state["review_id"]
        r = httpx.patch(
            f"{QA_URL}/api/v1/reviews/{review_id}/status",
            json={"new_status": "in_review"},  # approved → in_review is invalid
            headers=HEADERS,
            timeout=10,
        )
        assert r.status_code == 422
