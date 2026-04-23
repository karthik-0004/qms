from fastapi import APIRouter
from .routes.capas import router as capas_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(capas_router)
