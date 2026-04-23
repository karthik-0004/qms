from fastapi import APIRouter
from .routes.jobs import router as jobs_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(jobs_router)
