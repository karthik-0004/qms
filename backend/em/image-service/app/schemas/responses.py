"""Image Service — Pydantic response schemas."""

from datetime import datetime
from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: str
    tenant_id: str
    plate_id: str
    image_key: str
    image_type: str
    captured_at: datetime
    uploaded_by: str
    file_size_bytes: int
    width_px: int | None
    height_px: int | None
    resolution_dpi: int | None
    magnification: float | None
    camera_settings: dict
    is_primary: bool
    status: str
    created_at: datetime
    updated_at: datetime
