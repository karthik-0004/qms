# Changelog

All notable changes to the Rainer Platform will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Phase D — RainerCCV**: 5 CCV microservices (crm, contract, workorder, technician, billing) with domain logic, repositories, models, unit tests, Dockerfiles
- **API Routers**: HTTP API routes + Pydantic v2 request/response schemas for all 14 Phase B/C/D services
- **Alembic Scaffolds**: Migration configuration (alembic.ini, env.py) for all 27 services
- **Frontend Pages**: 13 new pages — QMS (quality-events, capa, training, equipment, analytics), EM (jobs, analytics), CCV (crm, technicians, billing, certificates, analytics), Platform (settings, users)
- **Sidebar Navigation**: Added technicians + billing links to CCV nav; fixed /ccv/workorders → /ccv/work-orders URL mismatch
- **CI/CD**: Added Phase B/C/D change detection (18 filters), matrix test jobs (QMS, EM, CCV), expanded Docker build matrix to 27 services
- **.env.example**: Environment variable documentation for all 27 services
- **.dockerignore**: Build exclusions for all services
- **Playwright**: E2E test configuration + smoke test suite
- **Helm Chart**: ConfigMap, Secret, Ingress, ServiceAccount, RBAC, _helpers.tpl, NOTES.txt templates
- **Makefile**: Phase B/C/D targets for testing, migrations, and dev setup
- **Frontend API Client**: Typed service clients for QMS, EM, CCV with TanStack Query hooks
- **Frontend RBAC**: usePermission hook + withRBAC higher-order component
- **DB Seed Script**: Bootstrap admin tenant, admin user, and platform config defaults

### Fixed
- Sidebar URL mismatch: `/ccv/workorders` → `/ccv/work-orders`

## [0.1.0] — 2025-01-15

### Added
- **Phase A — Platform Services**: 12 microservices (auth, tenant, user, gateway, audit, notification, config, workflow, schedule, file, reporting, analytics)
- **Phase B — RainerQMS**: 5 QMS microservices (document, quality-event, capa, training, equipment)
- **Phase C — EndGameBiotech EM**: 5 EM microservices (plate, image, ai, job, qa-review)
- **Shared Libraries**: rainer_common, rainer_auth_lib, rainer_tenant_lib
- **Infrastructure**: docker-compose (full stack), Kubernetes manifests, Helm chart, Prometheus + Grafana + Loki + Jaeger observability
- **Frontend**: Next.js 15 app with NextAuth v5, Zustand, shadcn/ui, TanStack Query, dashboard, QMS documents page, EM dashboard + plates pages
- **CI/CD**: GitHub Actions pipeline with change detection, test jobs, Docker image builds
- **Auth E2E**: 14 test cases for document lifecycle (create → submit → approve → obsolete)
- **EM E2E**: 20 test cases (health → register → sampling → incubation → image → AI → QA → approve)
