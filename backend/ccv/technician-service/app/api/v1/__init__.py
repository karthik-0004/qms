from fastapi import APIRouter
from .routes.technicians import router as technicians_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(technicians_router)
