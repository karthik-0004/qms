from fastapi import APIRouter
from .routes.management_reviews import router as management_reviews_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(management_reviews_router)
