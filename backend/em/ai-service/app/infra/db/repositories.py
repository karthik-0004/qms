"""AI Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import AnalysisResult, AnalysisRun


class AnalysisRunRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, run_id: str) -> AnalysisRun | None:
        result = await self._db.execute(
            select(AnalysisRun).where(AnalysisRun.id == run_id)
        )
        return result.scalar_one_or_none()

    async def list_by_plate(self, plate_id: str) -> list[AnalysisRun]:
        result = await self._db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.plate_id == plate_id)
            .order_by(AnalysisRun.created_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[AnalysisRun], int]:
        query = select(AnalysisRun).where(AnalysisRun.tenant_id == tenant_id)
        count_q = select(func.count()).select_from(AnalysisRun).where(
            AnalysisRun.tenant_id == tenant_id
        )
        if status:
            query = query.where(AnalysisRun.status == status)
            count_q = count_q.where(AnalysisRun.status == status)

        query = query.offset(offset).limit(limit).order_by(AnalysisRun.created_at.desc())
        items = list((await self._db.execute(query)).scalars().all())
        total = (await self._db.execute(count_q)).scalar_one()
        return items, total

    async def create(
        self,
        tenant_id: str,
        plate_id: str,
        image_id: str,
        model_name: str,
        model_version: str,
        triggered_by: str,
        job_id: str | None = None,
    ) -> AnalysisRun:
        now = datetime.now(timezone.utc)
        run = AnalysisRun(
            id=str(uuid4()),
            tenant_id=tenant_id,
            plate_id=plate_id,
            image_id=image_id,
            model_name=model_name,
            model_version=model_version,
            triggered_by=triggered_by,
            job_id=job_id,
            status="pending",
            created_at=now,
            updated_at=now,
        )
        self._db.add(run)
        await self._db.flush()
        return run

    async def update(self, run_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(AnalysisRun).where(AnalysisRun.id == run_id).values(**fields)
        )


class AnalysisResultRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_run_id(self, run_id: str) -> AnalysisResult | None:
        result = await self._db.execute(
            select(AnalysisResult).where(AnalysisResult.analysis_run_id == run_id)
        )
        return result.scalar_one_or_none()

    async def get_latest_for_plate(self, plate_id: str) -> AnalysisResult | None:
        result = await self._db.execute(
            select(AnalysisResult)
            .where(AnalysisResult.plate_id == plate_id)
            .order_by(AnalysisResult.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        analysis_run_id: str,
        tenant_id: str,
        plate_id: str,
        colony_count: int,
        colony_positions: list,
        confidence_score: float,
        contamination_detected: bool,
        raw_output: dict,
        contamination_type: str | None = None,
        anomaly_flags: list | None = None,
    ) -> AnalysisResult:
        result = AnalysisResult(
            id=str(uuid4()),
            analysis_run_id=analysis_run_id,
            tenant_id=tenant_id,
            plate_id=plate_id,
            colony_count=colony_count,
            colony_positions=colony_positions,
            confidence_score=confidence_score,
            contamination_detected=contamination_detected,
            contamination_type=contamination_type,
            anomaly_flags=anomaly_flags or [],
            raw_output=raw_output,
            created_at=datetime.now(timezone.utc),
        )
        self._db.add(result)
        await self._db.flush()
        return result
