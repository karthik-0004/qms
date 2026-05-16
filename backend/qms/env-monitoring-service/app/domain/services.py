"""Env Monitoring Service — Environmental monitoring domain service."""

from datetime import datetime, timezone

import structlog

from rainer_common.exceptions import ForbiddenError, NotFoundError

from ..infra.db.models import MonitoringPoint, MonitoringReading
from ..infra.db.repositories import MonitoringPointRepository, MonitoringReadingRepository

logger = structlog.get_logger(__name__)


def _detect_reading_status(value: float, alert_limit: float | None, action_limit: float | None) -> str:
    """Determine exceedance status based on configured limits."""
    if action_limit is not None and value > action_limit:
        return "action_limit_exceeded"
    if alert_limit is not None and value > alert_limit:
        return "alert_limit_exceeded"
    return "within_limits"


class EnvMonitoringDomainService:
    """Environmental monitoring lifecycle: points, readings, excursions."""

    def __init__(
        self,
        point_repo: MonitoringPointRepository,
        reading_repo: MonitoringReadingRepository,
        tenant_id: str,
    ) -> None:
        self._points = point_repo
        self._readings = reading_repo
        self._tenant_id = tenant_id

    async def list_points(
        self,
        status: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[MonitoringPoint], int]:
        return await self._points.list_points(
            tenant_id=self._tenant_id,
            status=status,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def create_point(
        self,
        point_id: str,
        location: str,
        parameter: str,
        frequency_type: str,
        created_by: str,
        alert_limit: float | None = None,
        action_limit: float | None = None,
        frequency_value: int | None = None,
    ) -> MonitoringPoint:
        point = await self._points.create(
            tenant_id=self._tenant_id,
            point_id=point_id,
            location=location,
            parameter=parameter,
            frequency_type=frequency_type,
            created_by=created_by,
            alert_limit=alert_limit,
            action_limit=action_limit,
            frequency_value=frequency_value,
        )
        logger.info("monitoring_point_created", point_db_id=point.id, tenant=self._tenant_id)
        return point

    async def get_point(self, point_db_id: str) -> MonitoringPoint:
        point = await self._points.get_by_id(point_db_id)
        if not point:
            raise NotFoundError("MonitoringPoint", point_db_id)
        if point.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this monitoring point")
        return point

    async def update_point(self, point_db_id: str, **fields) -> MonitoringPoint:
        await self.get_point(point_db_id)
        allowed = {"location", "parameter", "alert_limit", "action_limit",
                   "frequency_type", "frequency_value", "status"}
        filtered = {k: v for k, v in fields.items() if k in allowed and v is not None}
        if filtered:
            await self._points.update(point_db_id, **filtered)
        return await self.get_point(point_db_id)

    async def add_reading(
        self,
        point_db_id: str,
        value: float,
        recorded_at: datetime,
        recorded_by_user_id: str | None = None,
        notes: str | None = None,
    ) -> MonitoringReading:
        point = await self.get_point(point_db_id)
        status = _detect_reading_status(value, point.alert_limit, point.action_limit)
        reading = await self._readings.create(
            tenant_id=self._tenant_id,
            point_id=point_db_id,
            value=value,
            recorded_at=recorded_at,
            status=status,
            recorded_by_user_id=recorded_by_user_id,
            notes=notes,
        )
        # Update last reading on the point
        await self._points.update(
            point_db_id,
            last_reading_value=value,
            last_reading_at=recorded_at,
        )
        logger.info("monitoring_reading_added", point_id=point_db_id, status=status)
        return reading

    async def list_readings(
        self,
        point_db_id: str,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[MonitoringReading]:
        await self.get_point(point_db_id)
        return await self._readings.list_by_point(point_db_id, from_date=from_date, to_date=to_date)

    async def list_excursions(self, point_db_id: str) -> list[MonitoringReading]:
        await self.get_point(point_db_id)
        return await self._readings.list_excursions(point_db_id)
