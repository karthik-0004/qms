# RainerQMS — Codebase vs. Documentation Gap Analysis & API Binding Status Report

**Repository:** `c:\Users\akash\qms-clubed` (Rainer Platform / RainerQMS)  
**Master documentation:** `RainerQMS_Master_Documentation.md` (present; read in full)  
**Report date:** 2026-05-13  
**Analyst note:** Instructions referenced NestJS/Prisma; **evidence in this repo** shows **Python 3.12+ FastAPI**, **SQLAlchemy 2.0 async**, **Alembic**, **Next.js 15 App Router**, and **no Prisma/NestJS**. This report uses the **actual** stack unless explicitly contrasting with the master document.

**Section map (12):** (1) Executive Summary → (2) Documentation Baseline → (3) Codebase Architecture & Scope → (4) Global Cross-Reference → (5) Per-Module Status → (6) REST Endpoint & Client Binding Matrix → (7) Entity & Field Analysis → (8) Roles, Permissions & UI Guards → (9) Workflow Implementation Mapping → (10) Integrations & Platform Dependencies → (11) Compliance, Audit Trail & Electronic Signatures → (12) Prioritized Gap Resolution Summary.

---

## 1. Executive Summary

**Sampling method (brief):** Full read of `RainerQMS_Master_Documentation.md`; listing of root and `docs/**/*.md`; directory walk of `backend/` (27 `main.py` services), `frontend/apps/web/`, and targeted `grep` for `APIRouter`, `@router`, `EventPublisher`, `Keycloak`, `Temporal`, OpenSearch, S3/MinIO, and frontend API clients (`lib/api/**`). Prisma/schema files: **none found** (0 `*.prisma`).

**Top findings:**

1. **Stack & platform mismatch vs master doc:** Master doc specifies NestJS, Prisma, Keycloak, Temporal, dedicated `search-service`, and 14 QMS microservices. The repo implements **FastAPI + SQLAlchemy**, **JWT auth-service** (no Keycloak references under `backend/platform/auth-service`), **no Temporal usage in code**, **no `search-service` microservice**, and **only five QMS domain services** (document, quality-event, capa, training, equipment). **EndGameBiotech (EM)** and **RainerCCV** are substantial products in code/README but are **outside** the QMS master document’s module list.

2. **API gateway coverage is partial:** `gateway-service` proxies **documents**, plus platform/CCV routes; it does **not** register proxies for **quality-event**, **capa**, **training**, **equipment**, or **analytics**. Default QMS client base URLs send **capa, training, and equipment** traffic to the **gateway** (`NEXT_PUBLIC_API_URL`), which will **not** route those paths unless operators set per-service `NEXT_PUBLIC_QMS_*_API_URL` env vars—otherwise calls **404** or hit wrong handlers.

3. **Concrete FE↔BE path and contract mismatches:** Frontend `lib/api/services/qms.ts` calls **`/capa/capas`** and **`/capa/capas/{id}/transition`**, but the CAPA service exposes **`/api/v1/capas`** and has **no** `transition` route (updates use `PATCH`, closure `POST /close`, etc.). Equipment client uses **`/equipment/assets`**; backend uses **`/api/v1/equipment`** (list `GET ""`, item `GET /{id}`). CAPA list handling does not normalize the backend’s `{ data, pagination }` envelope the way documents/quality-events do. CAPA UI types reference **`priority`**; API schema exposes **`severity`**.

4. **Nine documented QMS workflows vs code:** Document, CAPA, quality event, training (courses/assignments), and equipment/calibration have **partial** API/domain support. **Audit management**, **internal audit workflow**, **supplier**, **risk**, **PT**, **complaints**, **management review**, **environmental excursion**, and **non-conforming work** as first-class services/workflows are **not** implemented as dedicated QMS microservices in this tree (platform `audit-service` is **platform audit logs**, not ISO audit program management).

5. **Event-driven architecture (doc §7.3) largely absent in QMS services:** Shared `rainer_events` (Kafka) exists, and `audit-service` references processing Kafka events, but **no matches** for `EventPublisher` / publish calls under `backend/qms/` in this scan—cross-service triggers described in the master doc (e.g. document approved → training) are **not evidenced** in QMS service code.

