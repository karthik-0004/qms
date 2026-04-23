from fastapi import APIRouter
from .routes.plates import router as plates_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(plates_router)
