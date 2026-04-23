from fastapi import APIRouter
from .routes.analytics import router as analytics_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(analytics_router)
