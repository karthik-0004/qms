from fastapi import APIRouter
from .routes.invoices import router as invoices_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(invoices_router)