**Blockers:** None for reading master documentation (`RainerQMS_Master_Documentation.md` found at repo root).

---

## 2. Documentation Baseline (from `RainerQMS_Master_Documentation.md` + repo Markdown)

### 2.1 Fourteen modules (as documented)

| # | Module | Documented microservice |
|---|--------|-------------------------|
| 1 | Document Control & Management | `document-service` |
| 2 | Quality Event Management | `quality-event-service` |
| 3 | CAPA Management | `capa-service` |
| 4 | Audit Management | `audit-service` |
| 5 | Training & Competency | `training-service` |
| 6 | Equipment & Calibration | `equipment-service` |
| 7 | Environmental Monitoring | `envmon-service` |
| 8 | Supplier & Reagent Quality | `supplier-service` |
| 9 | Risk Management | `risk-service` |
| 10 | Proficiency Testing & ILC | `proficiency-testing-service` |
| 11 | Customer Complaints | `complaint-service` |
| 12 | Management Review | `management-review-service` |
| 13 | Reporting & Analytics | `analytics-service` |
| 14 | Lab-Specific Features | *(distributed)* |

### 2.2 Eight roles (as documented)

System/Tenant Admin, Quality Manager, Lab Director, Section Head, Analyst/Technician, Viewer, Auditor, API User (master doc §3.1; notes MVP “5 roles” vs extended list).

### 2.3 Nine workflows (as documented)

1. Document lifecycle (§4.1)  
2. CAPA (§4.2)  
3. Internal audit (§4.3)  
4. Equipment calibration (§4.4)  
5. Non-conforming work (§4.5)  
6. Supplier qualification (§4.6)  
7. Customer complaint (§4.7)  
8. Management review (§4.8)  
9. Environmental excursion (§4.9)

### 2.4 Key entities / fields (documented)

Master §5 defines rich graphs: `Tenant`, `Site`, `Document`, `QualityEvent`, `CAPA`, `CAPAAction`, `Audit`, `AuditFinding`, `Equipment`, `CalibrationRecord`, `TrainingPlan`/`TrainingAssignment`/`TrainingRecord`, `Supplier`, immutable `AuditTrailRecord`, etc., with field tables for documents, events, CAPAs, audits, equipment, training assignments, calibration records.

### 2.5 Integrations (documented)

LIMS/ERP catalogs, IdP/SSO (deferred MVP), IoT/edge, M365/Slack/Teams, HL7/FHIR/ASTM, **Kafka** bus, **OpenSearch**, **S3**, **Keycloak**, **Temporal**, public REST API (Phase 2+).

### 2.6 Implied APIs (from workflows & entities)

REST (and optional future GraphQL) for CRUD + workflow transitions on all module aggregates; webhooks; file upload; search; auth/token; tenant resolution; notification dispatch; analytics KPIs/dashboards.

### 2.7 Tech stack (documented vs README)

| Layer | Master doc | Repo `README.md` (evidence) |
|-------|------------|-----------------------------|
| Frontend | React 18 + Vite + TanStack Query + … | **Next.js 15** App Router, TanStack Query, shadcn, Tailwind |
| Backend | NestJS + Prisma | **FastAPI** + **SQLAlchemy** + **Alembic** + Pydantic v2 |
| Auth | Keycloak | **auth-service** (JWT; no Keycloak in auth-service tree) |
| DB | PostgreSQL schema-per-tenant | PostgreSQL (multi-service DBs; tenant context via headers/JWT) |
| Events | Kafka | Kafka **libraries** + audit consumer patterns; **limited publisher usage in QMS** |
| Search | OpenSearch | **Compose mentions OpenSearch**; no dedicated search microservice located |
| Workflow | Temporal | **Not found** in codebase grep |

### 2.8 Other Markdown reviewed

`README.md`, `GAPS.md`, `PROJECT_MEMORY.md`, `COMBINED_DEVELOPMENT_PLAN.md`, `CHANGELOG.md`, `docs/run-local.md`, `docs/dev-auth-access.md`, `docs/services.md`, `docs/APIs/platform/README.md`, `backend/README.md`, EM/CCV smoke/testing docs, `rainer-platform-multi-product-roadmap.md`, `ui-testing-practices.md`.

