"""AI Service — Domain service layer."""

from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.repositories import AnalysisResultRepository, AnalysisRunRepository
from ..infra.db.models import AnalysisResult, AnalysisRun
from ..core.config import get_settings

logger = structlog.get_logger(__name__)


class AIServiceError(Exception):
    pass


class AnalysisRunNotFoundError(AIServiceError):
    pass


class AnalysisAlreadyRunningError(AIServiceError):
    pass


class AIDomainService:
    def __init__(self, db: AsyncSession) -> None:
        self._run_repo = AnalysisRunRepository(db)
        self._result_repo = AnalysisResultRepository(db)
        self._settings = get_settings()

    async def create_analysis_run(
        self,
        tenant_id: str,
        plate_id: str,
        image_id: str,
        triggered_by: str,
        job_id: str | None = None,
        model_name: str | None = None,
        model_version: str | None = None,
    ) -> AnalysisRun:
        run = await self._run_repo.create(
            tenant_id=tenant_id,
            plate_id=plate_id,
            image_id=image_id,
            model_name=model_name or self._settings.model_name,
            model_version=model_version or self._settings.model_version,
            triggered_by=triggered_by,
            job_id=job_id,
        )
        logger.info(
            "analysis_run.created",
            run_id=run.id,
            plate_id=plate_id,
            image_id=image_id,
            tenant_id=tenant_id,
        )
        return run

    async def get_run(self, run_id: str) -> AnalysisRun:
        run = await self._run_repo.get_by_id(run_id)
        if not run:
            raise AnalysisRunNotFoundError(f"Analysis run '{run_id}' not found.")
        return run

    async def list_runs(
        self,
        tenant_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AnalysisRun], int]:
        return await self._run_repo.list_by_tenant(
            tenant_id=tenant_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    async def list_runs_for_plate(self, plate_id: str) -> list[AnalysisRun]:
        return await self._run_repo.list_by_plate(plate_id)

    async def start_run(self, run_id: str) -> AnalysisRun:
        run = await self.get_run(run_id)
        if run.status not in ("pending",):
            raise AnalysisAlreadyRunningError(
                f"Run '{run_id}' is in status '{run.status}', cannot start."
            )
        await self._run_repo.update(
            run_id,
            status="running",
            started_at=datetime.now(timezone.utc),
        )
        logger.info("analysis_run.started", run_id=run_id)
        return await self.get_run(run_id)

    async def complete_run(
        self,
        run_id: str,
        colony_count: int,
        colony_positions: list,
        confidence_score: float,
        contamination_detected: bool,
        raw_output: dict,
        contamination_type: str | None = None,
        anomaly_flags: list | None = None,
    ) -> tuple[AnalysisRun, AnalysisResult]:
        run = await self.get_run(run_id)
        completed_at = datetime.now(timezone.utc)
        duration = None
        if run.started_at:
            duration = (completed_at - run.started_at).total_seconds()

        await self._run_repo.update(
            run_id,
            status="complete",
            completed_at=completed_at,
            duration_seconds=duration,
        )

        result = await self._result_repo.create(
            analysis_run_id=run_id,
            tenant_id=run.tenant_id,
            plate_id=run.plate_id,
            colony_count=colony_count,
            colony_positions=colony_positions,
            confidence_score=confidence_score,
            contamination_detected=contamination_detected,
            contamination_type=contamination_type,
            anomaly_flags=anomaly_flags or [],
            raw_output=raw_output,
        )
        logger.info(
            "analysis_run.completed",
            run_id=run_id,
            colony_count=colony_count,
            confidence_score=confidence_score,
            contamination=contamination_detected,
        )
        return await self.get_run(run_id), result

    async def fail_run(self, run_id: str, error_message: str) -> AnalysisRun:
        await self._run_repo.update(
            run_id,
            status="failed",
            completed_at=datetime.now(timezone.utc),
            error_message=error_message,
        )
        logger.warning("analysis_run.failed", run_id=run_id, error=error_message)
        return await self.get_run(run_id)

    async def get_result_for_run(self, run_id: str) -> AnalysisResult | None:
        return await self._result_repo.get_by_run_id(run_id)

    async def get_latest_result_for_plate(self, plate_id: str) -> AnalysisResult | None:
        return await self._result_repo.get_latest_for_plate(plate_id)
