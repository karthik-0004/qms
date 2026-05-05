from fastapi import APIRouter
from .routes.gateway import router as gateway_router
from .routes.auth import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(gateway_router)
api_v1_router.include_router(auth_router)
