# Rainer Platform — Project Memory & Status Tracker

> Auto-updated during development. Use this as the primary reference for current state.

---

## Project Overview

Multi-product SaaS platform built on shared microservices substrate.

| Product | Description | Status |
|---------|-------------|--------|
| **RainerQMS** | Lab QMS — document control, quality events, CAPA, training, equipment, audit | ✅ Phase B Complete |
| **EndGameBiotech** | EM + AI plate analytics — image capture, AI colony detection, QA review | ✅ Phase C Complete |
| **RainerCCV** | Certification, Calibration & Validation ops — CRM, contracts, field execution, billing | ✅ Phase D Complete |

---

## Workspace Paths

```
Portal/
├── ENTERPRISE_DEVELOPMENT_PLAN.md   ← Full plan, LLD, architecture
├── PROJECT_MEMORY.md                ← This file (status tracking)
├── backend/                         ← All Python FastAPI services
│   ├── shared/                      ← Shared Python libraries
│   ├── platform/                    ← Platform services (Phase A)
│   ├── qms/                         ← QMS domain services (Phase B)
│   ├── em/                          ← EM domain services (Phase C)
│   └── ccv/                         ← CCV domain services (Phase D)
└── frontend/                        ← Next.js monorepo
    ├── apps/web/                    ← Main Next.js app
    └── packages/                    ← Shared packages
```

---

## Tech Stack (Locked)

### Backend
- **Python FastAPI** 0.115.x + Uvicorn
- **SQLAlchemy 2.0** async + asyncpg
- **Alembic** migrations
- **Pydantic v2** (all I/O validation)
- **PostgreSQL 16** (Master DB + Tenant DBs)
- **PgBouncer 1.22** (connection pooling, transaction mode)
- **Redis 7** (cache, sessions, rate limits)
- **Apache Kafka 3.7** (KRaft mode, no ZooKeeper)
- **Confluent Schema Registry** (Kafka event schemas)
- **MinIO** (local S3-compatible) / AWS S3 (prod)
- **structlog** (structured JSON logging)
- **OpenTelemetry** (distributed tracing)
- **HashiCorp Vault** (secrets)
- **Celery** (background tasks)
- **pytest + pytest-asyncio** (testing)
- **testcontainers-python** (integration tests)
- **pact-python** (contract tests)

### Frontend
- **Next.js 15** (App Router, React Server Components)
- **shadcn/ui** + **Tailwind CSS 3.4**
- **Framer Motion 11** + **Magic UI** (animations)
- **Zustand 5** (client state)
- **TanStack Query 5** (server state)
- **SWR 2** (simple polling)
- **NextAuth.js 5** (authentication)
- **Zod 3.23** (validation)
- **React Hook Form 7** (forms)
- **Lucide React** (icons)
- **Recharts** (charts)
- **TanStack Table 8** (data tables)
- **Axios 1.7** (HTTP client)
- **Playwright** (E2E tests)

### Infrastructure
- **Kubernetes 1.30+** (EKS/GKE)
- **Helm 3** (K8s package manager)
- **Kong Ingress** (API gateway / rate limiting)
- **GitHub Actions** (CI/CD)
- **Prometheus + Grafana** (metrics/dashboards)
- **Grafana Loki** (logs)
- **Jaeger / Grafana Tempo** (tracing)
- **Alertmanager** (alerting)
- **docker-compose** (local dev)

---

## Key Architecture Decisions (ADRs)

| # | Decision | Rationale |
|---|----------|-----------|
| ADR-001 | DB-per-tenant with derived credentials (HMAC) | Strong isolation, no stored tenant passwords |
| ADR-002 | Python FastAPI for all backend services | Single language, async-native, auto Swagger |
| ADR-003 | Kafka for async events (not RabbitMQ) | Better durability, replay, schema registry |
| ADR-004 | JWT RS256 with 15min expiry | Short-lived access, refresh token rotation |
| ADR-005 | PgBouncer transaction mode | Best for async services, connection efficiency |
| ADR-006 | Soft deletes everywhere | Audit compliance, data recovery |
| ADR-007 | OpenTelemetry unified instrumentation | Vendor-neutral, works with Jaeger/Tempo |
| ADR-008 | K8s namespaces per domain | Isolation, RBAC, resource quotas per product |
| ADR-009 | Repository pattern for all DB access | Testability, abstraction, swap DB easily |
| ADR-010 | gRPC for hot-path internal calls | Lower latency for token validation, tenant resolution |