**Important:** `GAPS.md` claims broad “✅ RESOLVED” production readiness; this report **re-verifies against** master-doc expectations and **flags remaining inconsistencies** (e.g. gateway and client paths) so `GAPS.md` should not be treated as sole truth without cross-check.

---

## 3. Codebase Architecture (Observed) & Scope

### 3.1 Backend layout

- **`backend/platform/`**: auth, tenant, user, gateway, audit, notification, config, workflow-engine, file, reporting, analytics, schedule, (+ gateway aggregates CCV proxies).  
- **`backend/qms/`**: **5** services — document, quality-event, capa, training, equipment.  
- **`backend/em/`**, **`backend/ccv/`**: non-QMS products (plates, jobs, CRM, contracts, etc.).

### 3.2 Frontend layout

- **`frontend/apps/web`**: Next.js routes for QMS (`(qms)/qms/...`), EM, CCV, platform settings, admin/super-admin.

### 3.3 “NestJS / Prisma” instruction

**No NestJS `nest-cli.json` or `main.ts` (Nest)** and **no Prisma schema** were found. Persistence is **SQLAlchemy models** per service (e.g. `document-service/app/infra/db/models.py`).

---

## 4. Global Cross-Reference: Documentation vs Code

| Theme | Documentation says | Code / repo says | Gap |
|-------|-------------------|------------------|-----|
| Backend framework | NestJS | FastAPI | **High** — all architecture diagrams/onboarding assuming Nest are inaccurate for this repo |
| ORM | Prisma | SQLAlchemy + Alembic | **High** |
| Auth | Keycloak | JWT auth-service | **High** for enterprises expecting Keycloak |
| QMS microservices | 14 modules each as service | 5 QMS services + platform | **Critical** for modules 4,7–14 as dedicated QMS domains |
| `audit-service` | ISO audit program | Platform audit **logs** API | **Naming / domain** confusion |
| Workflow engine | Temporal | workflow-engine **HTTP API** exists; no Temporal client in repo | **Medium** |
| Cross-module Kafka | Many triggers | QMS publishers not evidenced | **High** |
| Search | OpenSearch service | Infra may run OpenSearch; no `search-service` | **Medium** |
| Multi-product | RainerQMS focus | EM + CCV first-class | **Doc scope** vs **repo scope** |

---

## 5. Per-Module Status (14 QMS Modules)

**Legend — implementation:** `Full` = service + core CRUD/workflow APIs aligned with doc MVP; `Partial` = subset; `Missing` = no dedicated service found.  
**Legend — binding:** `Fully Bound` = gateway or consistent base URL + FE client paths + response shapes aligned; `Partially Bound` = some flows or env-dependent; `Not Bound` = no/minimal FE or broken paths.

| # | Module | Backend | Frontend (QMS area) | Binding status |
|---|--------|---------|---------------------|----------------|
| 1 | Document Control | **Partial** — `document-service` + gateway proxy | **Partial** — list/create/approve flows in UI | **Partially Bound** — document path most consistent |
| 2 | Quality Events | **Partial** — `quality-event-service` | **Partial** — list/create | **Partially Bound** — defaults to **:8021** in client (bypasses gateway) |
| 3 | CAPA | **Partial** — `capa-service` | **Partial** — list UI | **Not Bound** — wrong URL prefix; missing `transition`; response shape |
| 4 | Audit Management | **Missing** as QMS domain | **Missing** | **Not Bound** |
| 5 | Training | **Partial** — courses + assignments APIs | **Partial** — courses UI | **Partially Bound** — gateway default issue; paths differ from some FE assumptions |
| 6 | Equipment | **Partial** — assets + calibrate endpoints | **Partial** — list/create | **Not Bound** — `/equipment/assets` vs `/equipment` |
| 7 | Environmental Monitoring | **Missing** | **Missing** | **Not Bound** |
| 8 | Supplier | **Missing** | **Missing** | **Not Bound** |
| 9 | Risk | **Missing** | **Missing** | **Not Bound** |
| 10 | Proficiency Testing | **Missing** | **Missing** | **Not Bound** |
| 11 | Complaints | **Missing** | **Missing** | **Not Bound** |
| 12 | Management Review | **Missing** | **Missing** | **Not Bound** |
| 13 | Reporting & Analytics | **Partial** — `analytics-service` | **Partial** — hooks call `/analytics/*` via platform client | **Not Bound** via gateway — **no analytics proxy** on gateway |
| 14 | Lab-Specific Features | **Missing** as dedicated implementation | N/A | **Not Bound** |

