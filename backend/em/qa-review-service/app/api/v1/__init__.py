from fastapi import APIRouter
from .routes.reviews import router as reviews_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(reviews_router)