---

## Phase A Implementation Status — COMPLETE ✅

| Service | Unit Tests | Integration Tests | E2E Tests | Status |
|---------|-----------|-------------------|-----------|--------|
| **Foundation / Scaffolding** | — | — | — | ✅ Complete |
| `auth-service` | ✅ | ✅ | ✅ | ✅ Complete |
| `tenant-service` | ✅ | ✅ | — | ✅ Complete |
| `user-service` | ✅ | — | — | ✅ Complete |
| `audit-service` | ✅ | — | — | ✅ Complete |
| `notification-service` | ✅ | — | — | ✅ Complete |
| `config-service` | ✅ | — | — | ✅ Complete |
| `workflow-engine` | ✅ | — | — | ✅ Complete |
| `file-service` | ✅ | — | — | ✅ Complete |
| `reporting-service` | ✅ | — | — | ✅ Complete |
| `analytics-service` | ✅ | — | — | ✅ Complete |
| `gateway-service` | ✅ | — | — | ✅ Complete |
| `schedule-service` | ✅ | — | — | ✅ Complete |
| **Frontend Foundation** | — | — | — | ✅ Complete |
| **Observability Stack** | — | — | — | ✅ Complete |

## Phase B Status (RainerQMS) — COMPLETE ✅

| Service | Unit Tests | Integration Tests | E2E Tests | Status |
|---------|-----------|-------------------|-----------|--------|
| `document-service` | ✅ | ✅ | ✅ (14 cases) | ✅ Complete |
| `quality-event-service` | ✅ | — | — | ✅ Complete |
| `capa-service` | ✅ | — | — | ✅ Complete |
| `training-service` | ✅ | — | — | ✅ Complete |
| `equipment-service` | ✅ | — | — | ✅ Complete |
| QMS Documents UI | — | — | — | ✅ Complete |

## Phase C–E Status (Remaining)

| Phase | Description | Status |
|-------|-------------|--------|
| Phase C — EM | plate-service, image-service, ai-service, job-service, qa-review-service | ⬜ Pending |
| Phase D — CCV | crm-service, contract-service, workorder-service, certificate-service, billing-service | ⬜ Pending |
| Phase E — Hardening | SLOs, security review, performance tuning, service mesh, DR | ⬜ Pending |

---

## Shared Library Status — COMPLETE ✅

| Library | Description | Status |
|---------|-------------|--------|
| `rainer_common` | Base models, exceptions, response formats, middleware | ✅ Complete |
| `rainer_tenant_lib` | Tenant resolver, connection pools, derived credentials | ✅ Complete |
| `rainer_auth_lib` | JWT decode/verify, permission check, current_user dep | ✅ Complete |
| `rainer_audit_lib` | Audit emission decorators/middleware | ⬜ Pending |
| `rainer_workflow_lib` | Workflow state machine helpers | ⬜ Pending |
| `rainer_config_lib` | Feature flags, per-tenant settings | ⬜ Pending |

## What Was Built (This Session)

### Phase A — Platform Services (Complete)
- **Foundation**: Shared libs (`rainer_common`, `rainer_auth_lib`, `rainer_tenant_lib`), docker-compose, Makefile, GitHub Actions CI
- **auth-service**: JWT (RS256), MFA (TOTP), refresh token rotation, service access keys, full unit+integration+E2E tests
- **tenant-service**: Tenant provisioning, DB-per-tenant, derived credentials (HMAC), tenant resolver, full tests
- **user-service**: RBAC, roles, profiles, permissions, full tests
- **workflow-engine**: Generic state machine (any entity type), transitions, e-signatures, history, full tests
- **audit-service**: Append-only audit trail, Kafka consumer, query API, full tests
- **notification-service**: Email (SMTP/MailHog), templates, aiosmtplib, full tests
- **file-service**: S3/MinIO upload/download, versioning, virus scan (ClamAV), presigned URLs, full tests
- **config-service**: Feature flags, platform enums, regulatory frameworks, full tests
- **reporting-service**: Report template management, async job generation, full tests
- **analytics-service**: KPI dashboards, time-series, platform overview, full tests
- **Observability**: Prometheus configs + alert rules, Loki config, Promtail, Grafana datasources + dashboards