---

## 6. REST Endpoint & Client Binding Matrix

### 6.1 QMS: Document service (`document-service`, prefix `/api/v1/documents`)

| HTTP | Backend route (evidence) | Frontend / caller | Match? |
|------|--------------------------|---------------------|--------|
| GET | `/` list | `documentsApi.list` → `GET /documents` | ✅ (via gateway or direct) |
| POST | `/` create | `documentsApi.create` | ✅ |
| GET | `/{id}` | `documentsApi.get` | ✅ |
| PATCH | `/{id}` | (not wired in excerpt) | ⚠️ partial |
| DELETE | `/{id}` | (if used) | ⚠️ |
| POST | `/{id}/submit-for-review` | `submitForReview` | ✅ |
| POST | `/{id}/approve` | `approve` | ✅ |
| POST | `/{id}/reject` | (if used) | ⚠️ |
| POST | `/{id}/make-obsolete` | (if used) | ⚠️ |
| GET | `/{id}/versions` | (if used) | ⚠️ |
| GET | `/due-for-review` | (if used) | ⚠️ |

**Orphan backend (no FE reference in `qms.ts`):** `reject`, `make-obsolete`, `versions`, `due-for-review` if UI does not call them (confirm per-page).

### 6.2 QMS: Quality events (`quality-event-service`, `/api/v1/quality-events`)

| HTTP | Backend | Frontend | Match? |
|------|---------|----------|--------|
| GET | `/` | `qualityEventsApi.list` | ✅ envelope normalized |
| POST | `/` | `create` | ✅ |
| GET | `/summary` | (optional; check UI) | ⚠️ |
| GET | `/{id}` | `get` | ✅ |
| PATCH | `/{id}` | (check UI) | ⚠️ |
| POST | `/{id}/close` | (check UI) | ⚠️ |
| DELETE | `/{id}` | (check UI) | ⚠️ |

### 6.3 QMS: CAPA (`capa-service`, `/api/v1/capas`)

| HTTP | Backend route | Frontend (`qms.ts`) | Match? |
|------|---------------|---------------------|--------|
| GET | `/` | `GET /capa/capas` | ❌ **wrong path** |
| POST | `/` | `POST /capa/capas` | ❌ |
| GET | `/{id}` | `GET /capa/capas/{id}` | ❌ |
| PATCH | `/{id}` | (not used) | ⚠️ |
| POST | `/{id}/close` | (not used) | ⚠️ |
| POST | `/{id}/verify-effectiveness` | (not used) | ⚠️ |
| GET/POST | `/{id}/actions` … | (not used) | ⚠️ |
| — | *(none)* | `POST …/transition` | ❌ **orphan FE call** |

**Orphan backend routes (no matching FE in `qms.ts`):** `PATCH /capas/{id}`, `POST /close`, `POST /verify-effectiveness`, actions CRUD/complete.

### 6.4 QMS: Training (`training-service`, `/api/v1/training/...`)

| HTTP | Backend | Frontend | Match? |
|------|---------|----------|--------|
| GET | `/training/courses` | `trainingApi.list` | ✅ path |
| POST | `/training/courses` | `create` | ✅ |
| GET | `/training/courses/{id}` | `get` | ✅ |
| *(others in file)* | assignments, complete, etc. | (verify UI) | ⚠️ |

### 6.5 QMS: Equipment (`equipment-service`, `/api/v1/equipment`)

