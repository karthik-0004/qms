from pydantic import BaseModel, Field


class CreateCertificateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    certificate_number: str = Field(..., min_length=1)
    certificate_type: str = Field(..., min_length=1)
    customer_id: str = Field(..., min_length=1)
    issue_date: str = Field(..., min_length=1)
    expiry_date: str | None = None
    description: str | None = None