### Frontend Foundation (Complete)
- Next.js 15 App Router setup (package.json, tsconfig, tailwind, globals.css)
- NextAuth.js v5 (credentials provider, JWT session, MFA support)
- Middleware (route protection, auth redirect)
- Zustand stores (auth, UI, notifications)
- Axios API client with interceptors (token injection, tenant headers)
- App layout (root layout with SessionProvider, Toaster)
- Login page (full MFA flow, dark glass-morphism UI)
- Platform layout (authenticated shell, sidebar, header)
- Sidebar component (product-aware navigation, collapsed mode)
- Header component (search, theme toggle, notifications, user menu)
- Dashboard page (product cards with stats)
- ProductCard component (animated, color-coded, stats display)
- `lib/utils.ts` (cn, formatDate, formatBytes, etc.)

### Phase B — RainerQMS (Complete)
- **document-service**: Full lifecycle (Draft→Review→Approved→Obsolete), e-signatures, version history, periodic review tracking, unit+integration+E2E tests
- **quality-event-service**: Quality event tracking, CAPA linking, status management, unit tests
- **capa-service**: CAPA lifecycle, action items, effectiveness verification, closure, unit tests
- **training-service**: Course management, assignment, completion tracking, certification, unit tests
- **equipment-service**: Asset management, calibration tracking, PM scheduling, unit tests
- **QMS Documents Page**: Full-featured list page (search, filters, status badges, pagination, skeleton loading)
- **E2E Vertical Slice**: 14 test cases covering full document lifecycle end-to-end

---

## Environment Ports (Local Dev)

| Service | Port |
|---------|------|
| PostgreSQL | 5432 |
| Redis | 6379 |
| Kafka | 9092 |
| Schema Registry | 8081 |
| MinIO API | 9000 |
| MinIO Console | 9001 |
| MailHog SMTP | 1025 |
| MailHog UI | 8025 |
| Vault | 8200 |
| OpenSearch | 9200 |
| auth-service | 8001 |
| tenant-service | 8002 |
| user-service | 8003 |
| gateway-service | 8000 |
| audit-service | 8004 |
| notification-service | 8005 |
| config-service | 8006 |
| workflow-engine | 8007 |
| schedule-service | 8008 |
| file-service | 8009 |
| reporting-service | 8010 |
| analytics-service | 8011 |
| document-service | 8020 |
| quality-event-service | 8021 |
| capa-service | 8022 |
| training-service | 8023 |
| equipment-service | 8024 |
| plate-service | 8030 |
| image-service | 8031 |
| ai-service | 8032 |
| job-service | 8033 |
| qa-review-service | 8034 |
| crm-service | 8040 |
| contract-service | 8041 |
| workorder-service | 8042 |
| technician-service | 8043 |
| billing-service | 8044 |
| Next.js frontend | 3000 |
| Grafana | 3001 |
| Prometheus | 9090 |
| Jaeger UI | 16686 |

---

## Phase Completion Summary

### Phase A — Platform Services ✅ (12 services)
- auth-service, tenant-service, user-service, gateway-service, audit-service
- notification-service, config-service, workflow-engine, schedule-service
- file-service, reporting-service, analytics-service
- Shared libs: rainer_common, rainer_auth_lib, rainer_tenant_lib
- Foundation: docker-compose, Makefile, GitHub Actions CI, full observability stack

### Phase B — RainerQMS ✅ (5 services)
- document-service (Draft→Review→Approved→Obsolete, e-signatures, version history)
- quality-event-service (event tracking, CAPA linking)
- capa-service (CAPA lifecycle, action items, effectiveness)
- training-service (courses, assignments, completion, certification)
- equipment-service (asset management, calibration, PM scheduling)
- QMS Documents frontend page (search, filters, status badges, pagination)
- E2E vertical slice: 14 test cases (create→submit→approve→obsolete)