| HTTP | Backend | Frontend | Match? |
|------|---------|----------|--------|
| GET | `""` (list) | `GET /equipment/assets` | ❌ |
| POST | `""` (create) | `POST /equipment/assets` | ❌ |
| GET | `/{id}` | `GET /equipment/assets/{id}` | ❌ |
| GET | `/due-for-calibration` | (check) | ⚠️ |
| POST | `/{id}/calibrate` | (check) | ⚠️ |
| POST | `/{id}/decommission` | (check) | ⚠️ |
| DELETE | `/{id}` | (check) | ⚠️ |

### 6.6 Platform: Analytics (`analytics-service`, `/api/v1/analytics`)

| HTTP | Backend | Frontend (`analytics.ts` via `apiClient`) | Match? |
|------|---------|---------------------------------------------|--------|
| GET | `/kpis` | `/analytics/kpis` → gateway `/api/v1/analytics/kpis` | ❌ **gateway has no analytics router** |

**Orphan backend (relative to gateway):** entire `analytics-service` surface when called through default `NEXT_PUBLIC_API_URL` gateway.

### 6.7 Gateway-mounted routers (observed `gateway-service/app/api/v1/__init__.py`)

Includes: `gateway`, `auth`, `audit` proxy, **`documents` proxy**, `notifications`, `tenants`, `users`, `crm`, **CCV services proxy** — **not** quality-event, capa, training, equipment, analytics.

---

## 7. Entity & Field Analysis (ORM vs Master §5)

**Method:** Compared master entity field tables to representative SQLAlchemy + Pydantic surfaces (`document-service` models; `equipment-service` / `capa-service` responses).

### 7.1 Document

| Doc field (subset) | Implemented (observed) | Status |
|--------------------|--------------------------|--------|
| `document_id` | `id` UUID | ✅ |
| `document_number` | `doc_number` | ✅ |
| `distribution_list[]` | not in `Document` model | **Missing** |
| `approvers[]` | single `approver_id` | **Partial / mismatch** |
| `content` rich text | not separate column (file_id / metadata?) | **Partial** |
| `audit_trail[]` | not on document row (platform audit / separate pattern?) | **Partial** |

### 7.2 Quality event

Frontend `QualityEvent` type uses `event_number`, `reported_by`, `reported_at`; backend uses different naming in responses (verify `QualityEventResponse`); alignment **requires** OpenAPI or schema diff (flagged **internal conflict risk**).

### 7.3 CAPA

| Doc field | API response (CAPAResponse) | UI type (`qms.ts`) | Status |
|-----------|---------------------------|--------------------|--------|
| `priority` (UI) | `severity` | `priority` in `CAPA` interface | ❌ **mismatch** |
| `actions[]` | separate endpoints | not in list DTO | **Partial** |

### 7.4 Equipment

| Doc / UX | API | FE `Equipment` | Status |
|----------|-----|----------------|--------|
| `next_calibration_due` | `next_calibration_date` | `next_calibration` | ⚠️ **naming drift** |

### 7.5 Audit trail (immutable)

Master: append-only `AuditTrailRecord` with `before_value` / `after_value`.  
Code: `PlatformAuditLog` with `metadata` JSON and **no** `before_value`/`after_value` columns in model shown — **schema mismatch** vs ALCOA+ narrative unless stored inside `metadata`.

---

## 8. Roles, Permissions & UI Guards

| Aspect | Documentation | Code (evidence) | Gap |
|---------|----------------|-----------------|-----|
| Role names | Quality Manager, Section Head, Analyst, … | `usePermission.ts`: `super_admin`, `tenant_admin`, `tenant_user`, `company_admin`, `company_user` | **Different model** — platform multi-tenant roles, not QMS lab roles |
| Permission strings | Not enumerated per API in master doc | Fine-grained strings (`document:approve`, `capa:write`, …) | Good for dev; **not mapped** to master’s 8 roles |
| API enforcement | RBAC at gateway + service | `CurrentUser` dependency in services | Partial — verify each route checks permission scopes |
| UI | Role-aware screens | Sidebar + `usePermission` | **Partial** — does not implement master’s Section Head / Auditor / QM matrix |

