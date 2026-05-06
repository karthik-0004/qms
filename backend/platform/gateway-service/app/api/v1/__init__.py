from fastapi import APIRouter
from .routes.gateway import router as gateway_router
<<<<<<< HEAD
from .routes.documents_proxy import router as documents_proxy_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(gateway_router)
api_v1_router.include_router(documents_proxy_router)
=======
from .routes.auth import router as auth_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(gateway_router)
api_v1_router.include_router(auth_router)
>>>>>>> ffc221eed48483e4fa7c1e09407208b63779887e