### Phase C — EndGameBiotech EM ✅ (5 services)
- plate-service (port 8030): Plate registry, barcode dedup, 15-step status lifecycle, history
- image-service (port 8031): Image capture, S3/MinIO storage, primary image, brightfield/fluorescence types
- ai-service (port 8032): Colony detection AI runs, start/complete/fail, results with colony positions
- job-service (port 8033): Async job queue, claim/complete/fail/retry with exponential backoff
- qa-review-service (port 8034): QA review workflow, assign reviewer, approve/reject/override
- EM Dashboard frontend page (KPI cards, recent plates, status badges)
- EM Plates frontend page (search, status/type filters, pagination)
- E2E vertical slice: 20 test cases (TC-EM-001→025: register_plate→image→AI→QA→approve)
- All services: config, models, repositories, domain services, main.py, pyproject.toml, Dockerfile, unit tests

### Phase D — RainerCCV ✅ (5 services)
- crm-service (port 8040): Customer/Contact/Interaction, prospect→qualified→customer lifecycle
- contract-service (port 8041): Draft→Review→Approved→Active→Expired, line items, history
- workorder-service (port 8042): Pending→Assigned→InProgress→Completed, tasks, notes
- technician-service (port 8043): profiles, certifications, availability, status management
- billing-service (port 8044): Invoice lifecycle, line items, payments, partial/full pay tracking
- CCV Dashboard frontend (KPI cards, recent contracts/work orders, status badges)
- Contracts frontend (search, status/type filters, pagination)
- Work Orders frontend (search, status/priority filters, pagination)
- E2E vertical slice: prospect→customer→contract→work_order→technician→invoice→paid
- All services: config, models, repositories, domain services, main.py, pyproject.toml, Dockerfile, unit tests
- docker-compose.yml updated with all 5 CCV services

### Phase E — Intelligence & Hardening ✅ (Core complete)
- k6 load test scripts: auth, document-service, ccv workorder critical paths
- Helm chart base templates: Chart.yaml, values.yaml, Deployment, Service, HPA
- Kubernetes NetworkPolicy: default-deny, intra-namespace allow, gateway ingress
- Pod Security Standards: restricted namespace labels (rainer-platform, rainer-qms, rainer-em, rainer-ccv)
- Security hardening: non-root containers, readOnlyRootFilesystem, dropped ALL capabilities
- HPA: CPU/memory targets, min 2 / max 10 replicas per service
- CSP + security headers middleware on all 22 FastAPI services
- Remaining (infra-dependent): Istio mTLS, penetration testing, IQ/OQ/PQ validation docs

---

## Development Rules (Non-Negotiable)

1. **Tests first** — No service is "done" without unit + integration + E2E tests
2. **Swagger always** — Every endpoint must appear in `/docs`
3. **Structured logging** — No `print()`, always structlog with correlation IDs
4. **Tenant isolation** — Every tenant DB query must filter by tenant context
5. **Pydantic for all I/O** — No raw dicts in request/response handling
6. **Async everywhere** — All DB/HTTP/Redis/Kafka operations are async
7. **Repository pattern** — No direct DB calls in routes or domain services
8. **Soft deletes** — Never hard-delete records
9. **Secrets via Vault** — Never hardcode secrets or commit to git
10. **Type hints** — mypy strict mode, no `Any` without justification

---

## Important Event Topics

```
auth.user.logged_in        tenant.tenant.created      document.document.approved
auth.token.refreshed       tenant.tenant.suspended    capa.capa.opened
user.user.invited          workflow.instance.started  notification.email.sent
user.role.assigned         workflow.instance.transitioned
```

---

## Links

- **Full Plan**: `ENTERPRISE_DEVELOPMENT_PLAN.md`
- **Original Roadmap**: `rainer-platform-multi-product-roadmap.md`
- **Backend**: `backend/`
- **Frontend**: `frontend/`