---

## 9. Workflow Implementation Mapping (9 vs Code)

| Workflow (doc) | Backend logic located? | FE actions | Events (Kafka doc §7.3) |
|----------------|------------------------|------------|-------------------------|
| 4.1 Document lifecycle | **Partial** — submit/approve/reject/effective paths in `document-service` | Document pages | **Not evidenced** publish from QMS |
| 4.2 CAPA | **Partial** — state fields + close/effectiveness/actions | List; **no** full wizard | **Missing** cross-service |
| 4.3 Internal audit | **No** QMS audit aggregate | **No** | N/A |
| 4.4 Calibration | **Partial** — `record_calibration` endpoint | Limited UI | **Missing** auto quality-event on fail (doc) |
| 4.5 NC work | Partially overlaps quality-event | **No** dedicated NC flow | N/A |
| 4.6 Supplier | **No** | **No** | N/A |
| 4.7 Complaint | **No** | **No** | N/A |
| 4.8 Management review | **No** | **No** | N/A |
| 4.9 Env excursion | **No** | **No** | N/A |

---

## 10. Integrations & Platform Dependencies (Evidence Table)

| Integration | Master doc | Observed in repo |
|-------------|------------|------------------|
| PostgreSQL | ✅ | ✅ per-service DB configs |
| Redis | ✅ | Shared `rainer_cache` (per GAPS / shared lib) |
| Kafka | ✅ | `rainer_events`, audit Kafka tests |
| S3 | ✅ | `boto3` in `file-service`, image/reporting configs (MinIO defaults) |
| OpenSearch | ✅ | Infra/compose references; **no search microservice** |
| Keycloak | ✅ | **Not found** in auth-service code |
| Temporal | ✅ | **Not found** |
| Kong / API GW | Kong mentioned | **FastAPI `gateway-service`** |
| Notifications | ✅ | `notification-service` + gateway proxy |
| AI | ✅ | `em/ai-service` (product-scoped) |
| LIMS / ERP | ✅ future | **Not evidenced** as connectors in `backend/qms` |

---

## 11. Compliance, Audit Trail & Electronic Signatures

| Requirement (master §7–8) | Implementation evidence | Gap |
|---------------------------|-------------------------|-----|
| ALCOA+ / immutable audit | `PlatformAuditLog` append-style table; Kafka ingestion path in audit tests | Field-level before/after not in model snippet; **gap** vs doc’s `before_value`/`after_value` |
| 21 CFR Part 11 e-sign | Document approve takes `signature` string | **Partial** — needs security design review (password re-entry, meaning, hash link) vs master §8.4 |
| ISO clause mapping | Doc: `iso_clause_mapping` on documents | JSON metadata possible; **not verified** in UI/API |
| Tenant isolation | `tenant_id` on models + `X-Tenant-ID` / JWT | ✅ pattern present |

---

## 12. Prioritized Gap Resolution Summary

This section consolidates: **mocks / env / hard-coding**, **code not represented in the QMS master doc**, the **sequential binding plan** for all 14 modules, and the **severity × effort** backlog.

### 12.1 Mocks, hard-coded values & placeholder environment

| Item | Location / pattern | Risk |
|------|-------------------|------|
| Default MinIO/S3 creds | `file-service` / `image-service` config defaults | **High** if used beyond local dev |
| `NEXT_PUBLIC_API_URL` default `localhost:8000` | `client.ts`, `qms-client.ts` | Misroutes QMS calls to gateway without proxies |
| UI status labels | CAPA page `STATUS_CONFIG` object | Hard-coded labels (acceptable for MVP if moved to constants per org rules) |
| `GAPS.md` “all resolved” | Root | **Process risk** — contradicts live binding issues found above |

**Suggested env checklist (non-exhaustive):** `NEXT_PUBLIC_QMS_DOCUMENT_API_URL`, `NEXT_PUBLIC_QMS_QUALITY_EVENT_API_URL`, `NEXT_PUBLIC_QMS_CAPA_API_URL`, `NEXT_PUBLIC_QMS_TRAINING_API_URL`, `NEXT_PUBLIC_QMS_EQUIPMENT_API_URL`, `NEXT_PUBLIC_API_URL`, service DB URLs, Kafka brokers, JWT secrets, S3 keys.

