from fastapi import APIRouter
from .routes.analysis import router as analysis_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(analysis_router)
