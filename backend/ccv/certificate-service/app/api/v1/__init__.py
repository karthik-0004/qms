from fastapi import APIRouter
from .routes.certificates import router as certificates_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(certificates_router, prefix="/certificates")