### 12.2 Code-not-in-documentation inventory

| Area | Path / product | Note |
|------|----------------|------|
| EndGameBiotech | `backend/em/*`, `frontend/.../(em)/` | Plate imaging, jobs, QA review — **separate product** |
| RainerCCV | `backend/ccv/*`, gateway CCV proxies | CRM, contracts, work orders, billing, technicians |
| Multi-product shell | `README.md`, sidebar | User-facing **portal** beyond QMS-only doc |
| Super-admin / tenant admin | `app/(admin)`, `app/(auth)/super-admin` | **Platform ops** not in QMS master |

### 12.3 Sequential binding plan (all 14 modules) — tasks & test checklists

**Phase A — Fix transport & contracts (blocking)**

| Step | Tasks | Test checklist |
|------|-------|----------------|
| A1 | Add gateway proxies OR change defaults so **all** QMS browsers hit correct origins consistently | E2E: load each QMS page with **only** `NEXT_PUBLIC_API_URL` set; network tab shows **200** for list APIs |
| A2 | Align `qms.ts` paths: `/capas`, `/equipment`, remove `/capa/...` and `/equipment/assets` | Unit/integration: contract test against OpenAPI |
| A3 | Align CAPA mutations with backend (`PATCH`, `POST /close`, actions) or add backend `transition` shim | State machine test: create → investigate → … → closed |
| A4 | Normalize CAPA/equipment paginated responses like documents/quality-events | Assert `total`, `page` match backend `pagination` |
| A5 | Add **analytics** proxy to gateway or route `analyticsApi` to dedicated base URL | Dashboard/KPI page returns data |

**Phase B — Modules 1–6 depth (MVP parity)**

| Module | Tasks | Tests |
|--------|-------|-------|
| 1 Document | Wire reject, versions, due-for-review if in scope | UI + API integration |
| 2 Quality event | Close + delete + summary dashboard | API + UI |
| 3 CAPA | Full lifecycle UI + permissions | RBAC matrix from `usePermission` |
| 4 Audit (QMS) | **New service** or rename platform audit for clarity | N/A until scoped |
| 5 Training | Assignment flows from doc §4.1 trigger | Event or polling integration test |
| 6 Equipment | Calibrate + decommission UI; OOT → quality event (per doc) | Integration |

**Phase C — Modules 7–14 (new services)**

For each of envmon, supplier, risk, PT, complaints, management-review, extended analytics/lab features: scaffold service, DB schema, gateway route, FE shell, and Kafka contracts per master §7.3.

### 12.4 Prioritized gaps (Critical / High / Medium / Low) with effort S / M / L / XL

| ID | Gap | Severity | Effort | Owner suggestion |
|----|-----|----------|--------|-------------------|
| G1 | Nine QMS modules (and QMS audit) **missing** | **Critical** | **XL** | Architecture + product |
| G2 | Gateway **missing** QMS + analytics proxies; default env misroutes | **Critical** | **M** | Platform |
| G3 | FE CAPA/equipment **wrong paths**; CAPA `transition` orphan | **Critical** | **S** | Full-stack |
| G4 | CAPA **priority vs severity** + pagination envelope inconsistencies | **High** | **S** | Frontend |
| G5 | Master stack (Nest/Prisma/Keycloak/Temporal) ≠ actual stack | **High** | **L** | Documentation |
| G6 | Kafka **documented** cross-service flows **not implemented** in QMS | **High** | **L** | Backend |
| G7 | Analytics UI → gateway **404** | **High** | **S** | Platform |
| G8 | Immutable audit trail **shape** differs from master fields | **Medium** | **M** | Compliance engineering |
| G9 | Roles: master lab roles vs platform roles | **Medium** | **L** | Product + auth |
| G10 | OpenSearch **service** absent | **Medium** | **XL** | Search team |
| G11 | EM/CCV **undocumented** in QMS master | **Low** (for QMS doc) | **M** | Technical writing |

---

*End of report.*
