"""Unit tests — ImageDomainService."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.domain.services import (
    ImageDomainService,
    ImageNotFoundError,
    InvalidImageTypeError,
)
from app.infra.db.models import PlateImage


def _make_image(**kwargs) -> PlateImage:
    defaults = dict(
        id=str(uuid4()),
        tenant_id=str(uuid4()),
        plate_id=str(uuid4()),
        image_key="tenants/abc/plates/123/img.tiff",
        image_type="brightfield",
        file_size_bytes=1024 * 1024 * 5,
        is_primary=False,
        status="uploaded",
        camera_settings={},
        captured_at=datetime.now(timezone.utc),
        uploaded_by=str(uuid4()),
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        deleted_at=None,
    )
    defaults.update(kwargs)
    return MagicMock(spec=PlateImage, **defaults)


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def service(mock_db):
    svc = ImageDomainService(mock_db)
    svc._repo = AsyncMock()
    return svc


# ─── register_image ───────────────────────────────────────────────────────────

class TestRegisterImage:
    async def test_registers_brightfield_image(self, service):
        plate_id = str(uuid4())
        image = _make_image(plate_id=plate_id, image_type="brightfield")
        service._repo.create.return_value = image

        result = await service.register_image(
            tenant_id=image.tenant_id,
            plate_id=plate_id,
            image_key="img.tiff",
            image_type="brightfield",
            captured_at=datetime.now(timezone.utc),
            uploaded_by=str(uuid4()),
        )

        assert result.image_type == "brightfield"
        service._repo.create.assert_awaited_once()

    async def test_sets_primary_when_flagged(self, service):
        plate_id = str(uuid4())
        image = _make_image(plate_id=plate_id, is_primary=True)
        service._repo.create.return_value = image

        await service.register_image(
            tenant_id=image.tenant_id,
            plate_id=plate_id,
            image_key="img.tiff",
            image_type="fluorescence",
            captured_at=datetime.now(timezone.utc),
            uploaded_by=str(uuid4()),
            is_primary=True,
        )

        service._repo.set_primary.assert_awaited_once_with(plate_id, image.id)

    async def test_invalid_type_raises(self, service):
        with pytest.raises(InvalidImageTypeError):
            await service.register_image(
                tenant_id=str(uuid4()),
                plate_id=str(uuid4()),
                image_key="img.png",
                image_type="xray",  # invalid
                captured_at=datetime.now(timezone.utc),
                uploaded_by=str(uuid4()),
            )


# ─── get_image ────────────────────────────────────────────────────────────────

class TestGetImage:
    async def test_returns_image(self, service):
        image = _make_image()
        service._repo.get_by_id.return_value = image

        result = await service.get_image(image.id)
        assert result.id == image.id

    async def test_raises_if_not_found(self, service):
        service._repo.get_by_id.return_value = None

        with pytest.raises(ImageNotFoundError):
            await service.get_image(str(uuid4()))


# ─── list_images_for_plate ───────────────────────────────────────────────────

class TestListImagesForPlate:
    async def test_returns_images(self, service):
        images = [_make_image() for _ in range(4)]
        service._repo.list_by_plate.return_value = images
        plate_id = str(uuid4())

        result = await service.list_images_for_plate(plate_id)

        assert len(result) == 4
        service._repo.list_by_plate.assert_awaited_once_with(plate_id, image_type=None)

    async def test_filters_by_type(self, service):
        images = [_make_image(image_type="fluorescence")]
        service._repo.list_by_plate.return_value = images
        plate_id = str(uuid4())

        await service.list_images_for_plate(plate_id, image_type="fluorescence")

        service._repo.list_by_plate.assert_awaited_once_with(plate_id, image_type="fluorescence")


# ─── set_primary ──────────────────────────────────────────────────────────────

class TestSetPrimary:
    async def test_sets_primary_correctly(self, service):
        plate_id = str(uuid4())
        image = _make_image(plate_id=plate_id)
        service._repo.get_by_id.return_value = image

        await service.set_primary(plate_id, image.id)

        service._repo.set_primary.assert_awaited_once_with(plate_id, image.id)

    async def test_raises_if_image_belongs_to_different_plate(self, service):
        image = _make_image(plate_id=str(uuid4()))
        service._repo.get_by_id.return_value = image

        with pytest.raises(ImageNotFoundError):
            await service.set_primary(str(uuid4()), image.id)


# ─── delete_image ─────────────────────────────────────────────────────────────

class TestDeleteImage:
    async def test_soft_deletes(self, service):
        image = _make_image()
        service._repo.get_by_id.return_value = image

        await service.delete_image(image.id)

        service._repo.soft_delete.assert_awaited_once_with(image.id)
