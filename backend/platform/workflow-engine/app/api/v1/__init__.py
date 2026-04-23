from fastapi import APIRouter
from .routes.workflows import router as workflows_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(workflows_router)
