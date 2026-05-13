import uuid
from datetime import datetime
from typing import Optional
from app.schemas.requests import CreateCertificateRequest
from app.schemas.responses import CertificateResponse, CertificateListResponse

# Module-level storage for certificates (persists across requests)
_certificates: dict[str, dict] = {}


class CertificateService:
    """In-memory certificate service for demo purposes."""
    
    def __init__(self):
        # Use module-level storage for persistence across requests
        pass
    
    def list_certificates(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        status: Optional[str] = None,
    ) -> CertificateListResponse:
        """List certificates with pagination and filtering."""
        all_certs = list(_certificates.values())
        
        # Apply search filter
        if search:
            search_lower = search.lower()
            all_certs = [
                c for c in all_certs
                if search_lower in c.get("title", "").lower()
                or search_lower in c.get("certificate_number", "").lower()
            ]
        
        # Apply status filter
        if status:
            all_certs = [c for c in all_certs if c.get("status") == status]
        
        # Sort by created date (newest first)
        all_certs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        total = len(all_certs)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated = all_certs[start_idx:end_idx]
        
        return CertificateListResponse(
            items=[CertificateResponse(**c) for c in paginated],
            total=total,
            page=page,
            page_size=page_size,
        )
    
    def create_certificate(self, data: CreateCertificateRequest) -> CertificateResponse:
        """Create a new certificate."""
        cert_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        certificate = {
            "id": cert_id,
            "certificate_number": data.certificate_number,
            "title": data.title,
            "customer_name": f"Customer-{data.customer_id[:8]}",  # Placeholder
            "certificate_type": data.certificate_type,
            "status": "draft",
            "issued_date": data.issue_date,
            "expiry_date": data.expiry_date,
            "issued_by": "system",  # Will be updated when issued
            "created_at": now,
            "updated_at": now,
        }
        
        _certificates[cert_id] = certificate
        return CertificateResponse(**certificate)
    
    def get_certificate(self, certificate_id: str) -> Optional[CertificateResponse]:
        """Get a certificate by ID."""
        cert = _certificates.get(certificate_id)
        if cert:
            return CertificateResponse(**cert)
        return None
    
    def issue_certificate(self, certificate_id: str) -> Optional[CertificateResponse]:
        """Issue a certificate (mark as issued)."""
        cert = _certificates.get(certificate_id)
        if not cert:
            return None
        
        cert["status"] = "issued"
        cert["issued_date"] = datetime.utcnow().isoformat()
        cert["issued_by"] = "system"  # Should be the current user
        cert["updated_at"] = datetime.utcnow().isoformat()
        
        return CertificateResponse(**cert)
