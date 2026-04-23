from fastapi import APIRouter
from .routes.users import router as users_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(users_router)
