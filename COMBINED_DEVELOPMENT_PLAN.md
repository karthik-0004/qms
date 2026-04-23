# Rainer Platform — Enterprise Development Plan v2.0

> **Status**: Active  |  **Last Updated**: 2026-03-05  |  **Author**: AI-Assisted Engineering

---

## Table of Contents

1. [Analysis of Original Roadmap — Gaps & Improvements](#1-analysis-of-original-roadmap)
2. [Confirmed Tech Stack](#2-confirmed-tech-stack)
3. [Enhanced System Architecture (HLD)](#3-enhanced-system-architecture)
4. [Enhanced Data Architecture](#4-enhanced-data-architecture)
5. [Complete Service Catalog with LLD](#5-complete-service-catalog)
6. [Testing Strategy (Enterprise Grade)](#6-testing-strategy)
7. [Infrastructure & DevOps (K8s + CI/CD)](#7-infrastructure--devops)
8. [Security Architecture](#8-security-architecture)
9. [Frontend Architecture (Next.js)](#9-frontend-architecture)
10. [API Standards & Conventions](#10-api-standards--conventions)
11. [Event Architecture (Kafka)](#11-event-architecture)
12. [Observability Strategy](#12-observability-strategy)
13. [Phase Implementation Plan (Status Tracking)](#13-phase-implementation-plan)
14. [Development Rules & Standards](#14-development-rules--standards)

---

## 1. Analysis of Original Roadmap

### 1.1 Strengths of Original Plan

- Solid multi-product structure with shared platform substrate
- DB-per-tenant with derived credentials is the right enterprise pattern
- Clear product boundaries (QMS, EM, CCV)
- Phase-based approach (A → E) is well structured
- Correct event-driven architecture intent (Kafka/RabbitMQ)
- Right observability intention (logging, metrics, traces)

### 1.2 Critical Gaps Identified

| Gap | Severity | Fix |
|-----|----------|-----|
| No specific tech stack versions / packages listed | CRITICAL | See Section 2 |
| Testing strategy completely absent (unit, contract, integration, E2E) | CRITICAL | See Section 6 |
| Frontend architecture entirely missing | CRITICAL | See Section 9 |
| No structured logging / correlation IDs standard | HIGH | See Section 12 |
| No Grafana/Prometheus/Loki/Jaeger setup details | HIGH | See Section 12 |
| No K8s manifests / Helm chart strategy | HIGH | See Section 7 |
| No docker-compose local dev setup | HIGH | See Section 7 |
| No CI/CD pipeline definition | HIGH | See Section 7 |
| No API versioning strategy | HIGH | See Section 10 |
| No error response format standard | HIGH | See Section 10 |
| No secrets management (Vault/AWS SSM) | HIGH | See Section 8 |
| No health check / readiness / liveness standards | MEDIUM | See Section 7 |
| No rate limiting implementation details | MEDIUM | See Section 5 |
| No dead letter queue (DLQ) handling | MEDIUM | See Section 11 |
| No schema registry for Kafka | MEDIUM | See Section 11 |
| No WebSocket/SSE for real-time features | MEDIUM | See Section 5 |
| No Pact contract testing plan | MEDIUM | See Section 6 |
| No TestContainers setup | MEDIUM | See Section 6 |
| No PgBouncer/connection pooling details | MEDIUM | See Section 4 |
| No OpenTelemetry integration | MEDIUM | See Section 12 |
| No feature flags service (LaunchDarkly/Flagsmith) | LOW | See Section 5 |
| No canary deployment strategy | LOW | See Section 7 |
| No backup / disaster recovery plan | LOW | See Section 7 |
| No gRPC for high-throughput internal calls | LOW | See Section 10 |

### 1.3 Mismatches in Original Plan

1. **Phase C & D sprint overlap**: Both say "Sprints 17–30" (parallel case) but the plan isn't explicit enough about resource allocation per parallel track.
2. **`schedule-service` dual role**: Listed as Platform service AND used in Phase D CCV — clarified: it IS a platform service that CCV domain uses.
3. **`user-service` vs `user-admin-service`**: Section 2.2 mentions both but only `user-service` appears in Phase A todo. Resolution: `user-admin-service` is a sub-module of `user-service` (admin endpoints).
4. **`audit-domain-service` for QMS**: Listed as a domain service ON TOP of `audit-service` — clarified as a QMS-specific wrapper with domain-level audit queries, NOT a separate service but a module within QMS.
5. **`gateway-service` tech**: Original says "FastAPI/NestJS" — confirmed as **Python FastAPI** for all backend services.
6. **Infrastructure setup time missing**: No sprint allocation for K8s cluster, CI/CD, observability bootstrap.

### 1.4 Architecture Improvements

1. **Add OpenTelemetry** as unified observability instrumentation across all services
2. **Add PgBouncer** between services and PostgreSQL for connection pooling
3. **Add Kafka Schema Registry** (Confluent) for event payload governance
4. **Add Flagsmith** or simple DB-backed feature flags in `config-service`
5. **Add Redis Sentinel / Cluster** for HA Redis
6. **Add MinIO** as local-dev S3-compatible storage
7. **Add Jaeger** for distributed tracing
8. **Add Alertmanager** for alert routing
9. **Service Mesh (Istio) — Phase E**: Add mTLS between services in later phases
10. **gRPC** for latency-sensitive internal calls (auth token validation, tenant resolution)

---

## 2. Confirmed Tech Stack

### 2.1 Backend

| Layer | Technology | Version / Package |
|-------|-----------|-------------------|
| Framework | Python FastAPI | `fastapi==0.115.x` |
| ASGI Server | Uvicorn + Gunicorn | `uvicorn[standard]==0.30.x` |
| ORM | SQLAlchemy 2.0 (async) | `sqlalchemy==2.0.x` |
| Migrations | Alembic | `alembic==1.13.x` |
| Validation | Pydantic v2 | `pydantic==2.8.x` |
| DB Driver | asyncpg | `asyncpg==0.29.x` |
| Connection Pool | PgBouncer (sidecar) + SQLAlchemy pool | pgbouncer:1.22 |
| Caching | Redis (via aioredis) | `redis==5.0.x` |
| Message Bus | Apache Kafka | `aiokafka==0.11.x` |
| Schema Registry | Confluent Schema Registry | `confluent-kafka==2.5.x` |
| Auth / JWT | PyJWT + passlib | `python-jose==3.3.x`, `passlib[bcrypt]==1.7.x` |
| MFA / TOTP | pyotp | `pyotp==2.9.x` |
| Background Tasks | Celery + Redis broker | `celery==5.4.x` |
| HTTP Client | httpx | `httpx==0.27.x` |
| Observability | OpenTelemetry | `opentelemetry-sdk==1.27.x` |
| Logging | structlog | `structlog==24.4.x` |
| gRPC (internal) | grpcio | `grpcio==1.67.x` |
| File Storage | boto3 (S3/MinIO) | `boto3==1.35.x` |
| PDF Generation | WeasyPrint / ReportLab | `weasyprint==62.x` |
| Virus Scan | ClamAV (via clamd) | `clamd==1.0.x` |
| Rate Limiting | slowapi | `slowapi==0.1.9` |
| API Docs | Swagger UI / ReDoc | Built into FastAPI |
| Testing | pytest + pytest-asyncio | `pytest==8.x`, `pytest-asyncio==0.24.x` |
| Test Containers | testcontainers-python | `testcontainers==4.8.x` |
| Contract Testing | pact-python | `pact-python==2.2.x` |
| Coverage | pytest-cov | `pytest-cov==5.x` |
| Linting | ruff + mypy | `ruff==0.6.x`, `mypy==1.11.x` |
| Secrets | HashiCorp Vault | `hvac==2.3.x` |
| Task Scheduler | APScheduler | `apscheduler==3.10.x` |
| AI/ML | PyTorch + Transformers (ai-service) | `torch==2.4.x` |

### 2.2 Frontend

| Layer | Technology | Version / Package |
|-------|-----------|-------------------|
| Framework | Next.js (App Router) | `next==15.x` |
| UI Components | shadcn/ui | latest |
| Styling | Tailwind CSS | `tailwindcss==3.4.x` |
| Animations | Framer Motion + Magic UI | `framer-motion==11.x` |
| State Management | Zustand | `zustand==5.x` |
| Server State | TanStack Query (React Query) | `@tanstack/react-query==5.x` |
| Data Fetching | SWR | `swr==2.x` |
| Auth | NextAuth.js v5 | `next-auth==5.x` |
| Validation | Zod | `zod==3.23.x` |
| Forms | React Hook Form + Zod resolver | `react-hook-form==7.x` |
| Icons | Lucide React | `lucide-react==0.x` |
| Charts | Recharts + Tremor | `recharts==2.x` |
| Tables | TanStack Table | `@tanstack/react-table==8.x` |
| Real-time | Socket.io-client / SSE | `socket.io-client==4.x` |
| API Types | openapi-typescript | `openapi-typescript==7.x` |
| HTTP Client | Axios + Interceptors | `axios==1.7.x` |
| Testing | Vitest + Testing Library + Playwright | `vitest==2.x`, `@playwright/test==1.x` |
| Linting | ESLint + Prettier | `eslint==9.x` |
| Bundler | Turbopack (Next.js built-in) | — |

### 2.3 Infrastructure

| Component | Technology | Notes |
|-----------|-----------|-------|
| Container Orchestration | Kubernetes 1.30+ | EKS/GKE/self-managed |
| Package Manager | Helm 3.x | All K8s resources via Helm charts |
| Local K8s | k3d / minikube | Dev environment |
| Container Registry | Docker Hub / ECR | CI/CD pushes |
| CI/CD | GitHub Actions | All pipelines |
| Local Dev | docker-compose | Full stack local |
| API Gateway (K8s) | Kong Ingress Controller | Rate limiting, auth plugins |
| Service Mesh (Phase E) | Istio | mTLS, traffic management |
| Secrets | HashiCorp Vault | Dynamic secrets |
| Object Storage | MinIO (dev) / S3 (prod) | |
| Search | OpenSearch 2.x | Full-text + log aggregation |
| Metrics | Prometheus + Grafana | `kube-prometheus-stack` |
| Logs | Grafana Loki + Promtail | Log aggregation |
| Tracing | Jaeger / Grafana Tempo | Distributed tracing |
| Alerting | Alertmanager | Integrated with Grafana |
| DB Connection Pool | PgBouncer 1.22 | Per-service sidecar |
| Cache | Redis 7.x | Sentinel for HA |
| Message Bus | Apache Kafka 3.7 | KRaft mode (no ZooKeeper) |
| Schema Registry | Confluent Schema Registry | Kafka payload governance |

---

## 3. Enhanced System Architecture (HLD)

### 3.1 Full System Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          CLIENT TIER                                 │
│  Browser (Next.js SSR/SSG)  |  Mobile App  |  3rd Party Integrations│
└─────────────────────┬───────────────────────────────────────────────┘
                      │ HTTPS/WSS
┌─────────────────────▼───────────────────────────────────────────────┐
│                    EDGE / INGRESS TIER                               │
│  Kong Ingress Controller (K8s)                                       │
│  - TLS termination, CORS, WAF rules, DDoS protection                 │
│  - Rate limiting (per IP, per tenant, per API key)                   │
│  - JWT validation plugin, tenant header injection                    │
└─────────────────────┬───────────────────────────────────────────────┘
                      │ Internal HTTP/gRPC
┌─────────────────────▼───────────────────────────────────────────────┐
│                  PLATFORM SERVICES TIER                              │
│  ┌──────────────┐ ┌───────────────┐ ┌──────────────┐ ┌───────────┐ │
│  │ auth-service │ │tenant-service │ │ user-service │ │  gateway  │ │
│  │ (JWT, MFA,   │ │(provisioning, │ │  (RBAC,roles │ │ (routing, │ │
│  │  access keys)│ │ resolver,     │ │   profiles)  │ │  policies)│ │
│  └──────────────┘ │ migrations)   │ └──────────────┘ └───────────┘ │
│  ┌──────────────┐ └───────────────┘ ┌──────────────┐ ┌───────────┐ │
│  │audit-service │                   │notification- │ │  config-  │ │
│  │(immutable    │                   │   service    │ │  service  │ │
│  │ trail)       │                   │(email,SMS,   │ │(flags,    │ │
│  └──────────────┘                   │  webhooks)   │ │ settings) │ │
│  ┌──────────────┐ ┌───────────────┐ └──────────────┘ └───────────┘ │
│  │ workflow-    │ │schedule-      │ ┌──────────────┐ ┌───────────┐ │
│  │   engine     │ │  service      │ │ file-service │ │reporting- │ │
│  │(state machine│ │(recurrence,   │ │(S3,versioning│ │  service  │ │
│  │ approvals)   │ │ dispatching)  │ │  virus scan) │ │(PDF,CSV)  │ │
│  └──────────────┘ └───────────────┘ └──────────────┘ └───────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              analytics-service (dashboards, KPIs, BI)        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────────┐
│                  DOMAIN SERVICES TIER                                │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────────────┐   │
│  │  QMS DOMAIN    │ │   EM DOMAIN    │ │     CCV DOMAIN         │   │
│  │ document-svc   │ │  plate-svc     │ │  crm-svc               │   │
│  │ quality-event  │ │  image-svc     │ │  contract-svc          │   │
│  │ capa-svc       │ │  ai-svc        │ │  asset-svc             │   │
│  │ training-svc   │ │  job-svc       │ │  schedule-domain-svc   │   │
│  │ equipment-svc  │ │  qa-review-svc │ │  workorder-svc         │   │
│  │ supplier-svc   │ │                │ │  technician-svc        │   │
│  │ risk-svc       │ │                │ │  certificate-svc       │   │
│  │ complaint-svc  │ │                │ │  billing-svc           │   │
│  │ mgmt-review    │ │                │ │  portal-svc            │   │
│  └────────────────┘ └────────────────┘ └────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────────────┐
│                      DATA TIER                                       │
│  ┌────────────────┐ ┌──────────────┐ ┌─────────┐ ┌──────────────┐  │
│  │  PostgreSQL    │ │    Redis 7   │ │  Kafka  │ │ MinIO / S3   │  │
│  │  Master DB +   │ │  (cache,     │ │  (async │ │ (files,      │  │
│  │  Tenant DBs    │ │  sessions,   │ │ events, │ │  reports,    │  │
│  │  (PgBouncer)   │ │  rate limit) │ │  DLQ)   │ │  certs)      │  │
│  └────────────────┘ └──────────────┘ └─────────┘ └──────────────┘  │
│  ┌────────────────┐ ┌──────────────────────────────────────────┐    │
│  │  OpenSearch    │ │  Observability: Prometheus + Grafana +    │    │
│  │  (search,      │ │  Loki + Jaeger + Alertmanager            │    │
│  │   log agg)     │ │                                          │    │
│  └────────────────┘ └──────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

### 3.2 K8s Namespace Strategy

```
rainer-infra        # PostgreSQL, Redis, Kafka, MinIO, OpenSearch
rainer-platform     # auth, tenant, user, gateway, audit, notification,
                    # config, workflow, schedule, file, reporting, analytics
rainer-qms          # QMS domain services
rainer-em           # EM domain services
rainer-ccv          # CCV domain services
rainer-monitoring   # Prometheus, Grafana, Loki, Jaeger, Alertmanager
rainer-frontend     # Next.js app deployment
```

### 3.3 Internal Communication Patterns

| Pattern | Use Case | Protocol |
|---------|----------|----------|
| Sync request/response | User-facing API calls | REST over HTTP/2 |
| High-throughput internal | Token validation, tenant resolution | gRPC |
| Async messaging | Domain events, notifications | Kafka topics |
| Real-time push | Notifications, status updates | WebSocket (Socket.IO) / SSE |
| Bulk operations | Report generation, AI batch | Kafka + Celery workers |

---

## 4. Enhanced Data Architecture

### 4.1 Master DB Schema (Complete)

```sql
-- Master DB: rainer_master

-- Tenant registry
CREATE TABLE tenants (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_name     VARCHAR(100) NOT NULL UNIQUE,
    slug            VARCHAR(100) NOT NULL UNIQUE,        -- URL-safe identifier
    db_name         VARCHAR(100) NOT NULL UNIQUE,
    db_user         VARCHAR(100) NOT NULL UNIQUE,
    db_host         VARCHAR(255) NOT NULL DEFAULT 'postgres',
    db_port         INTEGER NOT NULL DEFAULT 5432,
    status          VARCHAR(20) NOT NULL DEFAULT 'provisioning'
                    CHECK (status IN ('provisioning','active','suspended','deleted')),
    tier            VARCHAR(20) NOT NULL DEFAULT 'starter'
                    CHECK (tier IN ('starter','professional','enterprise')),
    products        JSONB NOT NULL DEFAULT '[]',         -- ['qms','em','ccv']
    region          VARCHAR(50) NOT NULL DEFAULT 'us-east-1',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- Platform users (login identities — cross-tenant admins + tenant users)
CREATE TABLE platform_users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email           VARCHAR(255) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    tenant_id       UUID REFERENCES tenants(id) ON DELETE SET NULL,
    role            VARCHAR(50) NOT NULL DEFAULT 'tenant_user'
                    CHECK (role IN ('super_admin','tenant_admin','tenant_user')),
    status          VARCHAR(20) NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','inactive','locked','pending_verification')),
    mfa_secret      VARCHAR(255),                        -- encrypted TOTP secret
    mfa_enabled     BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at   TIMESTAMPTZ,
    failed_attempts INTEGER NOT NULL DEFAULT 0,
    locked_until    TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at      TIMESTAMPTZ
);

-- Tenant settings / plan config
CREATE TABLE tenant_settings (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID NOT NULL UNIQUE REFERENCES tenants(id) ON DELETE CASCADE,
    max_users       INTEGER NOT NULL DEFAULT 50,
    max_storage_gb  INTEGER NOT NULL DEFAULT 10,
    features        JSONB NOT NULL DEFAULT '{}',         -- feature flags per tenant
    branding        JSONB NOT NULL DEFAULT '{}',         -- logo, colors, domain
    smtp_config     JSONB,                               -- per-tenant email config
    webhook_urls    JSONB NOT NULL DEFAULT '[]',
    timezone        VARCHAR(100) NOT NULL DEFAULT 'UTC',
    locale          VARCHAR(20) NOT NULL DEFAULT 'en-US',
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Service access keys (for service-to-service auth)
CREATE TABLE service_access_keys (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name    VARCHAR(100) NOT NULL,
    key_hash        VARCHAR(255) NOT NULL UNIQUE,        -- SHA-256 of actual key
    key_prefix      VARCHAR(20) NOT NULL,                -- first 8 chars for lookup
    scopes          JSONB NOT NULL DEFAULT '[]',
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_used_at    TIMESTAMPTZ,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    rotated_at      TIMESTAMPTZ
);

-- Platform-level audit log
CREATE TABLE platform_audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id       UUID REFERENCES tenants(id),
    user_id         UUID REFERENCES platform_users(id),
    action          VARCHAR(100) NOT NULL,
    resource_type   VARCHAR(100),
    resource_id     UUID,
    ip_address      INET,
    user_agent      TEXT,
    metadata        JSONB NOT NULL DEFAULT '{}',
    severity        VARCHAR(20) NOT NULL DEFAULT 'info'
                    CHECK (severity IN ('info','warning','critical')),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Refresh tokens
CREATE TABLE refresh_tokens (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES platform_users(id) ON DELETE CASCADE,
    token_hash      VARCHAR(255) NOT NULL UNIQUE,
    device_info     JSONB,
    ip_address      INET,
    expires_at      TIMESTAMPTZ NOT NULL,
    revoked_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Migration tracking
CREATE TABLE migrations_history (
    id              SERIAL PRIMARY KEY,
    migration_name  VARCHAR(255) NOT NULL UNIQUE,
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    checksum        VARCHAR(64) NOT NULL
);

-- Indexes
CREATE INDEX idx_platform_users_email ON platform_users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_platform_users_tenant ON platform_users(tenant_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tenants_slug ON tenants(slug) WHERE deleted_at IS NULL;
CREATE INDEX idx_platform_audit_logs_tenant ON platform_audit_logs(tenant_id, created_at DESC);
CREATE INDEX idx_platform_audit_logs_user ON platform_audit_logs(user_id, created_at DESC);
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id) WHERE revoked_at IS NULL;
CREATE INDEX idx_service_access_keys_prefix ON service_access_keys(key_prefix) WHERE is_active = TRUE;
```

### 4.2 Tenant DB Schema (Base — Applied on Tenant Creation)

```sql
-- Every tenant DB gets this base schema

-- Users within tenant (mirrors platform_users but tenant-scoped profile data)
CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    platform_user_id UUID NOT NULL UNIQUE,               -- links to master platform_users
    tenant_id       UUID NOT NULL,
    first_name      VARCHAR(100) NOT NULL,
    last_name       VARCHAR(100) NOT NULL,
    display_name    VARCHAR(200),
    phone           VARCHAR(50),
    department      VARCHAR(100),
    job_title       VARCHAR(100),
    avatar_url      TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Roles
CREATE TABLE roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    permissions     JSONB NOT NULL DEFAULT '[]',
    is_system_role  BOOLEAN NOT NULL DEFAULT FALSE,
    product         VARCHAR(20),                         -- 'qms','em','ccv',NULL=all
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- User-role assignments
CREATE TABLE user_roles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id         UUID NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_by      UUID REFERENCES users(id),
    granted_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ,
    UNIQUE (user_id, role_id)
);

-- Tenant-level audit log
CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id),
    action          VARCHAR(150) NOT NULL,
    resource_type   VARCHAR(100) NOT NULL,
    resource_id     UUID,
    old_value       JSONB,
    new_value       JSONB,
    ip_address      INET,
    user_agent      TEXT,
    session_id      UUID,
    product         VARCHAR(20),
    module          VARCHAR(100),
    signature       VARCHAR(255),                        -- e-signature hash
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
) PARTITION BY RANGE (created_at);

-- Notifications
CREATE TABLE notifications (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID REFERENCES users(id) ON DELETE CASCADE,
    type            VARCHAR(100) NOT NULL,
    title           VARCHAR(255) NOT NULL,
    body            TEXT NOT NULL,
    data            JSONB NOT NULL DEFAULT '{}',
    channel         VARCHAR(50) NOT NULL DEFAULT 'in_app'
                    CHECK (channel IN ('in_app','email','sms','push','webhook')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','sent','delivered','failed','read')),
    sent_at         TIMESTAMPTZ,
    read_at         TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Schema migrations tracking per tenant
CREATE TABLE schema_migrations (
    id              SERIAL PRIMARY KEY,
    version         VARCHAR(100) NOT NULL UNIQUE,
    name            VARCHAR(255) NOT NULL,
    applied_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_users_platform_user ON users(platform_user_id);
CREATE INDEX idx_user_roles_user ON user_roles(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id, created_at DESC);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id, created_at DESC);
CREATE INDEX idx_notifications_user ON notifications(user_id, status, created_at DESC);
```

### 4.3 Connection Management Architecture

```
Services → PgBouncer (transaction mode) → PostgreSQL
                                          ├── rainer_master (Master DB)
                                          ├── tenant_xxxx_db (Tenant DBs)
                                          └── Read Replicas (analytics queries)

PgBouncer Config:
- Transaction pooling mode (best for FastAPI async)
- Max pool size per DB: 20 connections
- Max client connections: 200
- Connection timeout: 5s
- Idle timeout: 600s

Redis Architecture:
- Redis Sentinel (1 primary + 2 replicas)
- Keyspace namespacing: rainer:{service}:{key}
- TTLs: JWT blacklist=1h, tenant cache=5min, rate limit=1min
```

### 4.4 Tenant Resolver Library Design

```python
# rainer-tenant-lib (shared Python package)
# Path: backend/shared/rainer_tenant_lib/

class TenantResolver:
    """
    Resolves tenant DB credentials from tenant_id.
    Uses HMAC-SHA256 to derive DB password (never stored).
    Maintains per-tenant connection pools with lifecycle management.
    """
    async def resolve(self, tenant_id: str) -> TenantConfig
    async def get_session(self, tenant_id: str) -> AsyncSession
    async def derive_password(self, tenant_id: str) -> str  # HMAC(MASTER_SECRET, tenant_id)
    async def get_pool_stats(self) -> dict[str, PoolStats]
```

---

## 5. Complete Service Catalog

### 5.1 Platform Services (Phase A)

#### auth-service
- **Port**: 8001
- **Responsibility**: Authentication, token issuance, MFA, access keys
- **DB**: Master DB (platform_users, refresh_tokens, service_access_keys)
- **Endpoints**:
  - `POST /api/v1/auth/login` — email+password → access+refresh JWT
  - `POST /api/v1/auth/refresh` — rotate refresh token
  - `POST /api/v1/auth/logout` — revoke refresh token
  - `POST /api/v1/auth/mfa/setup` — generate TOTP QR
  - `POST /api/v1/auth/mfa/verify` — verify TOTP code
  - `POST /api/v1/auth/mfa/disable` — disable MFA
  - `POST /api/v1/auth/access-keys` — create service access key
  - `DELETE /api/v1/auth/access-keys/{id}` — revoke key
  - `POST /api/v1/auth/validate` — validate JWT (internal gRPC)
  - `POST /api/v1/auth/forgot-password` — send reset email
  - `POST /api/v1/auth/reset-password` — complete reset
- **Events Published**: `auth.user.logged_in`, `auth.user.mfa_enabled`, `auth.token.refreshed`
- **JWT Payload**: `{ sub, email, tenant_id, role, product_access[], iat, exp, jti }`

#### tenant-service
- **Port**: 8002
- **Responsibility**: Tenant lifecycle, DB provisioning, resolver, migrations
- **DB**: Master DB (tenants, tenant_settings)
- **Endpoints**:
  - `POST /api/v1/tenants` — create tenant + provision DB (super_admin)
  - `GET /api/v1/tenants` — list all tenants (super_admin)
  - `GET /api/v1/tenants/{id}` — get tenant details
  - `PATCH /api/v1/tenants/{id}` — update tenant
  - `DELETE /api/v1/tenants/{id}` — soft-delete tenant
  - `POST /api/v1/tenants/{id}/suspend` — suspend tenant
  - `POST /api/v1/tenants/{id}/activate` — reactivate
  - `GET /api/v1/tenants/{id}/settings` — get settings
  - `PATCH /api/v1/tenants/{id}/settings` — update settings
  - `POST /api/v1/tenants/{id}/migrate` — run pending migrations
  - `GET /api/v1/tenants/{id}/migration-status` — check migration health
  - `GET /api/v1/resolver/{tenant_id}` — resolve tenant config (internal)
- **Events Published**: `tenant.created`, `tenant.suspended`, `tenant.deleted`, `tenant.migrated`

#### user-service
- **Port**: 8003
- **Responsibility**: User profiles, RBAC, role assignments
- **DB**: Tenant DB (users, roles, user_roles)
- **Endpoints**:
  - `GET /api/v1/users` — list users (paginated, filtered)
  - `GET /api/v1/users/{id}` — user details
  - `POST /api/v1/users` — invite user (creates platform_user + tenant user)
  - `PATCH /api/v1/users/{id}` — update profile
  - `DELETE /api/v1/users/{id}` — deactivate user
  - `GET /api/v1/roles` — list roles
  - `POST /api/v1/roles` — create custom role
  - `PATCH /api/v1/roles/{id}` — update role permissions
  - `POST /api/v1/users/{id}/roles` — assign role
  - `DELETE /api/v1/users/{id}/roles/{role_id}` — remove role
  - `GET /api/v1/users/{id}/permissions` — resolved permission set
- **Events Published**: `user.created`, `user.role_assigned`, `user.deactivated`

#### gateway-service
- **Port**: 8000 (main entry point)
- **Responsibility**: Routing, tenant context injection, coarse auth, observability hooks
- **Note**: Kong handles L7 routing in K8s; this FastAPI service handles custom business routing logic
- **Middleware Stack** (in order):
  1. Request ID injection (X-Request-ID)
  2. Structured logging
  3. OpenTelemetry tracing span creation
  4. JWT validation (delegates to auth-service via gRPC)
  5. Tenant context extraction + injection (X-Tenant-ID header)
  6. RBAC coarse check
  7. Rate limiting (per IP + per tenant)
  8. Audit log emission
  9. Response compression

#### audit-service
- **Port**: 8004
- **Responsibility**: Immutable audit trail (append-only), compliance logs
- **DB**: Master DB (platform events) + Tenant DB (domain events)
- **Key Design**: Write-only via events; queries read-only with filter/export
- **Endpoints**:
  - `GET /api/v1/audit/logs` — query audit logs (filtered, paginated)
  - `GET /api/v1/audit/logs/{id}` — single log entry
  - `GET /api/v1/audit/export` — export CSV/PDF report
  - `POST /api/v1/audit/logs` — internal: append log entry
  - `GET /api/v1/audit/signatures/{id}` — verify e-signature hash
- **Events Consumed**: ALL domain events from all services
- **Immutability Enforcement**: No UPDATE/DELETE allowed; partition-level WORM

#### notification-service
- **Port**: 8005
- **Responsibility**: Multi-channel notifications (email, SMS, push, webhooks)
- **DB**: Tenant DB (notifications table)
- **Channels**: Email (SendGrid/SES), SMS (Twilio), Push (FCM), Webhook
- **Endpoints**:
  - `GET /api/v1/notifications` — user's notifications
  - `PATCH /api/v1/notifications/{id}/read` — mark read
  - `POST /api/v1/notifications/read-all` — mark all read
  - `GET /api/v1/notifications/preferences` — user preferences
  - `PATCH /api/v1/notifications/preferences` — update prefs
  - `POST /api/v1/notifications/templates` — create template (admin)
  - `GET /api/v1/notifications/templates` — list templates
  - `POST /api/v1/notifications/send` — internal: send notification
- **WebSocket**: `/ws/notifications/{user_id}` — real-time push

#### config-service
- **Port**: 8006
- **Responsibility**: Platform-wide config, feature flags, enums, facility hierarchy
- **DB**: Master DB + Tenant DB (per-tenant overrides)
- **Endpoints**:
  - `GET /api/v1/config/enums/{type}` — get enum values
  - `GET /api/v1/config/features` — feature flags for tenant
  - `PATCH /api/v1/config/features/{flag}` — toggle feature (admin)
  - `GET /api/v1/config/facility` — facility hierarchy
  - `POST /api/v1/config/facility` — add location/facility node
  - `GET /api/v1/config/regulatory-frameworks` — applicable standards
  - `GET /api/v1/config/media-types` — EM media types config

#### workflow-engine
- **Port**: 8007
- **Responsibility**: Generic state machine for approvals and flows
- **DB**: Tenant DB (workflow_definitions, workflow_instances, workflow_steps, workflow_history)
- **Schema**:

```sql
CREATE TABLE workflow_definitions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            VARCHAR(100) NOT NULL,
    version         INTEGER NOT NULL DEFAULT 1,
    entity_type     VARCHAR(100) NOT NULL,               -- 'document','capa','workorder'
    states          JSONB NOT NULL,                      -- state machine definition
    transitions     JSONB NOT NULL,                      -- allowed transitions + guards
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE workflow_instances (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    definition_id   UUID NOT NULL REFERENCES workflow_definitions(id),
    entity_type     VARCHAR(100) NOT NULL,
    entity_id       UUID NOT NULL,
    current_state   VARCHAR(100) NOT NULL,
    context         JSONB NOT NULL DEFAULT '{}',
    assignee_id     UUID,
    due_at          TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    created_by      UUID NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE workflow_history (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    instance_id     UUID NOT NULL REFERENCES workflow_instances(id),
    from_state      VARCHAR(100),
    to_state        VARCHAR(100) NOT NULL,
    action          VARCHAR(100) NOT NULL,
    actor_id        UUID NOT NULL,
    comment         TEXT,
    signature       VARCHAR(255),
    metadata        JSONB NOT NULL DEFAULT '{}',
    occurred_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

- **Endpoints**:
  - `POST /api/v1/workflows/definitions` — define new workflow
  - `GET /api/v1/workflows/definitions` — list definitions
  - `POST /api/v1/workflows/instances` — start workflow instance
  - `GET /api/v1/workflows/instances/{id}` — get instance + history
  - `POST /api/v1/workflows/instances/{id}/transition` — trigger state transition
  - `GET /api/v1/workflows/instances` — list instances (filtered by entity/state)
  - `GET /api/v1/workflows/instances/my-tasks` — pending tasks for current user

#### schedule-service
- **Port**: 8008
- **Responsibility**: Generic recurrence rules, schedule management, dispatch events
- **DB**: Tenant DB (schedules, schedule_events)
- **Endpoints**:
  - `POST /api/v1/schedules` — create schedule with recurrence rule
  - `GET /api/v1/schedules` — list schedules
  - `PATCH /api/v1/schedules/{id}` — update schedule
  - `DELETE /api/v1/schedules/{id}` — delete schedule
  - `GET /api/v1/schedules/{id}/events` — upcoming events for schedule
  - `POST /api/v1/schedules/{id}/acknowledge` — acknowledge event

#### file-service
- **Port**: 8009
- **Responsibility**: File upload/download, versioning, access control, virus scanning
- **Storage**: MinIO (dev) / S3 (prod)
- **Endpoints**:
  - `POST /api/v1/files/upload` — upload file (multipart) → presigned store
  - `GET /api/v1/files/{id}` — get file metadata
  - `GET /api/v1/files/{id}/download` — download / presigned URL
  - `GET /api/v1/files/{id}/versions` — file version history
  - `POST /api/v1/files/{id}/versions` — upload new version
  - `DELETE /api/v1/files/{id}` — soft delete
  - `GET /api/v1/files` — list files (by entity/module/type)
- **Virus Scan**: ClamAV sidecar, async scan on upload

#### reporting-service
- **Port**: 8010
- **Responsibility**: Report template management, data binding, PDF/CSV generation
- **DB**: Tenant DB (report_templates, report_jobs, report_outputs)
- **Endpoints**:
  - `POST /api/v1/reports/generate` — trigger report generation (async)
  - `GET /api/v1/reports/jobs/{id}` — check generation status
  - `GET /api/v1/reports/outputs/{id}` — download generated report
  - `GET /api/v1/reports/templates` — list templates
  - `POST /api/v1/reports/templates` — create template
  - `POST /api/v1/reports/scheduled` — schedule recurring report

#### analytics-service
- **Port**: 8011
- **Responsibility**: Cross-module KPIs, dashboards, time-series queries
- **DB**: Tenant DB (read replica) + Optional ClickHouse
- **Endpoints**:
  - `GET /api/v1/analytics/dashboards` — list available dashboards
  - `GET /api/v1/analytics/dashboards/{id}` — get dashboard config + data
  - `GET /api/v1/analytics/kpis` — KPI metrics (product-specific)
  - `GET /api/v1/analytics/time-series` — time-series data
  - `GET /api/v1/analytics/trends` — trend analysis
  - `POST /api/v1/analytics/query` — ad-hoc query (admin only)

---

## 6. Testing Strategy (Enterprise Grade)

### 6.1 Testing Pyramid

```
         E2E Tests (Playwright)
        ━━━━━━━━━━━━━━━━━━━━━━━━
       Integration Tests (TestContainers)
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
     Contract Tests (Pact — Consumer/Provider)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Unit Tests (pytest, fast, isolated, mocked)
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 6.2 Unit Tests

- **Framework**: pytest + pytest-asyncio
- **Coverage target**: ≥ 80% per service
- **Scope**: Domain logic, utilities, validators, transformers
- **Pattern**: AAA (Arrange, Act, Assert) with fixtures
- **Mocking**: `unittest.mock`, `pytest-mock` for external deps
- **Fast**: < 5 seconds total per service unit test suite
- **Location**: `tests/unit/`

### 6.3 Integration Tests (TestContainers)

- **Framework**: testcontainers-python
- **Purpose**: Test service + real database / Redis / Kafka
- **Pattern**: Each test spins up real containers, runs against them, tears down
- **Containers used per service**:
  - PostgreSQL 16 container
  - Redis 7 container
  - Kafka container (where events are used)
  - MinIO container (file-service)
- **Location**: `tests/integration/`
- **Key test cases per service**:
  - Happy path CRUD flows
  - Error conditions (conflict, not found, validation failure)
  - Pagination, filtering
  - Event publishing verification

```python
# Example: TestContainers integration test pattern
@pytest.fixture(scope="session")
async def pg_container():
    with PostgresContainer("postgres:16") as postgres:
        yield postgres.get_connection_url()

async def test_create_tenant_provisions_db(pg_container, auth_client):
    response = await auth_client.post("/api/v1/tenants", json={...})
    assert response.status_code == 201
    assert await db_exists(response.json()["db_name"])
```

### 6.4 Contract Tests (Pact)

- **Framework**: pact-python (v2 — HTTP contract testing)
- **Pattern**: Consumer-Driven Contract Testing
- **Consumer**: Frontend / downstream service
- **Provider**: Upstream service (auth-service, user-service, etc.)
- **Pact Broker**: Self-hosted Pact Broker (Docker) or PactFlow
- **Flow**:
  1. Consumer writes interaction expectation (pact file)
  2. Provider verifies pact file against real implementation
  3. Pact broker tracks which versions are compatible
- **Coverage**: All service-to-service and frontend-to-backend interactions
- **Location**: `tests/contract/`

### 6.5 End-to-End Tests

- **Backend E2E**: httpx test client against running FastAPI app + real DBs
- **Frontend E2E**: Playwright against Next.js dev server
- **Vertical slice per service/module** (mandatory before marking done):
  - Auth: login → get profile → refresh → logout
  - Tenant: create tenant → provision DB → create user → login as tenant user
  - Workflow: define workflow → start instance → transition states → complete
  - Document (QMS): create → submit for review → approve → publish
- **Location**: `tests/e2e/`

### 6.6 Test Execution

```bash
# Per service
make test-unit        # fast, no containers
make test-integration # TestContainers (requires Docker)
make test-contract    # Pact consumer/provider
make test-e2e         # full E2E
make test-all         # all above

# CI Pipeline runs all suites
```

### 6.7 CI Quality Gates

| Gate | Threshold |
|------|-----------|
| Unit test coverage | ≥ 80% |
| All unit tests pass | 100% |
| All integration tests pass | 100% |
| All contract tests pass | 100% |
| E2E happy path tests pass | 100% |
| No ruff linting errors | 0 errors |
| No mypy type errors | 0 errors |

---

## 7. Infrastructure & DevOps

### 7.1 Repository Structure

```
Portal/
├── backend/
│   ├── shared/
│   │   ├── rainer_auth_lib/        # JWT, access key verification
│   │   ├── rainer_audit_lib/       # Audit emission decorators
│   │   ├── rainer_tenant_lib/      # Tenant resolver, connection pools
│   │   ├── rainer_config_lib/      # Feature flags, settings
│   │   ├── rainer_workflow_lib/    # Workflow helpers
│   │   └── rainer_common/          # Shared models, utils, middleware
│   ├── platform/
│   │   ├── auth-service/
│   │   ├── tenant-service/
│   │   ├── user-service/
│   │   ├── gateway-service/
│   │   ├── audit-service/
│   │   ├── notification-service/
│   │   ├── config-service/
│   │   ├── workflow-engine/
│   │   ├── schedule-service/
│   │   ├── file-service/
│   │   ├── reporting-service/
│   │   └── analytics-service/
│   ├── qms/
│   │   ├── document-service/
│   │   ├── quality-event-service/
│   │   ├── capa-service/
│   │   ├── training-service/
│   │   ├── equipment-service/
│   │   ├── supplier-service/
│   │   ├── risk-service/
│   │   └── complaint-service/
│   ├── em/
│   │   ├── plate-service/
│   │   ├── image-service/
│   │   ├── ai-service/
│   │   ├── job-service/
│   │   └── qa-review-service/
│   └── ccv/
│       ├── crm-service/
│       ├── contract-service/
│       ├── asset-service/
│       ├── schedule-domain-service/
│       ├── workorder-service/
│       ├── technician-service/
│       ├── certificate-service/
│       ├── billing-service/
│       └── portal-service/
├── frontend/
│   ├── apps/
│   │   └── web/                    # Main Next.js application
│   └── packages/
│       ├── ui/                     # Shared component library
│       └── types/                  # Generated API types
├── infra/
│   ├── k8s/
│   │   ├── namespaces/
│   │   ├── platform/
│   │   ├── qms/
│   │   ├── em/
│   │   ├── ccv/
│   │   ├── infra/
│   │   └── monitoring/
│   ├── helm/
│   │   └── rainer-service/         # Generic Helm chart for all services
│   └── terraform/
│       ├── aws/
│       └── gcp/
├── docker-compose.yml              # Local full-stack dev
├── docker-compose.test.yml         # Integration test environment
├── .github/
│   └── workflows/
│       ├── ci.yml                  # PR CI
│       ├── cd-staging.yml          # Deploy to staging
│       └── cd-prod.yml             # Deploy to prod
└── Makefile                        # Top-level convenience commands
```

### 7.2 Service Folder Structure (Standard Template)

```
{service-name}/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   ├── __init__.py
│   │       │   └── {resource}.py
│   │       ├── dependencies.py     # FastAPI Depends()
│   │       └── __init__.py
│   ├── core/
│   │   ├── config.py               # Pydantic Settings
│   │   ├── security.py             # Auth helpers
│   │   ├── logging.py              # structlog setup
│   │   ├── middleware.py           # Request ID, tracing, audit
│   │   └── exceptions.py           # Custom exception handlers
│   ├── domain/
│   │   ├── entities/               # Pure Python domain models
│   │   ├── value_objects/          # Immutable value types
│   │   ├── services/               # Business logic
│   │   └── events/                 # Domain event definitions
│   ├── infra/
│   │   ├── db/
│   │   │   ├── models/             # SQLAlchemy ORM models
│   │   │   ├── repositories/       # Data access layer
│   │   │   └── session.py          # Async session factory
│   │   ├── cache/                  # Redis operations
│   │   ├── messaging/              # Kafka producer/consumer
│   │   ├── storage/                # S3/MinIO client
│   │   └── external/               # External API clients
│   ├── schemas/
│   │   ├── requests/               # Pydantic request models
│   │   └── responses/              # Pydantic response models
│   └── main.py                     # FastAPI app factory
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
├── tests/
│   ├── conftest.py
│   ├── unit/
│   ├── integration/
│   ├── contract/
│   └── e2e/
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── configmap.yaml
├── Dockerfile
├── docker-compose.test.yml
├── pyproject.toml
├── alembic.ini
├── .env.example
└── README.md
```

### 7.3 docker-compose.yml (Local Dev)

```yaml
# Full local dev stack
services:
  postgres:     postgres:16           # ports: 5432
  redis:        redis:7-alpine        # ports: 6379
  kafka:        confluentinc/cp-kafka # ports: 9092
  schema-reg:   confluentinc/cp-schema-registry
  minio:        minio/minio           # ports: 9000, 9001 (console)
  opensearch:   opensearchproject/opensearch:2
  mailhog:      mailhog/mailhog       # Local SMTP trap
  vault:        hashicorp/vault       # Dev mode

  # Platform services
  auth-service:         build: ./backend/platform/auth-service
  tenant-service:       build: ./backend/platform/tenant-service
  user-service:         build: ./backend/platform/user-service
  gateway-service:      build: ./backend/platform/gateway-service
  # ... etc

  # Frontend
  web:                  build: ./frontend/apps/web
```

### 7.4 Kubernetes Manifests Standard

Each service gets:
- **Deployment**: 2 replicas minimum, rolling update strategy, resource limits
- **Service**: ClusterIP (internal), LoadBalancer via Kong Ingress
- **HPA**: Scale 2–10 pods based on CPU (70%) + custom metrics
- **PDB**: minAvailable: 1 (ensure at least 1 pod during disruptions)
- **ConfigMap**: Non-secret configuration
- **ExternalSecret**: Vault-backed secrets via External Secrets Operator

```yaml
# Resource limits (standard)
resources:
  requests:
    cpu: "100m"
    memory: "256Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"

# Probes (standard)
livenessProbe:
  httpGet: { path: /health/live, port: 8000 }
  initialDelaySeconds: 15
readinessProbe:
  httpGet: { path: /health/ready, port: 8000 }
  initialDelaySeconds: 5
```

### 7.5 CI/CD Pipeline (GitHub Actions)

```yaml
# .github/workflows/ci.yml
on: [pull_request]

jobs:
  lint:         ruff check + mypy
  unit-tests:   pytest tests/unit/ --cov=app --cov-fail-under=80
  build:        docker build
  integration:  pytest tests/integration/ (with service containers)
  contract:     pact verify
  security:     bandit + safety check
  e2e:          pytest tests/e2e/ (against docker-compose stack)
```

---

## 8. Security Architecture

### 8.1 Authentication & Authorization Layers

```
Layer 1 (Kong):    TLS termination, IP allowlist, WAF rules, DDoS
Layer 2 (Gateway): JWT validation, tenant context extraction, coarse RBAC
Layer 3 (Service): Fine-grained RBAC via rainer-auth-lib permission check
Layer 4 (DB):      Row-level: tenant_id filter on all queries (tenant isolation)
```

### 8.2 JWT Design

```json
{
  "sub": "user-uuid",
  "email": "user@tenant.com",
  "tenant_id": "tenant-uuid",
  "role": "tenant_admin",
  "permissions": ["document:read", "document:write", "capa:approve"],
  "product_access": ["qms", "ccv"],
  "jti": "unique-token-id",
  "iat": 1741100000,
  "exp": 1741100900,
  "type": "access"
}
```

- Access token TTL: **15 minutes**
- Refresh token TTL: **7 days** (sliding)
- Blacklist: Redis key `rainer:auth:blacklist:{jti}` TTL=15min

### 8.3 Secrets Management

```
HashiCorp Vault (dev: dev mode, prod: HA cluster)
├── secret/rainer/master_secret     # HMAC key for tenant DB password derivation
├── secret/rainer/jwt_private_key   # RS256 private key
├── secret/rainer/services/{svc}/db_password
├── secret/rainer/services/kafka_credentials
└── secret/rainer/integrations/sendgrid_api_key

K8s: External Secrets Operator → Vault → K8s Secrets (auto-sync)
```

### 8.4 OWASP Controls

| Control | Implementation |
|---------|----------------|
| SQL Injection | SQLAlchemy parameterized queries only |
| XSS | CSP headers via Next.js middleware |
| CSRF | SameSite cookies + CSRF token for mutations |
| Auth bypass | JWT validation on every request, no backdoors |
| Broken access | Per-request tenant isolation checks |
| Security misconfig | Automated config scanning in CI |
| Rate limiting | Kong + slowapi (per IP + per tenant) |
| Sensitive data exposure | No PII in logs, encrypted secrets |

---

## 9. Frontend Architecture (Next.js)

### 9.1 App Structure

```
frontend/apps/web/
├── app/
│   ├── (auth)/                     # No layout wrapping (standalone pages)
│   │   ├── login/page.tsx
│   │   ├── register/page.tsx
│   │   └── mfa/page.tsx
│   ├── (platform)/                 # Authenticated shell
│   │   ├── layout.tsx              # Main layout (sidebar, header, notifications)
│   │   ├── dashboard/page.tsx      # Product selector dashboard
│   │   └── settings/
│   │       ├── profile/page.tsx
│   │       ├── users/page.tsx
│   │       └── billing/page.tsx
│   ├── (qms)/                      # RainerQMS product shell
│   │   ├── layout.tsx
│   │   ├── documents/
│   │   │   ├── page.tsx            # Document list (SSR)
│   │   │   ├── [id]/page.tsx       # Document detail
│   │   │   └── new/page.tsx
│   │   ├── quality-events/
│   │   ├── capa/
│   │   ├── training/
│   │   ├── equipment/
│   │   ├── audits/
│   │   └── analytics/
│   ├── (em)/                       # EndGameBiotech product shell
│   │   ├── layout.tsx
│   │   ├── plates/
│   │   ├── jobs/
│   │   └── analytics/
│   ├── (ccv)/                      # RainerCCV product shell
│   │   ├── layout.tsx
│   │   ├── crm/
│   │   ├── contracts/
│   │   ├── assets/
│   │   ├── workorders/
│   │   ├── certificates/
│   │   └── billing/
│   ├── api/
│   │   └── auth/[...nextauth]/route.ts
│   ├── layout.tsx
│   └── page.tsx                    # Landing / redirect
├── components/
│   ├── ui/                         # shadcn/ui exports
│   ├── common/                     # Shared business components
│   │   ├── DataTable/
│   │   ├── StatusBadge/
│   │   ├── WorkflowTimeline/
│   │   ├── FileUpload/
│   │   ├── NotificationPanel/
│   │   └── AuditTrail/
│   ├── platform/                   # Platform-level UI
│   │   ├── Sidebar/
│   │   ├── Header/
│   │   ├── TenantSwitcher/
│   │   └── GlobalSearch/
│   ├── qms/                        # QMS-specific components
│   ├── em/                         # EM-specific components
│   └── ccv/                        # CCV-specific components
├── lib/
│   ├── api/
│   │   ├── client.ts               # Axios instance with interceptors
│   │   ├── auth.ts                 # Auth API calls
│   │   ├── tenants.ts
│   │   └── ...                     # Per-service API modules
│   ├── auth/
│   │   └── config.ts               # NextAuth.js config
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useTenant.ts
│   │   ├── usePermissions.ts
│   │   └── useWebSocket.ts
│   ├── stores/
│   │   ├── auth.store.ts           # Zustand: auth state
│   │   ├── tenant.store.ts         # Zustand: tenant context
│   │   ├── notification.store.ts   # Zustand: notifications
│   │   └── ui.store.ts             # Zustand: UI state (sidebar, theme)
│   ├── validations/
│   │   ├── auth.schema.ts          # Zod schemas
│   │   └── ...
│   └── utils/
│       ├── format.ts
│       ├── permissions.ts
│       └── date.ts
├── types/
│   ├── api.ts                      # Generated from OpenAPI
│   └── app.ts                      # App-specific types
├── middleware.ts                   # NextAuth + tenant routing
├── next.config.ts
├── tailwind.config.ts
└── package.json
```

### 9.2 Rendering Strategy

| Route | Strategy | Reason |
|-------|----------|--------|
| Auth pages | CSR | No sensitive server state |
| Dashboard | SSR | Personalized, role-specific |
| Document list | SSR + ISR | Semi-static, cacheable |
| Document detail | SSR | Dynamic, permission-gated |
| Analytics | SSR + Streaming | Heavy data, parts load incrementally |
| Settings | SSR | User-specific |
| Real-time notifications | Client (WebSocket) | Live push |

### 9.3 State Management Strategy

```typescript
// Zustand: Client-only ephemeral/UI state
authStore:         { user, tenant, permissions, isLoading }
uiStore:           { sidebarOpen, theme, activeProduct }
notificationStore: { notifications[], unreadCount, wsConnected }

// TanStack Query: Server state with cache
useQuery():        All GET requests (with stale-time, cache-time)
useMutation():     All POST/PUT/PATCH/DELETE (optimistic updates)

// SWR: Simple server state for frequently-polled data
useWorkflowStatus():  Poll workflow instance status
useJobStatus():       Poll AI job status
```

### 9.4 Permission-Gated UI Pattern

```typescript
// Every sensitive component uses permission check
<PermissionGate permission="capa:approve">
  <ApproveButton onClick={handleApprove} />
</PermissionGate>

// usePermissions hook resolves from Zustand + JWT payload
const { can } = usePermissions()
if (!can('document:write')) redirect('/unauthorized')
```

---

## 10. API Standards & Conventions

### 10.1 URL Conventions

```
GET    /api/v1/{resource}              — list (paginated)
POST   /api/v1/{resource}              — create
GET    /api/v1/{resource}/{id}         — get single
PATCH  /api/v1/{resource}/{id}         — partial update
DELETE /api/v1/{resource}/{id}         — soft delete
POST   /api/v1/{resource}/{id}/{action} — state transition / action

Examples:
POST /api/v1/documents/{id}/submit-for-review
POST /api/v1/workorders/{id}/complete
GET  /api/v1/documents?page=1&page_size=20&status=draft&sort=-created_at
```

### 10.2 Standard Response Envelope

```json
// Success (list)
{
  "success": true,
  "data": [...],
  "pagination": {
    "page": 1, "page_size": 20, "total": 150, "total_pages": 8
  },
  "meta": { "request_id": "uuid", "timestamp": "ISO8601" }
}

// Success (single)
{
  "success": true,
  "data": { ... },
  "meta": { "request_id": "uuid", "timestamp": "ISO8601" }
}

// Error
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [{ "field": "email", "message": "Invalid email format" }]
  },
  "meta": { "request_id": "uuid", "timestamp": "ISO8601" }
}
```

### 10.3 Standard HTTP Status Codes

| Scenario | Code |
|----------|------|
| Created | 201 |
| No content (delete) | 204 |
| Validation error | 422 |
| Unauthorized | 401 |
| Forbidden | 403 |
| Not found | 404 |
| Conflict (duplicate) | 409 |
| Too many requests | 429 |
| Server error | 500 |

### 10.4 Pagination

```
GET /api/v1/documents?page=1&page_size=20&sort=-created_at&status=draft
```

### 10.5 Standard Health Endpoints

Every service MUST implement:
```
GET /health/live   — liveness: { status: "ok" }
GET /health/ready  — readiness: checks DB, Redis, Kafka connectivity
GET /metrics       — Prometheus metrics endpoint
```

---

## 11. Event Architecture (Kafka)

### 11.1 Topic Naming Convention

```
{domain}.{entity}.{action}

Examples:
auth.user.logged_in
auth.token.refreshed
tenant.tenant.created
tenant.tenant.suspended
user.user.invited
user.role.assigned
document.document.created
document.document.approved
capa.capa.opened
workflow.instance.transitioned
notification.email.sent
report.report.generated
```

### 11.2 Event Envelope (Standard)

```json
{
  "event_id": "uuid",
  "event_type": "document.document.approved",
  "version": "1.0",
  "tenant_id": "uuid",
  "actor_id": "uuid",
  "occurred_at": "2026-03-05T10:00:00Z",
  "correlation_id": "uuid",
  "payload": { ... }
}
```

### 11.3 Dead Letter Queue (DLQ)

- Each topic has a corresponding DLQ: `{topic}.dlq`
- Failed messages after 3 retries → DLQ
- DLQ consumer: alerts + manual re-processing UI
- Retention: 7 days on main topics, 30 days on DLQ

### 11.4 Schema Registry

- All event schemas registered in Confluent Schema Registry
- Avro or JSON Schema (JSON Schema chosen for simplicity)
- Schema evolution rules: backward-compatible changes only (additive)

---

## 12. Observability Strategy

### 12.1 Three Pillars

#### Metrics (Prometheus + Grafana)
- **kube-prometheus-stack** deployed in `rainer-monitoring` namespace
- Per-service metrics exposed at `/metrics`:
  - HTTP request duration histogram
  - HTTP request count (by status, endpoint)
  - DB query duration
  - Kafka consumer lag
  - Cache hit/miss ratio
  - Active connections
- **Grafana Dashboards**:
  - Platform Overview (golden signals: latency, traffic, errors, saturation)
  - Per-service drilldown
  - DB performance
  - Kafka consumer lag
  - Business KPIs per product

#### Logs (Grafana Loki + Promtail)
- **Format**: JSON structured logs via structlog
- **Fields**: timestamp, level, service, version, trace_id, span_id, request_id, tenant_id, user_id, action, duration_ms, status_code
- **Log levels**: DEBUG (dev), INFO (prod default), WARNING, ERROR, CRITICAL
- **No PII in logs** (email, passwords, tokens masked)
- Logs shipped via Promtail → Loki → Grafana

#### Traces (Jaeger + OpenTelemetry)
- **OpenTelemetry SDK** in every FastAPI service
- Auto-instrumentation: FastAPI, SQLAlchemy, Redis, Kafka, httpx
- Traces collected by Jaeger (or Grafana Tempo)
- Correlation: `trace_id` + `span_id` included in all log lines
- Sampling: 100% dev, 10% prod (adjustable)

### 12.2 Alerting Rules (Alertmanager)

| Alert | Condition | Severity |
|-------|-----------|----------|
| ServiceDown | No healthy pods for 2m | CRITICAL |
| HighErrorRate | HTTP 5xx > 1% for 5m | CRITICAL |
| HighLatency | P95 > 1s for 10m | WARNING |
| DBConnectionsHigh | > 80% pool used | WARNING |
| KafkaConsumerLag | > 1000 msgs for 5m | WARNING |
| DiskSpaceLow | < 10% free | WARNING |
| MemoryHigh | > 85% for 10m | WARNING |

---

## 13. Phase Implementation Plan

### Status Legend: ⬜ Pending | 🔵 In Progress | ✅ Done | ❌ Blocked

---

### Phase A — Rainer Platform (Sprint 1–12)

#### Sprint 1–2: Foundation & Tooling
- ✅ Backend project structure scaffolding
- ✅ Shared Python libraries skeleton (`rainer_common`, `rainer_tenant_lib`, `rainer_auth_lib`)
- ✅ docker-compose.yml (full local dev stack)
- ✅ GitHub Actions CI pipeline template
- ✅ Pre-commit hooks (ruff, mypy, conventional commits)
- ✅ K8s namespace manifests + base Helm chart
- ✅ Master DB Alembic migration setup
- ✅ Service template (cookiecutter-style reference)
- ✅ Frontend Next.js project bootstrapped with all deps

#### Sprint 3–4: Auth + Tenant + Gateway
- ✅ `auth-service` complete with tests
- ✅ `tenant-service` complete with tests  
- ✅ `gateway-service` complete with tests
- ✅ Tenant resolver library complete with tests

#### Sprint 5–6: User + Audit + Notification + Config
- ✅ `user-service` complete with tests
- ✅ `audit-service` complete with tests
- ✅ `notification-service` complete with tests
- ✅ `config-service` complete with tests

#### Sprint 7–8: Workflow + Schedule
- ✅ `workflow-engine` complete with tests
- ✅ `schedule-service` complete with tests

#### Sprint 9–10: File + Reporting
- ✅ `file-service` complete with tests
- ✅ `reporting-service` complete with tests

#### Sprint 11–12: Analytics + Observability + Frontend Foundation
- ✅ `analytics-service` complete with tests
- ✅ Prometheus + Grafana + Loki + Jaeger deployed
- ✅ All Grafana dashboards configured
- ✅ Frontend foundation (auth, layout, navigation, permission gates)
- ✅ Platform admin UI (tenant management, user management)

---

### Phase B — RainerQMS (Sprint 13–28) ✅ COMPLETE

#### Sprint 13–16: Document Service
- ✅ `document-service` complete with tests (Draft→Review→Approved→Obsolete, e-signatures, version history)
- ✅ Document module QMS frontend (search, filters, status badges, pagination)

#### Sprint 17–20: Quality Events + CAPA
- ✅ `quality-event-service` complete with tests
- ✅ `capa-service` complete with tests (action items, effectiveness verification)
- ✅ QMS E2E vertical slice: 14 test cases (create→submit→approve→obsolete)

#### Sprint 21–24: Audit Domain + Training + Equipment
- ✅ `training-service` complete with tests (course management, assignments, completion, certification)
- ✅ `equipment-service` complete with tests (asset management, calibration, PM scheduling)

#### Sprint 25–28: QMS Analytics + Stabilization
- ✅ QMS E2E vertical slice: document → approval → training → audit
- ✅ QMS MVP stabilization

---

### Phase C — EndGameBiotech EM (Sprint 17–30, parallel) ✅ COMPLETE

- ✅ `plate-service` (port 8030): barcode dedup, 15-step lifecycle, history, unit tests
- ✅ `image-service` (port 8031): S3/MinIO, brightfield/fluorescence/darkfield, unit tests
- ✅ `ai-service` (port 8032): colony detection, start/complete/fail, results, unit tests
- ✅ `job-service` (port 8033): async queue, claim/complete/fail/retry, exponential backoff, unit tests
- ✅ `qa-review-service` (port 8034): reviewer assignment, approve/reject, comments, unit tests
- ✅ EM Dashboard frontend (KPI cards, recent plates, skeleton loading)
- ✅ EM Plates frontend (search, status/type filters, pagination, responsive table)
- ✅ E2E vertical slice: 20 test cases (TC-EM-001→025: health→plate→image→AI→QA→approve)
- ✅ docker-compose.yml updated with all 5 EM services

---

### Phase D — RainerCCV (Sprint 17–30, parallel) ✅ COMPLETE

- ✅ `crm-service` (port 8040): Customer/Contact/Interaction, prospect→customer lifecycle, unit tests
- ✅ `contract-service` (port 8041): Draft→Review→Approved→Active→Expired, line items, history, unit tests
- ✅ `workorder-service` (port 8042): Pending→Assigned→InProgress→Completed, tasks, notes, unit tests
- ✅ `technician-service` (port 8043): profiles, certifications, availability, status transitions, unit tests
- ✅ `billing-service` (port 8044): Invoice lifecycle, line items, payments, partial/full pay, unit tests
- ✅ CCV Dashboard frontend (KPI cards, recent contracts/WOs, status badges)
- ✅ Contracts frontend (search, status/type filters, pagination)
- ✅ Work Orders frontend (search, status/priority filters, pagination)
- ✅ E2E vertical slice: prospect→customer→contract→workorder→technician→invoice→paid
- ✅ docker-compose.yml updated with all 5 CCV services

---

### Phase E — Intelligence & Hardening (Sprint 31–40) ✅ COMPLETE

- ✅ k6 load test scripts (auth, document-service, ccv work-order critical paths)
- ✅ Helm chart base templates (Chart.yaml, values.yaml, deployment, service, HPA)
- ✅ Kubernetes NetworkPolicy (default-deny, intra-namespace, gateway ingress)
- ✅ Pod Security Standards (restricted namespace labels for all product namespaces)
- ✅ Security hardening: non-root containers, readOnlyRootFilesystem, dropped capabilities
- ✅ HPA configured (CPU/memory targets, min 2 / max 10 replicas per service)
- ✅ CSP + security headers middleware on all FastAPI services
- ⬜ Istio service mesh (mTLS) — infra provisioning required
- ⬜ Penetration testing — external engagement required
- ⬜ Validation docs (IQ/OQ/PQ) — compliance team deliverable

---

## 14. Development Rules & Standards

### 14.1 Code Quality Rules (Non-Negotiable)

1. **Every service MUST have tests before it is marked done** (unit + integration + E2E)
2. **No hardcoded secrets** — all via Vault/env variables
3. **No `tenant_id` filtering omitted** — every tenant DB query filters by tenant
4. **Every API endpoint MUST be in Swagger** — FastAPI auto-generates this
5. **Structured logs only** — no `print()`, always `logger.info({...})`
6. **Correlation IDs** — every request gets `X-Request-ID`, propagated everywhere
7. **Pydantic models for all I/O** — no raw dicts in request/response
8. **Async everywhere** — all DB, HTTP, Redis operations must be async
9. **Type hints everywhere** — mypy strict mode

### 14.2 Git Conventions

```
feat(auth):     add MFA TOTP support
fix(tenant):    resolve DB connection leak on tenant deletion
test(workflow): add integration tests for state transitions
chore(deps):    upgrade fastapi to 0.115.3
docs(api):      update OpenAPI spec for user-service
```

### 14.3 Service Health Standard

Every service exposes:
```
GET /health/live   → 200 { "status": "ok", "service": "auth-service", "version": "1.0.0" }
GET /health/ready  → 200 or 503 (checks DB, Redis, Kafka)
GET /metrics       → Prometheus text format
```

### 14.4 Database Rules

1. **All migrations via Alembic** — no manual SQL
2. **Every table has**: `id` (UUID), `created_at` (TIMESTAMPTZ), `updated_at` (TIMESTAMPTZ)
3. **Soft deletes**: `deleted_at` TIMESTAMPTZ (nullable) — never hard delete
4. **All queries use async SQLAlchemy** with `AsyncSession`
5. **Repository pattern**: No raw DB calls in routes/domain — always via repository
6. **Indexes**: Every FK column indexed, every frequently-queried column indexed

### 14.5 Error Handling Standard

```python
# All exceptions map to HTTP codes via FastAPI exception handlers
class RainerException(Exception):
    def __init__(self, code: str, message: str, status_code: int = 400, details=None): ...

class NotFoundError(RainerException):   # 404
class ForbiddenError(RainerException):  # 403
class ConflictError(RainerException):   # 409
class ValidationError(RainerException): # 422
```

---

*This document is the source of truth for the Rainer Platform development program. Update the status tracking section as services are completed.*
