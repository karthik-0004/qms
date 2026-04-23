from fastapi import APIRouter
from .routes.equipment import router as equipment_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(equipment_router)
