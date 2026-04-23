from fastapi import APIRouter
from .routes.contracts import router as contracts_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(contracts_router)
