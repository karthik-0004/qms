"""Image Service — Repository layer (tenant-scoped)."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .models import PlateImage


class PlateImageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_by_id(self, image_id: str) -> PlateImage | None:
        result = await self._db.execute(
            select(PlateImage).where(
                PlateImage.id == image_id,
                PlateImage.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_by_plate(
        self,
        plate_id: str,
        image_type: str | None = None,
    ) -> list[PlateImage]:
        query = select(PlateImage).where(
            PlateImage.plate_id == plate_id,
            PlateImage.deleted_at.is_(None),
        )
        if image_type:
            query = query.where(PlateImage.image_type == image_type)
        result = await self._db.execute(
            query.order_by(PlateImage.captured_at.desc())
        )
        return list(result.scalars().all())

    async def list_by_tenant(
        self,
        tenant_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[PlateImage], int]:
        query = select(PlateImage).where(
            PlateImage.tenant_id == tenant_id,
            PlateImage.deleted_at.is_(None),
        )
        count_q = select(func.count()).select_from(PlateImage).where(
            PlateImage.tenant_id == tenant_id,
            PlateImage.deleted_at.is_(None),
        )
        if status:
            query = query.where(PlateImage.status == status)
            count_q = count_q.where(PlateImage.status == status)

        query = query.offset(offset).limit(limit).order_by(PlateImage.captured_at.desc())
        items = list((await self._db.execute(query)).scalars().all())
        total = (await self._db.execute(count_q)).scalar_one()
        return items, total

    async def get_primary_for_plate(self, plate_id: str) -> PlateImage | None:
        result = await self._db.execute(
            select(PlateImage).where(
                PlateImage.plate_id == plate_id,
                PlateImage.is_primary.is_(True),
                PlateImage.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        tenant_id: str,
        plate_id: str,
        image_key: str,
        image_type: str,
        captured_at: datetime,
        uploaded_by: str,
        **kwargs,
    ) -> PlateImage:
        now = datetime.now(timezone.utc)
        image = PlateImage(
            id=str(uuid4()),
            tenant_id=tenant_id,
            plate_id=plate_id,
            image_key=image_key,
            image_type=image_type,
            captured_at=captured_at,
            uploaded_by=uploaded_by,
            status="uploaded",
            created_at=now,
            updated_at=now,
            **kwargs,
        )
        self._db.add(image)
        await self._db.flush()
        return image

    async def update(self, image_id: str, **fields) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self._db.execute(
            update(PlateImage).where(PlateImage.id == image_id).values(**fields)
        )

    async def set_primary(self, plate_id: str, image_id: str) -> None:
        """Clears existing primary then sets the given image as primary."""
        await self._db.execute(
            update(PlateImage)
            .where(PlateImage.plate_id == plate_id)
            .values(is_primary=False, updated_at=datetime.now(timezone.utc))
        )
        await self._db.execute(
            update(PlateImage)
            .where(PlateImage.id == image_id)
            .values(is_primary=True, updated_at=datetime.now(timezone.utc))
        )

    async def soft_delete(self, image_id: str) -> None:
        await self.update(image_id, deleted_at=datetime.now(timezone.utc))
