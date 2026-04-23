from fastapi import APIRouter
from .routes import router as scim_router

scim_v2_router = APIRouter(prefix="/scim/v2")
scim_v2_router.include_router(scim_router)
