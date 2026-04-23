"""Unit tests — AIDomainService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.domain.services import (
    AIDomainService,
    AnalysisAlreadyRunningError,
    AnalysisRunNotFoundError,
)
from app.infra.db.models import AnalysisResult, AnalysisRun


def _make_run(**kwargs) -> AnalysisRun:
    defaults = dict(
        id=str(uuid4()),
        tenant_id=str(uuid4()),
        plate_id=str(uuid4()),
        image_id=str(uuid4()),
        model_name="endgame-colony-detector-v1",
        model_version="1.0.0",
        status="pending",
        triggered_by=str(uuid4()),
        started_at=None,
        completed_at=None,
        duration_seconds=None,
        error_message=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return MagicMock(spec=AnalysisRun, **defaults)


def _make_result(**kwargs) -> AnalysisResult:
    defaults = dict(
        id=str(uuid4()),
        analysis_run_id=str(uuid4()),
        tenant_id=str(uuid4()),
        plate_id=str(uuid4()),
        colony_count=42,
        colony_positions=[],
        confidence_score=0.97,
        contamination_detected=False,
        anomaly_flags=[],
        raw_output={},
        created_at=datetime.now(timezone.utc),
    )
    defaults.update(kwargs)
    return MagicMock(spec=AnalysisResult, **defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    with patch("app.domain.services.get_settings") as mock_settings:
        mock_settings.return_value = MagicMock(
            model_name="endgame-colony-detector-v1",
            model_version="1.0.0",
        )
        svc = AIDomainService(mock_db)
        svc._run_repo = AsyncMock()
        svc._result_repo = AsyncMock()
        yield svc


# ─── create_analysis_run ─────────────────────────────────────────────────────

class TestCreateAnalysisRun:
    async def test_creates_run(self, service):
        run = _make_run()
        service._run_repo.create.return_value = run

        result = await service.create_analysis_run(
            tenant_id=run.tenant_id,
            plate_id=run.plate_id,
            image_id=run.image_id,
            triggered_by=run.triggered_by,
        )

        assert result.id == run.id
        service._run_repo.create.assert_awaited_once()

    async def test_uses_default_model(self, service):
        run = _make_run()
        service._run_repo.create.return_value = run

        await service.create_analysis_run(
            tenant_id=run.tenant_id,
            plate_id=run.plate_id,
            image_id=run.image_id,
            triggered_by=run.triggered_by,
        )

        kwargs = service._run_repo.create.call_args.kwargs
        assert kwargs["model_name"] == "endgame-colony-detector-v1"


# ─── get_run ──────────────────────────────────────────────────────────────────

class TestGetRun:
    async def test_returns_run(self, service):
        run = _make_run()
        service._run_repo.get_by_id.return_value = run

        result = await service.get_run(run.id)
        assert result.id == run.id

    async def test_raises_if_not_found(self, service):
        service._run_repo.get_by_id.return_value = None

        with pytest.raises(AnalysisRunNotFoundError):
            await service.get_run(str(uuid4()))


# ─── start_run ────────────────────────────────────────────────────────────────

class TestStartRun:
    async def test_transitions_pending_to_running(self, service):
        run = _make_run(status="pending")
        updated = _make_run(status="running")
        service._run_repo.get_by_id.side_effect = [run, updated]

        result = await service.start_run(run.id)

        assert result.status == "running"
        service._run_repo.update.assert_awaited_once()

    async def test_raises_if_already_running(self, service):
        run = _make_run(status="running")
        service._run_repo.get_by_id.return_value = run

        with pytest.raises(AnalysisAlreadyRunningError):
            await service.start_run(run.id)


# ─── complete_run ─────────────────────────────────────────────────────────────

class TestCompleteRun:
    async def test_completes_run_and_creates_result(self, service):
        run = _make_run(status="running", started_at=datetime.now(timezone.utc))
        completed_run = _make_run(status="complete")
        result_obj = _make_result(colony_count=25)
        service._run_repo.get_by_id.side_effect = [run, completed_run]
        service._result_repo.create.return_value = result_obj

        final_run, result = await service.complete_run(
            run_id=run.id,
            colony_count=25,
            colony_positions=[{"x": 100, "y": 200}],
            confidence_score=0.95,
            contamination_detected=False,
            raw_output={"raw": True},
        )

        assert final_run.status == "complete"
        assert result.colony_count == 25
        service._result_repo.create.assert_awaited_once()

    async def test_calculates_duration(self, service):
        started = datetime.now(timezone.utc)
        run = _make_run(status="running", started_at=started)
        completed_run = _make_run(status="complete")
        service._run_repo.get_by_id.side_effect = [run, completed_run]
        service._result_repo.create.return_value = _make_result()

        await service.complete_run(
            run_id=run.id,
            colony_count=0,
            colony_positions=[],
            confidence_score=0.5,
            contamination_detected=False,
            raw_output={},
        )

        update_kwargs = service._run_repo.update.call_args.kwargs
        assert update_kwargs["duration_seconds"] is not None
        assert update_kwargs["duration_seconds"] >= 0


# ─── fail_run ─────────────────────────────────────────────────────────────────

class TestFailRun:
    async def test_marks_run_failed(self, service):
        run = _make_run(status="running")
        failed_run = _make_run(status="failed")
        service._run_repo.get_by_id.side_effect = [run, failed_run]

        result = await service.fail_run(run.id, "Model inference timeout")

        assert result.status == "failed"
        update_kwargs = service._run_repo.update.call_args.kwargs
        assert update_kwargs["error_message"] == "Model inference timeout"
