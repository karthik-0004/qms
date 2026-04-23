from fastapi import APIRouter
from .routes.files import router as files_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(files_router)
