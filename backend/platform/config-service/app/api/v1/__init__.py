from fastapi import APIRouter
from .routes.config import router as config_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(config_router)
