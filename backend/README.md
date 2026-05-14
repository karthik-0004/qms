## Backend Overview

This folder contains **all backend code** for the Rainer platform and its domain modules.
It is organized as a **multi-service FastAPI** monorepo with shared Python libraries.

### What lives in `backend/`

- **`platform/`**: “core platform” services (auth, tenants, users, gateway, config, etc.)
- **`qms/`**: QMS domain services (documents, quality events, CAPA, training, equipment)
- **`em/`**: EndGameBiotech EM domain services (plates, images, AI, jobs, QA review)
- **`ccv/`**: CCV domain services (CRM, contracts, work orders, technicians, billing)
- **`shared/`**: shared Python libraries (imported by services)
- **`scripts/`**: one-off scripts for local/dev bootstrapping

### Backend architecture (service-internal)

Each service follows the same internal layout and separation of concerns:

- **`app/api/v1/`**: FastAPI route registration and versioned routes
- **`app/schemas/`**: Pydantic request/response schemas
- **`app/core/`**: settings, DB wiring, security helpers, validation utilities
- **`app/domain/`**: business logic (services / use-cases)
- **`app/infra/`**: adapters (DB repositories, HTTP clients, queues, storage)
- **`tests/`**: unit/integration/e2e tests for that service

You can see this pattern clearly in a platform service like `tenant-service`:

```1:6:backend/platform/tenant-service/app/api/v1/__init__.py
from fastapi import APIRouter
from .routes.tenants import router as tenants_router

api_v1_router = APIRouter(prefix="/api/v1")
api_v1_router.include_router(tenants_router)
```

and in its route module:

```20:33:backend/platform/tenant-service/app/api/v1/routes/tenants.py
router = APIRouter(prefix="/tenants", tags=["Tenants"])

def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> TenantDomainService:
    return TenantDomainService(
        tenant_repo=TenantRepository(db),
        settings_repo=TenantSettingsRepository(db),
        settings=settings,
    )
```

### Cross-cutting standards (shared)

Shared platform behavior comes from libraries in `backend/shared/`, most importantly:

- **`rainer_common/`**: standard middleware, logging, health endpoints, response envelopes
- **`rainer_auth_lib/`**: JWT + service-to-service auth utilities used across services
- **`rainer_tenant_lib/`**: tenant-related shared logic (where applicable)

Example: `rainer_common` provides consistent health endpoints:

```19:44:backend/shared/rainer_common/rainer_common/health.py
def create_health_router(
    service_name: str,
    service_version: str = "0.1.0",
    readiness_checks: dict[str, Callable[[], Coroutine[Any, Any, bool]]] | None = None,
) -> APIRouter:
    """
    Factory that creates /health/live and /health/ready endpoints.
```

and a consistent response envelope used across services:

```40:52:backend/shared/rainer_common/rainer_common/responses.py
class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: ResponseMeta = Field(default_factory=ResponseMeta)
```

### Services and domains

#### Platform services (`backend/platform/`)

These services power core platform concerns and are typically required by all domains:

- **`auth-service`**: authentication, JWT issuance, refresh tokens, MFA, access keys
- **`tenant-service`**: tenant provisioning and lifecycle
- **`user-service`**: user management
- **`gateway-service`**: gateway/proxy to consolidate public-facing API calls
- **`config-service`**: platform config
- **`audit-service`**: audit log ingestion/query
- **`notification-service`**: email/notification delivery
- **`workflow-engine`**: workflow execution/orchestration
- **`file-service`**: object/file storage integration (MinIO/S3-compatible)
- **`schedule-service`**: scheduling jobs/logic
- **`reporting-service`**: reporting exports
- **`analytics-service`**: analytics endpoints

#### QMS services (`backend/qms/`)

- **`document-service`**: documents
- **`quality-event-service`**: quality events
- **`capa-service`**: CAPA workflows
- **`training-service`**: training tracking
- **`equipment-service`**: equipment lifecycle

#### EM services (`backend/em/`)

- **`plate-service`**, **`image-service`**, **`ai-service`**, **`job-service`**, **`qa-review-service`**

