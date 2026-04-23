from fastapi import APIRouter
from .routes.reports import router as reports_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(reports_router)
