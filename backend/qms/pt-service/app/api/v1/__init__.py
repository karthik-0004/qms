from fastapi import APIRouter
from .routes.pt import router as pt_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(pt_router)
