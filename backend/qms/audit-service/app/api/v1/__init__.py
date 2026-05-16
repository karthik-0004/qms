"""Audit Management Service — API v1 router."""

from fastapi import APIRouter
from .routes.audits import router as audits_router, checklists_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(audits_router)
api_v1_router.include_router(checklists_router)
