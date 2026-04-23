from fastapi import APIRouter
from .routes.tenants import router as tenants_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(tenants_router)

__all__ = ["api_v1_router"]
