from fastapi import APIRouter

from .routes.auth import router as auth_router
from .routes.audit_proxy import router as audit_proxy_router
from .routes.ccv_services_proxy import router as ccv_services_proxy_router
from .routes.crm_proxy import router as crm_proxy_router
from .routes.analytics_proxy import router as analytics_proxy_router
from .routes.capas_proxy import router as capas_proxy_router
from .routes.documents_proxy import router as documents_proxy_router
from .routes.equipment_proxy import router as equipment_proxy_router
from .routes.gateway import router as gateway_router
from .routes.quality_events_proxy import router as quality_events_proxy_router
from .routes.training_proxy import router as training_proxy_router
from .routes.notifications_proxy import router as notifications_proxy_router
from .routes.tenants_proxy import router as tenants_proxy_router
from .routes.users_proxy import router as users_proxy_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(gateway_router)
api_v1_router.include_router(auth_router)
api_v1_router.include_router(audit_proxy_router)
api_v1_router.include_router(documents_proxy_router)
api_v1_router.include_router(quality_events_proxy_router)
api_v1_router.include_router(capas_proxy_router)
api_v1_router.include_router(training_proxy_router)
api_v1_router.include_router(equipment_proxy_router)
api_v1_router.include_router(analytics_proxy_router)
api_v1_router.include_router(notifications_proxy_router)
api_v1_router.include_router(tenants_proxy_router)
api_v1_router.include_router(users_proxy_router)
api_v1_router.include_router(crm_proxy_router)
api_v1_router.include_router(ccv_services_proxy_router)
