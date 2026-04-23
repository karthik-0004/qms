from fastapi import APIRouter
from .routes.quality_events import router as quality_events_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(quality_events_router)
