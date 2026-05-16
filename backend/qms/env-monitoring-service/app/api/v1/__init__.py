from fastapi import APIRouter
from .routes.monitoring_points import router as monitoring_points_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(monitoring_points_router)
