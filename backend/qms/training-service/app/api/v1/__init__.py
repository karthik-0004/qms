from fastapi import APIRouter
from .routes.training import router as training_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(training_router)
