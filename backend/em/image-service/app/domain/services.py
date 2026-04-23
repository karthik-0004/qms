"""Image Service — Domain service layer."""

from datetime import datetime, timezone

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..infra.db.repositories import PlateImageRepository
from ..infra.db.models import PlateImage

logger = structlog.get_logger(__name__)

VALID_IMAGE_TYPES = {"brightfield", "fluorescence", "uv", "composite"}


class ImageServiceError(Exception):
    pass


class ImageNotFoundError(ImageServiceError):
    pass


class InvalidImageTypeError(ImageServiceError):
    pass


class ImageDomainService:
    def __init__(self, db: AsyncSession) -> None:
        self._repo = PlateImageRepository(db)

    async def register_image(
        self,
        tenant_id: str,
        plate_id: str,
        image_key: str,
        image_type: str,
        captured_at: datetime,
        uploaded_by: str,
        file_size_bytes: int = 0,
        width_px: int | None = None,
        height_px: int | None = None,
        resolution_dpi: int | None = None,
        magnification: float | None = None,
        camera_settings: dict | None = None,
        is_primary: bool = False,
    ) -> PlateImage:
        if image_type not in VALID_IMAGE_TYPES:
            raise InvalidImageTypeError(
                f"Image type '{image_type}' is not valid. "
                f"Allowed: {sorted(VALID_IMAGE_TYPES)}"
            )

        image = await self._repo.create(
            tenant_id=tenant_id,
            plate_id=plate_id,
            image_key=image_key,
            image_type=image_type,
            captured_at=captured_at,
            uploaded_by=uploaded_by,
            file_size_bytes=file_size_bytes,
            width_px=width_px,
            height_px=height_px,
            resolution_dpi=resolution_dpi,
            magnification=magnification,
            camera_settings=camera_settings or {},
            is_primary=is_primary,
        )

        if is_primary:
            await self._repo.set_primary(plate_id, image.id)

        logger.info(
            "image.registered",
            image_id=image.id,
            plate_id=plate_id,
            image_type=image_type,
            tenant_id=tenant_id,
        )
        return image

    async def get_image(self, image_id: str) -> PlateImage:
        image = await self._repo.get_by_id(image_id)
        if not image:
            raise ImageNotFoundError(f"Image '{image_id}' not found.")
        return image

    async def list_images_for_plate(
        self,
        plate_id: str,
        image_type: str | None = None,
    ) -> list[PlateImage]:
        return await self._repo.list_by_plate(plate_id, image_type=image_type)

    async def list_images(
        self,
        tenant_id: str,
        status: str | None = None,
        offset: int = 0,
        limit: int = 20,
    ) -> tuple[list[PlateImage], int]:
        return await self._repo.list_by_tenant(
            tenant_id=tenant_id,
            status=status,
            offset=offset,
            limit=limit,
        )

    async def get_primary_image(self, plate_id: str) -> PlateImage | None:
        return await self._repo.get_primary_for_plate(plate_id)

    async def set_primary(self, plate_id: str, image_id: str) -> PlateImage:
        image = await self.get_image(image_id)
        if image.plate_id != plate_id:
            raise ImageNotFoundError(f"Image '{image_id}' does not belong to plate '{plate_id}'.")
        await self._repo.set_primary(plate_id, image_id)
        logger.info("image.primary_set", image_id=image_id, plate_id=plate_id)
        return await self.get_image(image_id)

    async def update_status(self, image_id: str, status: str) -> PlateImage:
        await self._repo.update(image_id, status=status)
        return await self.get_image(image_id)

    async def delete_image(self, image_id: str) -> None:
        await self.get_image(image_id)
        await self._repo.soft_delete(image_id)
        logger.info("image.deleted", image_id=image_id)
