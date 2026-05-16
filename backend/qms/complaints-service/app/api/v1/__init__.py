from fastapi import APIRouter
from .routes.complaints import router as complaints_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(complaints_router)
