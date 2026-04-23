from fastapi import APIRouter
from .routes.audit import router as audit_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(audit_router)
