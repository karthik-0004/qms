"""File Service — Core file management domain service."""

import io
import mimetypes
import uuid
from datetime import timedelta

import boto3
import structlog
from botocore.exceptions import ClientError

from rainer_common.exceptions import ForbiddenError, NotFoundError, ValidationError

from ..core.config import Settings
from ..infra.db.models import FileRecord, FileVersion
from ..infra.db.repositories import FileRepository, FileVersionRepository

logger = structlog.get_logger(__name__)


class FileDomainService:
    def __init__(
        self,
        file_repo: FileRepository,
        version_repo: FileVersionRepository,
        settings: Settings,
    ) -> None:
        self._files = file_repo
        self._versions = version_repo
        self._settings = settings
        self._s3 = self._create_s3_client()

    def _create_s3_client(self):
        kwargs = {
            "aws_access_key_id": self._settings.s3_access_key_id,
            "aws_secret_access_key": self._settings.s3_secret_access_key,
            "region_name": self._settings.s3_region,
        }
        if self._settings.s3_endpoint_url:
            kwargs["endpoint_url"] = self._settings.s3_endpoint_url
        return boto3.client("s3", **kwargs)

    async def upload_file(
        self,
        file_content: bytes,
        original_filename: str,
        content_type: str,
        tenant_id: str | None = None,
        uploaded_by: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        module: str | None = None,
        is_public: bool = False,
    ) -> FileRecord:
        """Upload a file to S3/MinIO and record in DB."""
        # Validate file size
        size_bytes = len(file_content)
        max_bytes = self._settings.max_file_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            raise ValidationError(
                f"File size {size_bytes} exceeds maximum {self._settings.max_file_size_mb}MB"
            )

        # Validate MIME type
        if content_type not in self._settings.allowed_mime_types:
            raise ValidationError(f"File type '{content_type}' is not allowed")

        # Generate S3 key
        file_ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
        s3_key = f"{tenant_id or 'global'}/{entity_type or 'misc'}/{uuid.uuid4()}.{file_ext}"

        # Upload to S3
        self._s3.put_object(
            Bucket=self._settings.s3_bucket_name,
            Key=s3_key,
            Body=file_content,
            ContentType=content_type,
        )

        # Create DB record
        safe_filename = original_filename.replace("/", "_").replace("\\", "_")
        file = await self._files.create(
            filename=safe_filename,
            original_filename=original_filename,
            content_type=content_type,
            size_bytes=size_bytes,
            s3_key=s3_key,
            s3_bucket=self._settings.s3_bucket_name,
            tenant_id=tenant_id,
            uploaded_by=uploaded_by,
            entity_type=entity_type,
            entity_id=entity_id,
            module=module,
            is_public=is_public,
        )

        # Trigger async virus scan (in prod, send to queue)
        if not self._settings.enable_virus_scan:
            await self._files.update_virus_scan(file.id, "skipped")
        else:
            await self._scan_file(file.id, file_content)

        logger.info("file_uploaded", file_id=file.id, filename=original_filename, size=size_bytes)
        return file

    async def get_file(self, file_id: str) -> FileRecord:
        file = await self._files.get_by_id(file_id)
        if not file:
            raise NotFoundError("File", file_id)
        return file

    async def get_download_url(
        self, file_id: str, expires_in_seconds: int = 3600
    ) -> str:
        """Generate a presigned download URL."""
        file = await self.get_file(file_id)
        if file.virus_scan_status == "infected":
            raise ForbiddenError("File failed virus scan and cannot be downloaded")

        url = self._s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": file.s3_bucket, "Key": file.s3_key},
            ExpiresIn=expires_in_seconds,
        )
        return url

    async def list_files(
        self,
        tenant_id: str | None = None,
        entity_type: str | None = None,
        module: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[FileRecord], int]:
        return await self._files.list_all(
            tenant_id=tenant_id,
            entity_type=entity_type,
            module=module,
            offset=(page - 1) * page_size,
            limit=page_size,
        )

    async def get_entity_files(
        self, entity_type: str, entity_id: str, tenant_id: str | None = None
    ) -> list[FileRecord]:
        return await self._files.list_by_entity(entity_type, entity_id, tenant_id)

    async def delete_file(self, file_id: str) -> None:
        """Soft-delete a file record (does NOT delete from S3 for compliance)."""
        file = await self.get_file(file_id)
        await self._files.soft_delete(file_id)
        logger.info("file_deleted", file_id=file_id, filename=file.filename)

    async def upload_new_version(
        self,
        file_id: str,
        file_content: bytes,
        uploaded_by: str | None = None,
        comment: str | None = None,
    ) -> tuple[FileRecord, FileVersion]:
        """Upload a new version of an existing file."""
        file = await self.get_file(file_id)

        file_ext = file.filename.rsplit(".", 1)[-1] if "." in file.filename else ""
        new_s3_key = f"{file.tenant_id or 'global'}/{file.entity_type or 'misc'}/{uuid.uuid4()}.{file_ext}"

        self._s3.put_object(
            Bucket=file.s3_bucket,
            Key=new_s3_key,
            Body=file_content,
            ContentType=file.content_type,
        )

        new_version = await self._files.increment_version(file_id)
        version_record = await self._versions.create(
            file_id=file_id,
            version=new_version,
            s3_key=new_s3_key,
            size_bytes=len(file_content),
            uploaded_by=uploaded_by,
            comment=comment,
        )

        logger.info("file_version_added", file_id=file_id, version=new_version)
        updated_file = await self.get_file(file_id)
        return updated_file, version_record

    async def get_versions(self, file_id: str) -> list[FileVersion]:
        await self.get_file(file_id)
        return await self._versions.list_by_file(file_id)

    async def _scan_file(self, file_id: str, content: bytes) -> None:
        """Perform virus scan via ClamAV."""
        try:
            import clamd
            cd = clamd.ClamdNetworkSocket(
                host=self._settings.clamav_host,
                port=self._settings.clamav_port,
            )
            scan_result = cd.instream(io.BytesIO(content))
            status = scan_result.get("stream", ("OK", ""))[0]
            scan_status = "clean" if status == "OK" else "infected"
            await self._files.update_virus_scan(file_id, scan_status)
            logger.info("virus_scan_complete", file_id=file_id, status=scan_status)
        except Exception as exc:
            logger.warning("virus_scan_failed", file_id=file_id, error=str(exc))
            await self._files.update_virus_scan(file_id, "skipped")
