# Rainer Platform

Enterprise Quality Management & Compliance Platform — Multi-product SaaS.

## Products

| Product | Description |
|---------|-------------|
| **RainerQMS** | Lab QMS — Document control, quality events, CAPA, training, equipment, audit |
| **EndGameBiotech** | EM + AI plate analytics — image capture, colony detection, QA review |
| **RainerCCV** | CCV ops — CRM, contracts, field execution, billing, certificates |

## Tech Stack

**Backend**: Python FastAPI · SQLAlchemy 2.0 async · Alembic · Pydantic v2 · PostgreSQL 16 · Redis 7 · Apache Kafka 3.7 · MinIO · structlog · OpenTelemetry · Celery

**Frontend**: Next.js 15 (App Router) · shadcn/ui · Tailwind CSS · Framer Motion · Zustand · TanStack Query · SWR · NextAuth.js v5 · Zod

**Infra**: Kubernetes · Helm · Kong Ingress · GitHub Actions · Prometheus + Grafana · Loki · Jaeger

---

## Quick Start (Local Dev)

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node.js 20+

### 1. Start Infrastructure

```bash
make up-infra
```

Starts: PostgreSQL, Redis, Kafka, MinIO, OpenSearch, MailHog, Vault

### 2. Start Observability Stack

```bash
make up-observability
```

Starts: Prometheus, Grafana (port 3001), Loki, Jaeger (port 16686)

### 3. Install Dependencies

```bash
make install-dev
make install-frontend
```

### 4. Run Migrations

```bash
make migrate-master
```

### 5. Start Platform Services

```bash
docker-compose up auth-service tenant-service user-service audit-service
```

### 6. Start Frontend

```bash
cd frontend/apps/web && npm run dev
# Opens at http://localhost:3000
```

---

## Project Structure

```
Portal/
├── backend/
│   ├── shared/              # Shared Python libs (rainer_common, rainer_auth_lib, rainer_tenant_lib)
│   ├── platform/            # Platform services (auth, tenant, user, workflow, audit, ...)
│   ├── qms/                 # RainerQMS domain services
│   ├── em/                  # EndGameBiotech domain services
│   └── ccv/                 # RainerCCV domain services
├── frontend/
│   └── apps/web/            # Next.js application
├── infra/
│   ├── k8s/                 # Kubernetes manifests
│   ├── prometheus/          # Prometheus config + alert rules
│   ├── grafana/             # Grafana provisioning
│   ├── loki/                # Loki config
│   └── promtail/            # Promtail config
├── docker-compose.yml       # Local dev stack
├── Makefile                 # Convenience commands
├── ENTERPRISE_DEVELOPMENT_PLAN.md  # Full architecture + LLD plan
└── PROJECT_MEMORY.md        # Implementation status tracker
```

---

## Service Ports (Local)

| Service | Port |
|---------|------|
| Frontend (Next.js) | 3000 |
| Grafana | 3001 |
| auth-service | 8001 |
| tenant-service | 8002 |
| user-service | 8003 |
| audit-service | 8004 |
| notification-service | 8005 |
| config-service | 8006 |
| workflow-engine | 8007 |
| file-service | 8009 |
| reporting-service | 8010 |
| analytics-service | 8011 |
| document-service (QMS) | 8020 |
| quality-event-service | 8021 |
| capa-service | 8022 |
| training-service | 8023 |
| equipment-service | 8024 |
| PostgreSQL | 5432 |
| Redis | 6379 |
| Kafka | 9092 |
| MinIO API | 9000 |
| MinIO Console | 9001 |
| Prometheus | 9090 |
| Jaeger UI | 16686 |

---

## Testing

```bash
# Run unit tests for a specific service
make test-service SVC=auth-service

# Run all tests (unit + integration + e2e)
make test-all

# Frontend tests
make test-frontend
```

### Test Pyramid

- **Unit tests**: pytest + mocks (fast, no containers)
- **Integration tests**: TestContainers (real PostgreSQL, Redis, Kafka)
- **Contract tests**: Pact (consumer-driven contract testing)
- **E2E tests**: httpx against real app + real DBs (vertical slice flows)

---

## Development Guidelines

1. **Tests first** — No service is "done" without unit + integration + E2E tests
2. **Every endpoint in Swagger** — `GET /docs` on any service
3. **Structured logging** — No `print()`, always structlog with correlation IDs
4. **Tenant isolation** — Every tenant DB query filters by tenant context
5. **Pydantic for all I/O** — No raw dicts in request/response
6. **Async everywhere** — All DB/HTTP/Redis/Kafka operations async
7. **Repository pattern** — No direct DB calls in routes or domain
8. **Soft deletes** — Never hard-delete records (`deleted_at` timestamp)
9. **Secrets via Vault** — Never hardcode secrets, never commit to git

---

## Documentation

- `ENTERPRISE_DEVELOPMENT_PLAN.md` — Full HLD + LLD, architecture decisions, service catalog
- `PROJECT_MEMORY.md` — Phase & service implementation status tracker
- Individual service `README.md` files (in each service folder)
- Swagger UI: `http://localhost:{PORT}/docs` for each service

---

## Architecture Decisions

| ADR | Decision |
|-----|----------|
| ADR-001 | DB-per-tenant with HMAC-derived passwords |
| ADR-002 | Python FastAPI for all backend services |
| ADR-003 | Kafka for async events (durability + replay) |
| ADR-004 | JWT RS256 with 15min access / 7-day refresh |
| ADR-005 | PgBouncer transaction mode (async-optimized) |
| ADR-006 | Repository pattern for all DB access |
| ADR-007 | OpenTelemetry unified observability |
| ADR-008 | K8s namespaces per domain |
