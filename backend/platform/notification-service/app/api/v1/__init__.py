from fastapi import APIRouter
from .routes.notifications import router as notifications_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(notifications_router)
