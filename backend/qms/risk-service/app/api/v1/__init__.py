from fastapi import APIRouter
from .routes.risks import router as risks_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(risks_router)
