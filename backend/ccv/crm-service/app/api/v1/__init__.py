from fastapi import APIRouter
from .routes.customers import router as customers_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(customers_router)
