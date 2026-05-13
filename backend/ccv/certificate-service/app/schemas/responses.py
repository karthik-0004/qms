from pydantic import BaseModel
from datetime import datetime


class CertificateResponse(BaseModel):
    id: str
    certificate_number: str
    title: str
    customer_name: str
    certificate_type: str
    status: str
    issued_date: str | None = None
    expiry_date: str | None = None
    issued_by: str
    
    class Config:
        from_attributes = True


class CertificateListResponse(BaseModel):
    items: list[CertificateResponse]
    total: int
    page: int
    page_size: int
