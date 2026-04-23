"""Schedule Service — Core scheduling domain service with recurrence rules."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import structlog

from rainer_common.exceptions import ConflictError, ForbiddenError, NotFoundError

from ..infra.db.models import Schedule, ScheduleEvent
from ..infra.db.repositories import ScheduleEventRepository, ScheduleRepository

logger = structlog.get_logger(__name__)

RECURRENCE_INTERVALS = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "biweekly": timedelta(weeks=2),
    "monthly": timedelta(days=30),
    "quarterly": timedelta(days=91),
    "semi-annual": timedelta(days=182),
    "annual": timedelta(days=365),
}


class ScheduleDomainService:
    """Generic recurring schedule management for any entity type."""

    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        event_repo: ScheduleEventRepository,
        tenant_id: str,
    ) -> None:
        self._schedules = schedule_repo
        self._events = event_repo
        self._tenant_id = tenant_id

    async def create_schedule(
        self,
        name: str,
        entity_type: str,
        recurrence_rule: str,
        created_by: str,
        description: str | None = None,
        entity_id: str | None = None,
        advance_notice_days: int = 7,
        owner_id: str | None = None,
        start_date: datetime | None = None,
        metadata: dict | None = None,
    ) -> Schedule:
        """Create a recurring schedule with automatic next_occurrence calculation."""
        if recurrence_rule not in RECURRENCE_INTERVALS and not recurrence_rule.startswith("custom:"):
            raise ValueError(
                f"Invalid recurrence_rule '{recurrence_rule}'. "
                f"Valid options: {list(RECURRENCE_INTERVALS.keys())} or 'custom:N_days'"
            )

        next_occurrence = self._calculate_next_occurrence(
            recurrence_rule, start_date or datetime.now(timezone.utc)
        )

        schedule = await self._schedules.create(
            tenant_id=self._tenant_id,
            name=name,
            entity_type=entity_type,
            recurrence_rule=recurrence_rule,
            created_by=created_by,
            description=description,
            entity_id=entity_id,
            advance_notice_days=advance_notice_days,
            owner_id=owner_id or created_by,
            next_occurrence=next_occurrence,
            metadata=metadata or {},
        )
        logger.info("schedule_created", schedule_id=schedule.id, entity_type=entity_type)
        return schedule

    async def get_schedule(self, schedule_id: str) -> Schedule:
        schedule = await self._schedules.get_by_id(schedule_id)
        if not schedule:
            raise NotFoundError("Schedule", schedule_id)
        if schedule.tenant_id != self._tenant_id:
            raise ForbiddenError("Access denied to this schedule")
        return schedule

    async def list_schedules(
        self,
        entity_type: str | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[Schedule], int]:
        return await self._schedules.list_schedules(
            tenant_id=self._tenant_id,
            entity_type=entity_type,
            is_active=is_active,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def get_upcoming_events(
        self, days_ahead: int = 30
    ) -> list[tuple[Schedule, list[ScheduleEvent]]]:
        """Get schedules with upcoming events in the next N days."""
        threshold = datetime.now(timezone.utc) + timedelta(days=days_ahead)
        schedules = await self._schedules.get_upcoming(self._tenant_id, threshold)
        result = []
        for schedule in schedules:
            events = await self._events.list_by_schedule(schedule.id, status="pending")
            result.append((schedule, events))
        return result

    async def acknowledge_event(
        self, schedule_id: str, event_id: str, acknowledged_by: str, notes: str | None = None
    ) -> ScheduleEvent:
        await self.get_schedule(schedule_id)
        event = await self._events.get_by_id(event_id)
        if not event or event.schedule_id != schedule_id:
            raise NotFoundError("ScheduleEvent", event_id)

        await self._events.acknowledge(
            event_id=event_id,
            acknowledged_by=acknowledged_by,
            notes=notes,
        )
        logger.info("schedule_event_acknowledged", event_id=event_id)
        return await self._events.get_by_id(event_id)

    async def deactivate_schedule(self, schedule_id: str) -> Schedule:
        await self.get_schedule(schedule_id)
        await self._schedules.update(schedule_id, is_active=False)
        logger.info("schedule_deactivated", schedule_id=schedule_id)
        return await self.get_schedule(schedule_id)

    async def advance_schedule(self, schedule_id: str) -> Schedule:
        """Advance schedule to next occurrence after acknowledging current."""
        schedule = await self.get_schedule(schedule_id)
        new_next = self._calculate_next_occurrence(
            schedule.recurrence_rule, datetime.now(timezone.utc)
        )
        await self._schedules.update(
            schedule_id,
            last_occurrence=schedule.next_occurrence,
            next_occurrence=new_next,
        )

        # Create next scheduled event
        await self._events.create(
            schedule_id=schedule_id,
            tenant_id=self._tenant_id,
            scheduled_at=new_next,
        )

        return await self.get_schedule(schedule_id)

    def _calculate_next_occurrence(
        self, recurrence_rule: str, from_date: datetime
    ) -> datetime:
        if recurrence_rule.startswith("custom:"):
            days = int(recurrence_rule.split(":", 1)[1].replace("_days", ""))
            return from_date + timedelta(days=days)
        interval = RECURRENCE_INTERVALS.get(recurrence_rule)
        if interval:
            return from_date + interval
        return from_date + timedelta(days=365)
