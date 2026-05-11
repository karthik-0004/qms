from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.audit_proxy import router as audit_proxy_router
from .routes.crm_proxy import router as crm_proxy_router
from .routes.documents_proxy import router as documents_proxy_router
from .routes.gateway import router as gateway_router
from .routes.notifications_proxy import router as notifications_proxy_router
from .routes.tenants_proxy import router as tenants_proxy_router
from .routes.users_proxy import router as users_proxy_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(gateway_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(audit_proxy_router)
api_v1_router.include_router(documents_proxy_router)
api_v1_router.include_router(notifications_proxy_router)
api_v1_router.include_router(tenants_proxy_router)
api_v1_router.include_router(users_proxy_router)
api_v1_router.include_router(crm_proxy_router)
