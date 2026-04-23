from fastapi import APIRouter
from .routes.workorders import router as workorders_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(workorders_router)