#### CCV services (`backend/ccv/`)

- **`crm-service`**, **`contract-service`**, **`workorder-service`**, **`technician-service`**, **`billing-service`**

### Configuration and environment variables

Each service ships its own `.env.example` under its directory, e.g.:

- `backend/platform/auth-service/.env.example`
- `backend/qms/document-service/.env.example`

**Do not hardcode secrets**; use `.env` files or Docker Compose environment overrides.

### Local development

Services are split into separate Docker Compose files — each domain shows as its own group in Docker Desktop.

| File | `name:` | Docker Desktop group | Services |
|---|---|---|---|
| `docker-compose.infra.yml` | `infra` | **infra** | PostgreSQL, Redis, Kafka, MinIO, Vault |
| `docker-compose.platform.yml` | `platform` | **platform** | Auth, Tenant, User, Audit, Notification, Config, Workflow, File, Gateway, Schedule, Reporting, Analytics |
| `docker-compose.qms.yml` | `qms` | **qms** | Documents, Quality Events, CAPA, Training, Equipment |
| `docker-compose.em.yml` | `em` | **em** | Plate, Image, AI, Jobs, QA Review |
| `docker-compose.ccv.yml` | `ccv` | **ccv** | CRM, Contracts, Work Orders, Technicians, Billing, Certificates |

All domain files connect to a shared `rainer-net` network created by `docker-compose.infra.yml`.

#### Start (from repo root)

```bash
# Using scripts (recommended)
./backend/scripts/dev.sh platform          # infra + platform
./backend/scripts/dev.sh qms               # infra + qms
./backend/scripts/dev.sh em                # infra + em
./backend/scripts/dev.sh ccv               # infra + ccv
./backend/scripts/dev.sh all               # all domains

# Or directly with docker compose:
docker compose -f docker-compose.infra.yml up -d
docker compose -f docker-compose.platform.yml up -d
docker compose -f docker-compose.qms.yml up -d
docker compose -f docker-compose.em.yml up -d
docker compose -f docker-compose.ccv.yml up -d
```

#### Stop

```bash
docker compose -f docker-compose.qms.yml down
docker compose -f docker-compose.platform.yml down
docker compose -f docker-compose.infra.yml down
```

#### Check status

```bash
docker compose -f docker-compose.infra.yml ps
docker compose -f docker-compose.platform.yml ps
docker compose -f docker-compose.qms.yml ps
```

#### View logs

```bash
docker compose -f docker-compose.platform.yml logs -f auth-service
docker compose -f docker-compose.qms.yml logs -f document-service
```

### Common ports (local)

| Service | Port |
|---|---|
| **Gateway** | `8000` |
| **Auth** | `8001` |
| **Tenant** | `8002` |
| **User** | `8003` |
| **Audit** | `8004` |
| **Notifications** | `8005` |
| **Config** | `8006` |
| **Workflow engine** | `8007` |
| **Schedule** | `8008` |
| **File service** | `8009` |
| **Reporting** | `8010` |
| **Analytics** | `8011` |
| **Documents** | `8020` |
| **Quality Events** | `8021` |
| **CAPA** | `8022` |
| **Training** | `8023` |
| **Equipment** | `8024` |
| **PostgreSQL** | `5435` (host) |
| **Redis** | `6379` |
| **Kafka** | `9092` |
| **MinIO** | `9000` (API), `9001` (Console) |
| **Vault** | `8200` |

### Testing

Each service contains its own `tests/` directory (unit/integration/e2e where applicable).
Typical usage patterns:

- **Unit tests**: `tests/unit/*`
- **Integration tests**: `tests/integration/*` (where present)
- **End-to-end vertical slice tests**: `tests/e2e/*` (where present)

### Common troubleshooting

- **500 with generic message**: services intentionally return a safe error envelope.
  Check the relevant service logs (`docker compose logs -f <service>`), using `request_id` if present.
- **Service unhealthy**: verify dependencies are up (DB/Redis/Kafka/MinIO) and check `/health/live` and `/health/ready`.

