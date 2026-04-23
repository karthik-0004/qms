"""Unit tests — FileDomainService business logic."""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from rainer_common.exceptions import ForbiddenError, NotFoundError, ValidationError

from app.core.config import Settings
from app.domain.services import FileDomainService
from app.infra.db.models import FileRecord


def make_settings(**kwargs) -> Settings:
    defaults = dict(
        rainer_env="testing",
        database_url="sqlite+aiosqlite:///:memory:",
        s3_endpoint_url="http://localhost:9000",
        s3_access_key_id="test",
        s3_secret_access_key="test",
        s3_bucket_name="test-bucket",
        max_file_size_mb=10,
        enable_virus_scan=False,
        allowed_mime_types=["application/pdf", "image/jpeg", "text/plain"],
    )
    defaults.update(kwargs)
    return Settings(**defaults)


def make_file(**kwargs) -> FileRecord:
    defaults = dict(
        id=str(uuid4()), tenant_id=str(uuid4()), uploaded_by=str(uuid4()),
        filename="test.pdf", original_filename="test.pdf",
        content_type="application/pdf", size_bytes=1024,
        s3_key="tenant/misc/test.pdf", s3_bucket="test-bucket",
        entity_type="document", entity_id=str(uuid4()), module="qms",
        is_public=False, is_deleted=False, virus_scan_status="clean",
        metadata_={}, current_version=1,
    )
    defaults.update(kwargs)
    f = MagicMock(spec=FileRecord)
    for k, v in defaults.items():
        setattr(f, k, v)
    return f


@pytest.fixture
def file_repo():
    return AsyncMock()


@pytest.fixture
def version_repo():
    return AsyncMock()


@pytest.fixture
def svc(file_repo, version_repo):
    s = FileDomainService.__new__(FileDomainService)
    s._files = file_repo
    s._versions = version_repo
    s._settings = make_settings()
    s._s3 = MagicMock()
    return s


class TestUploadFile:
    @pytest.mark.asyncio
    async def test_uploads_successfully(self, svc, file_repo):
        mock_file = make_file()
        file_repo.create.return_value = mock_file
        file_repo.update_virus_scan.return_value = None
        svc._s3.put_object.return_value = {}

        result = await svc.upload_file(
            file_content=b"PDF content here",
            original_filename="report.pdf",
            content_type="application/pdf",
            tenant_id=str(uuid4()),
        )
        assert result is mock_file
        svc._s3.put_object.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_on_file_too_large(self, svc):
        large_content = b"x" * (11 * 1024 * 1024)  # 11MB > 10MB limit
        with pytest.raises(ValidationError, match="exceeds maximum"):
            await svc.upload_file(
                file_content=large_content,
                original_filename="large.pdf",
                content_type="application/pdf",
            )

    @pytest.mark.asyncio
    async def test_raises_on_disallowed_mime_type(self, svc):
        with pytest.raises(ValidationError, match="not allowed"):
            await svc.upload_file(
                file_content=b"content",
                original_filename="script.sh",
                content_type="application/x-shellscript",
            )


class TestGetFile:
    @pytest.mark.asyncio
    async def test_returns_file(self, svc, file_repo):
        f = make_file()
        file_repo.get_by_id.return_value = f
        result = await svc.get_file(f.id)
        assert result is f

    @pytest.mark.asyncio
    async def test_raises_not_found(self, svc, file_repo):
        file_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            await svc.get_file("nonexistent")


class TestGetDownloadUrl:
    @pytest.mark.asyncio
    async def test_generates_presigned_url(self, svc, file_repo):
        f = make_file(virus_scan_status="clean")
        file_repo.get_by_id.return_value = f
        svc._s3.generate_presigned_url.return_value = "https://s3.example.com/presigned"

        url = await svc.get_download_url(f.id)
        assert url == "https://s3.example.com/presigned"
        svc._s3.generate_presigned_url.assert_called_once()

    @pytest.mark.asyncio
    async def test_raises_for_infected_file(self, svc, file_repo):
        f = make_file(virus_scan_status="infected")
        file_repo.get_by_id.return_value = f
        with pytest.raises(ForbiddenError, match="virus scan"):
            await svc.get_download_url(f.id)


class TestDeleteFile:
    @pytest.mark.asyncio
    async def test_soft_deletes_file(self, svc, file_repo):
        f = make_file()
        file_repo.get_by_id.return_value = f
        file_repo.soft_delete.return_value = None

        await svc.delete_file(f.id)
        file_repo.soft_delete.assert_called_with(f.id)
