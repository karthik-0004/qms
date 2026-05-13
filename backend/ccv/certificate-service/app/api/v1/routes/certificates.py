from fastapi import APIRouter, Depends, Query
from typing import Annotated
import structlog
from app.schemas.requests import CreateCertificateRequest
from app.schemas.responses import CertificateResponse, CertificateListResponse
from app.domain.service import CertificateService

logger = structlog.get_logger()

router = APIRouter(prefix="/certificates", tags=["Certificates"])

def get_certificate_service():
    return CertificateService()

@router.get("", response_model=CertificateListResponse)
async def list_certificates(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    service: Annotated[CertificateService, Depends(get_certificate_service)] = None,
):
    """List all certificates with pagination and filtering."""
    result = service.list_certificates(
        page=page,
        page_size=page_size,
        search=search,
        status=status,
    )
    return result


@router.post("", response_model=CertificateResponse)
async def create_certificate(
    data: CreateCertificateRequest,
    service: Annotated[CertificateService, Depends(get_certificate_service)] = None,
):
    """Create a new certificate."""
    certificate = service.create_certificate(data)
    logger.info("certificate.created", certificate_id=certificate.id)
    return certificate


@router.get("/{certificate_id}", response_model=CertificateResponse)
async def get_certificate(
    certificate_id: str,
    service: Annotated[CertificateService, Depends(get_certificate_service)] = None,
):
    """Get a certificate by ID."""
    certificate = service.get_certificate(certificate_id)
    if not certificate:
        raise LookupError(f"Certificate with ID {certificate_id} not found")
    return certificate


@router.post("/{certificate_id}/issue", response_model=CertificateResponse)
async def issue_certificate(
    certificate_id: str,
    service: Annotated[CertificateService, Depends(get_certificate_service)] = None,
):
    """Issue a certificate (mark as issued)."""
    certificate = service.issue_certificate(certificate_id)
    if not certificate:
        raise LookupError(f"Certificate with ID {certificate_id} not found")
    logger.info("certificate.issued", certificate_id=certificate_id)
    return certificate
