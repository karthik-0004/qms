"""Image Service — Pydantic request schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class RegisterImageRequest(BaseModel):
    plate_id: str
    image_key: str = Field(min_length=1)
    image_type: str = Field(min_length=1)
    captured_at: datetime
    file_size_bytes: int = 0
    width_px: int | None = None
    height_px: int | None = None
    resolution_dpi: int | None = None
    magnification: float | None = None
    camera_settings: dict = {}
    is_primary: bool = False
