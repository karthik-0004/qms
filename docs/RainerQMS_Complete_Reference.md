# RainerQMS — Complete System Reference

> **Document Purpose:** A comprehensive, single-source reference covering all 14 RainerQMS modules, their specification, implementation status, entity fields, state machines, API endpoints, user roles, workflows, and cross-module integrations. This document synthesizes three prior analyses:
> - `01_Spec_vs_Industry.md` — Spec-to-industry comparison
> - `02_Code_vs_Industry.md` — Code-to-industry comparison (legacy, based on earlier codebase state)
> - `03_Module_Workflows.md` — Module-by-module workflow walkthrough
> 
> It then reconciles these against the **actual codebase** (as of May 2026) to show exactly what is spec'd, what is built, and what gaps remain.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Architecture Overview](#2-architecture-overview)
3. [Module-by-Module Reference](#3-module-by-module-reference)
   - M1: Document Control
   - M2: Quality Event Management
   - M3: CAPA Management
   - M4: Audit Management
   - M5: Training & Competency
   - M6: Equipment & Calibration
   - M7: Environmental Monitoring
   - M8: Supplier Quality
   - M9: Risk Management
   - M10: Proficiency Testing (PT)
   - M11: Customer Complaint Management
   - M12: Management Review
   - M13: Reporting & Analytics
   - M14: Lab-Specific Features
4. [User Roles & Permissions](#4-user-roles--permissions)
5. [Cross-Module Event Flows](#5-cross-module-event-flows)
6. [Platform Services](#6-platform-services)
7. [Gaps & Issues Registry](#7-gaps--issues-registry)
8. [Frontend Implementation](#8-frontend-implementation)
   8.1 [Tech Stack](#81-tech-stack)
   8.2 [Route Structure](#82-route-structure)
   8.3 [Component Architecture](#83-component-architecture)
   8.4 [QMS Page-by-Page UI Binding](#84-qms-page-by-page-ui-binding)
   8.5 [API Client Architecture](#85-api-client-architecture)
   8.6 [Auth & State Management](#86-auth--state-management)
   8.7 [Frontend–Backend Data Flow](#87-frontendbackend-data-flow)
   8.8 [Frontend Gaps & Missing Features](#88-frontend-gaps--missing-features)
9. [Glossary](#9-glossary)

---

## 1. Executive Summary

### 1.1 Implementation Status Overview

| Module | Spec Status | Code Status | Endpoints | Tests |
|--------|------------|-------------|-----------|-------|
| M1: Document Control | ✅ Complete | ✅ Full | 13 | 14 E2E + 8 unit |
| M2: Quality Events | ✅ Complete | ✅ Full | 7 | 1 unit (109 lines) |
| M3: CAPA | ✅ Complete | ✅ Full | 11 | 1 unit (110 lines) |
| M4: Audit | ✅ Complete | 🔴 Not started | 0 | 0 |
| M5: Training | ✅ Complete | ✅ Full | 9 | 1 unit (138 lines) |
| M6: Equipment & Cal | ✅ Complete | ✅ Full | 10 | 1 unit (178 lines) |
| M7: Environmental Monitoring | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M8: Supplier Quality | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M9: Risk Management | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M10: Proficiency Testing | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M11: Customer Complaints | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M12: Management Review | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M13: Reporting & Analytics | ✅ Spec'd | 🔴 Not started | 0 | 0 |
| M14: Lab-Specific Features | ⚠️ Partial spec | 🔴 Not started | 0 | 0 |
| **Platform Services** | — | — | — | — |
| Workflow Engine | ✅ Spec'd | ✅ Full | 10 | 1 unit (211 lines) |
| Auth Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Tenant Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| User Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Audit Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Notification Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| File Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Gateway Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Schedule Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Reporting Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |
| Analytics Service | ✅ Spec'd | 🔴 Stub only | 0 | 0 |

**Legend:** ✅ = Completed | ⚠️ = Partial | 🔴 = Not started / stub only

### 1.2 Cross-Cutting Gaps

| Gap | Severity |
|-----|----------|
| No Kafka event publishing wired in any domain service | Critical |
| No service-to-service HTTP calls (all URLs configured, none used) | Critical |
| No file upload/download endpoints | High |
| No notification delivery (email, in-app) | High |
| No audit trail emission (21 CFR Part 11 non-compliant) | High |
| No document acknowledgment workflow (dead code: table + model, no API) | High |
| Missing `Effective` and `Superseded` states for document lifecycle | High |
| No RBAC role→permission mapping enforced at auth middleware (all users have same `tenant_id` JWT claims) | High |
| Missing modules: Audit, Supplier, Risk, PT, Complaint, Management Review, Reporting, Environmental Monitoring | High |
| No scheduler service for periodic review / calibration reminders | Medium |
| Shared lib `rainer_events` producer code exists but is **imported nowhere** in any QMS service | Medium |

---

## 2. Architecture Overview

### 2.1 Technology Stack

| Component | Specified | Implemented |
|-----------|-----------|-------------|
| **Language** | Python 3.12 | ✅ Python 3.12 |
| **Web Framework** | FastAPI | ✅ FastAPI |
| **ORM** | SQLAlchemy 2.0 (async) | ✅ SQLAlchemy 2.0 + asyncpg |
| **Database** | Schema-per-tenant Postgres | ✅ Master DB + per-tenant DB in `rainer_tenant_lib` |
| **Cache** | Redis | ✅ `rainer_cache` with async Redis |
| **Event Bus** | Kafka | ✅ `rainer_events` producer (unused) |
| **Workflow Engine** | Temporal | 🔴 Not wired; custom workflow-engine service instead |
| **Search** | OpenSearch | 🔴 Not started |
| **Auth** | JWT + Keycloak | ⚠️ JWT consumed; Keycloak not deployed |
| **Monitoring** | Prometheus, Grafana | ✅ infra configs present |
| **Logging** | ELK / Loki | ✅ Loki + Promtail configured |
| **Frontend** | Next.js (TypeScript) | ✅ 5 module pages built |
| **Containers** | Docker / Docker Compose | ✅ 8 compose files |
| **Orchestration** | Kubernetes | ✅ Helm charts in `infra/helm/` |

### 2.2 Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Gateway (stub)                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌───────────┐  ┌──────────┐  ┌────────┐  ┌───────────┐    │
│  │   Auth    │  │  Tenant  │  │  User  │  │  Config   │    │
│  │  Service  │  │  Service │  │ Service│  │  Service  │    │
│  │  (stub)   │  │  (stub)  │  │ (stub) │  │  (stub)   │    │
│  └───────────┘  └──────────┘  └────────┘  └───────────┘    │
│                                                              │
│  ┌─────────────┐  ┌──────────┐  ┌──────────────┐           │
│  │  Document   │  │ Quality  │  │    CAPA      │           │
│  │   Service   │  │  Event   │  │   Service    │           │
│  │    ✅       │  │ Service  │  │    ✅        │           │
│  └─────────────┘  │    ✅    │  └──────────────┘           │
│                   └──────────┘                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Training   │  │  Equipment  │  │ Workflow    │         │
│  │   Service   │  │   Service   │  │   Engine    │         │
│  │    ✅       │  │    ✅       │  │    ✅       │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  ┌──────────┐  ┌──────────────┐  ┌──────────┐              │
│  │  Audit   │  │ Notification │  │   File   │              │
│  │ Service  │  │   Service    │  │  Service │              │
│  │ (stub)   │  │   (stub)     │  │  (stub)  │              │
│  └──────────┘  └──────────────┘  └──────────┘              │
│                                                              │
│  ┌──────────────┐  ┌────────────────┐                       │
│  │  Reporting   │  │  Analytics     │                       │
│  │   Service    │  │   Service      │                       │
│  │   (stub)     │  │   (stub)       │                       │
│  └──────────────┘  └────────────────┘                       │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│                   Shared Libraries (✅ all)                   │
│  rainer_common  |  rainer_auth_lib  |  rainer_events        │
│  rainer_cache   |  rainer_tenant_lib                         │
└─────────────────────────────────────────────────────────────┘
```

### 2.3 Data Architecture

**Shared Kernel DB** (master database, one per deployment):
- Tenant configuration and provisioning data
- Cross-tenant reference data

**Per-Tenant DB** (one schema per tenant, all service tables co-located):
- `documents`, `document_versions`, `document_acknowledgments`, `document_distribution`
- `quality_events`
- `capas`, `capa_actions`
- `training_courses`, `training_assignments`
- `equipment`, `calibration_records`
- `workflow_definitions`, `workflow_instances`, `workflow_history`

**Redis**: Per-service caching, rate limiting

**Kafka Topics** (defined but no services publish to them):
- `rainer.document.events` — `rainer.{aggregate_type}.events` pattern

---

## 3. Module-by-Module Reference

### M1: Document Control

#### Purpose
Single source of truth for all controlled documents (SOPs, Work Instructions, Methods, Policies, Forms, Manuals). Ensures documents go through draft → review → approval → effective lifecycle with e-signatures, version control, and distribution acknowledgment.

#### Roles Involved
| Role | What they do |
|------|-------------|
| Author (Analyst/Section Head) | Writes new documents or revisions |
| Reviewer (peer Section Head) | Reads draft, suggests changes or approves review |
| Approver (Quality Manager / Lab Director) | Final sign-off with e-signature |
| Distribution List Members | Must read and acknowledge new effective documents |
| Document Owner (Section Head) | Maintains the document, handles periodic review |

#### Entity Fields

**Document (`documents` table)**

| Field | Type | Spec'd | In Code | Notes |
|-------|------|--------|---------|-------|
| id | UUID PK | ✅ | ✅ | |
| tenant_id | UUID FK | ✅ | ✅ | |
| doc_number | String(50) | ✅ | ✅ | Format: `DOC-YYYYMMDD-{random}` |
| title | String(255) | ✅ | ✅ | |
| doc_type | String(100) | ✅ | ✅ | SOP, WI, Method, Policy, Form, Manual, External |
| department | String(100) | ✅ | ✅ | |
| description | Text | ✅ | ✅ | |
| status | String(50) | ✅ | ✅ | draft / under_review / approved / obsolete |
| current_version | String(20) | ✅ | ✅ | Default "1.0" |
| owner_id | UUID | ✅ | ✅ | |
| approver_id | UUID | ✅ | ⚠️ | Single approver only; no multi-approver |
| effective_date | DateTime | ✅ | ✅ | |
| review_date | DateTime | ✅ | ✅ | |
| expiry_date | DateTime | ✅ | ✅ | |
| workflow_instance_id | UUID | ✅ | ✅ | Config exists, never populated |
| file_id | UUID | ✅ | ✅ | Stored but no upload/download |
| tags | JSONB | ✅ | ✅ | |
| metadata | JSONB | ✅ | ✅ | |
| regulatory_frameworks | JSONB | ✅ | ✅ | ISO 17025, ISO 15189, etc. |
| is_controlled | Boolean | ✅ | ✅ | Default true |
| created_by | UUID | ✅ | ✅ | |
| created_at | DateTime | ✅ | ✅ | |
| updated_at | DateTime | ✅ | ✅ | |
| deleted_at | DateTime | ✅ | ✅ | Soft delete |
| last_rejection_reason | Text | ✅ | ✅ | In DB + ORM |
| vault | String | 🔴 Spec gap | 🔴 | Not in code (QA-rel / QA-dft / Course Release) |
| taxonomy_id / folder_id | UUID | 🔴 Spec gap | 🔴 | Not in code |
| change_summary | Text | ✅ | ⚠️ | In DB but on `document_versions`, not `documents` |
| retention_period | Integer | ✅ | 🔴 | Not in code |
| iso_clause_mapping | JSONB | ✅ | 🔴 | Not in code |
| lifecycle_name | String | 🔴 Spec gap | 🔴 | MasterControl pattern |

**DocumentVersion (`document_versions` table)**

| Field | Type | In Code |
|-------|------|---------|
| id | UUID PK | ✅ |
| document_id | UUID FK | ✅ |
| version | String(20) | ✅ |
| file_id | UUID | ✅ |
| change_summary | Text | ✅ |
| approved_by | UUID | ✅ |
| approved_at | DateTime | ✅ |
| signature_hash | String(255) | ✅ SHA-256 |
| created_by | UUID | ✅ |
| created_at | DateTime | ✅ |

**DocumentAcknowledgment (`document_acknowledgments` table)**

| Field | Type | In Code | Notes |
|-------|------|---------|-------|
| id | UUID PK | ✅ | |
| document_id | UUID | ✅ | No FK constraint |
| user_id | UUID | ✅ | |
| acknowledged_at | DateTime | ✅ | |
| version | String(20) | ✅ | |
| ip_address | String(50) | ✅ | |

**⚠️ Dead code**: Table + model exist but **no API, no service, no repository**. Cannot create acknowledgments.

**DocumentDistribution (`document_distribution` table)**

| Field | Type | In Code |
|-------|------|---------|
| id | UUID PK | ✅ |
| document_id | UUID FK | ✅ |
| user_id | UUID | ✅ |
| added_by | UUID | ✅ |
| created_at | DateTime | ✅ |

#### State Machine

```
Spec: draft → under_review → approved → effective → superseded → obsolete
Code: draft → under_review → approved → obsolete
                                ↓
                          (dead) create_new_version → (no handler)
```

**Missing states (industry-standard):**
- `Effective` — Between Approved and Superseded
- `Superseded` — When new version replaces old
- The `create_new_version` transition is defined in `VALID_TRANSITIONS` but has **no handler method and no API endpoint** (dead code per D-2)

#### API Endpoints (13 implemented)

| Method | Path | Permission | Spec'd | Code |
|--------|------|-----------|--------|------|
| GET | `/documents` | DOCUMENT_READ | ✅ | ✅ |
| GET | `/documents/due-for-review` | DOCUMENT_READ | ✅ | ✅ |
| POST | `/documents` | DOCUMENT_WRITE | ✅ | ✅ |
| GET | `/{document_id}` | DOCUMENT_READ | ✅ | ✅ |
| PATCH | `/{document_id}` | DOCUMENT_WRITE | ✅ | ✅ |
| DELETE | `/{document_id}` | DOCUMENT_DELETE | ✅ | ✅ |
| POST | `/{id}/submit-for-review` | DOCUMENT_WRITE | ✅ | ✅ |
| POST | `/{id}/approve` | DOCUMENT_APPROVE | ✅ | ✅ |
| POST | `/{id}/reject` | DOCUMENT_APPROVE | ✅ | ✅ |
| POST | `/{id}/make-obsolete` | DOCUMENT_APPROVE | ✅ | ✅ |
| GET | `/{id}/versions` | DOCUMENT_READ | ✅ | ✅ |
| GET | `/{id}/distribution` | DOCUMENT_READ | ✅ | ✅ |
| POST | `/{id}/distribution` | DOCUMENT_WRITE | ✅ | ✅ |

**Missing endpoints (vs spec):**
- `POST /{id}/acknowledge` — No endpoint for acknowledgment (dead code)
- `POST /{id}/versions` — No create_new_version handler
- `POST /{id}/effective` — No transition to Effective state
- File upload/download — No endpoints
- Document search — No search endpoint

#### Workflow Steps (Spec)

1. **Create** — Author fills title, type, uploads file, selects folder, picks approver, distribution list
2. **Submit for Review** — Status → Under Review; reviewers notified
3. **Review** — Reviewer approves review OR requests changes
4. **Approve** — Approver e-signs with re-auth, meaning declaration, SHA-256 hash
5. **Effective** — Auto on effective_date; previous version → Superseded
6. **Training auto-triggers** — Distribution list members assigned training
7. **Acknowledge** — Each member reads and acknowledges
8. **Periodic Review** — 30/14/7 day reminders; owner confirms current or initiates revision

**Code coverage of workflow steps:**
- ✅ Step 1 (Create) — implemented
- ✅ Step 2 (Submit for Review) — implemented
- ⚠️ Step 3 (Review) — No reviewer workflow (single approver, no reviewer separation)
- ✅ Step 4 (Approve) — implemented with SHA-256 hash
- 🔴 Step 5 (Effective) — Not implemented; no Effective state
- 🔴 Step 6 (Training trigger) — Not wired (no Kafka event)
- 🔴 Step 7 (Acknowledge) — Dead code
- ⚠️ Step 8 (Periodic Review) — Query endpoint exists; no scheduler/notifications

---

### M2: Quality Event Management

#### Purpose
The "something went wrong" system. Analysts report problems (OOS, deviation, non-conformance), system classifies severity, triggers investigation, and escalates systemic issues to CAPA.

#### Roles Involved
| Role | What they do |
|------|-------------|
| Reporter (Analyst/Section Head) | Files the initial report |
| Section Head | Decides immediate action |
| Investigator | Does root cause analysis |
| Quality Manager | Reviews findings, decides CAPA escalation |
| Affected Personnel | People whose work may be impacted |
| Client (external) | Notified if results were affected |

#### Entity Fields

**QualityEvent (`quality_events` table)**

| Field | Type | Spec'd | Code |
|-------|------|--------|------|
| id | UUID PK | ✅ | ✅ |
| tenant_id | UUID | ✅ | ✅ |
| event_number | String(50) | ✅ | ✅ |
| title | String(255) | ✅ | ✅ |
| event_type | String(100) | ✅ | ✅ Deviation/NC/OOS/OOT/NC Work |
| description | Text | ✅ | ✅ |
| status | String(50) | ✅ | ✅ open/under_investigation/resolved/closed |
| severity | String(50) | ✅ | ✅ Critical/Major/Minor |
| priority | String(20) | ✅ | ✅ High/Medium/Low |
| department | String(100) | ✅ | ✅ |
| location | String(255) | ✅ | ✅ |
| detected_at | DateTime | ✅ | ✅ |
| detected_by | UUID | ✅ | ✅ |
| assigned_to | UUID | ✅ | ✅ |
| root_cause | Text | ✅ | ✅ |
| immediate_action | Text | ✅ | ✅ |
| capa_required | Boolean | ✅ | ✅ |
| capa_id | UUID | ✅ | ✅ |
| due_date | DateTime | ✅ | ✅ |
| closed_at | DateTime | ✅ | ✅ |
| tags | JSONB | ✅ | ✅ |
| attachments | JSONB | ✅ | ✅ |
| metadata | JSONB | ✅ | ✅ |
| created_by | UUID | ✅ | ✅ |
| created_at | DateTime | ✅ | ✅ |
| updated_at | DateTime | ✅ | ✅ |
| deleted_at | DateTime | ✅ | ✅ |

**Missing fields (vs spec):**
- `client_notified` Boolean — Not in code (spec says "Client notification flag `client_notified` boolean")
- Linked entity fields (linked_equipment, linked_document, linked_personnel) — Not explicit in model (stored in `metadata` JSONB)
- `root_cause_method` / `rca_tools` — Not in model
- `event_type` sub-typing → Non-Conforming Work as separate type with specific fields

#### State Machine

```
open ──investigate──> under_investigation ──resolve──> resolved ──close──> closed
  │                                                        ↑
  └──────────close──────────────────────────────────────────┘
                                                                 open <──reopen──┘
```

#### API Endpoints (7 implemented)

| Method | Path | Permission | Code |
|--------|------|-----------|------|
| GET | `/quality-events` | QUALITY_EVENT_READ | ✅ |
| POST | `/quality-events` | QUALITY_EVENT_WRITE | ✅ |
| GET | `/quality-events/summary` | QUALITY_EVENT_READ | ✅ |
| GET | `/{event_id}` | QUALITY_EVENT_READ | ✅ |
| PATCH | `/{event_id}` | QUALITY_EVENT_WRITE | ✅ |
| POST | `/{event_id}/close` | QUALITY_EVENT_WRITE | ✅ |
| DELETE | `/{event_id}` | QUALITY_EVENT_WRITE | ✅ |

**Missing endpoints (vs spec):**
- No `investigate` / `resolve` / `reopen` action endpoints (state transitions not exposed as separate endpoints)
- No Event Analyzer cross-event matching endpoint
- No Forms-Based System (FBS) multi-tab endpoint

#### Workflow Steps (Spec)

1. **Report** — Analyst fills description, type, severity, linked items
2. **Immediate Action** — Section Head decides (halt/quarantine/continue)
3. **Triage** — QM confirms severity; Critical → auto-CAPA
4. **Investigate** — RCA tools (5-Why, Fishbone, Fault Tree, Pareto)
5. **Review** — QM approves investigation + decides CAPA
6. **Escalate or Close** — Systemic → CAPA; One-off → Close locally
7. **Client Notification** — If affected results were reported
8. **Close** — QM e-signs closure

**Code coverage:**
- ✅ Create event with severity, type, description
- ⚠️ Update event (free-form `**fields`, no structured investigation workflow)
- ✅ Close event
- 🔴 No severity-based auto-CAPA trigger
- 🔴 No RCA tools (5-Why, Fishbone, etc.)
- 🔴 No Event Analyzer
- 🔴 No cross-module integration (Kafka not wired)

---

### M3: CAPA Management

#### Purpose
Corrective Action / Preventive Action. Permanently fixes systemic problems through investigation → action planning → implementation → effectiveness verification.

#### Roles Involved
| Role | What they do |
|------|-------------|
| CAPA Initiator | Triggers the CAPA (from QE, audit, complaint, etc.) |
| CAPA Owner | Accountable for getting it closed |
| Action Owners | Execute individual action items |
| Investigators | Do root cause analysis |
| Quality Manager | Approves plan, verifies effectiveness, closes |
| Effectiveness Reviewer | Checks at 30/60/90 days |

#### Entity Fields

**CAPA (`capas` table)**

| Field | Type | Spec'd | Code |
|-------|------|--------|------|
| id | UUID PK | ✅ | ✅ |
| tenant_id | UUID | ✅ | ✅ |
| capa_number | String(50) | ✅ | ✅ |
| title | String(255) | ✅ | ✅ |
| capa_type | String(50) | ✅ | ✅ corrective/preventive/both |
| description | Text | ✅ | ✅ |
| status | String(50) | ✅ | ✅ (6 states) |
| severity | String(50) | ✅ | ✅ |
| root_cause | Text | ✅ | ✅ |
| root_cause_method | String(100) | ✅ | ✅ |
| source_type | String(100) | ✅ | ✅ Quality Event/Audit Finding/etc. |
| source_id | UUID | ✅ | ✅ |
| owner_id | UUID | ✅ | ✅ |
| department | String(100) | ✅ | ✅ |
| due_date | DateTime | ✅ | ✅ |
| target_close_date | DateTime | ✅ | ✅ |
| actual_close_date | DateTime | ✅ | ✅ |
| effectiveness_check_date | DateTime | ✅ | ✅ |
| effectiveness_verified | Boolean | ✅ | ✅ |
| workflow_instance_id | UUID | ✅ | ✅ |
| tags | JSONB | ✅ | ✅ |
| attachments | JSONB | ✅ | ✅ |
| created_by | UUID | ✅ | ✅ |
| created_at | DateTime | ✅ | ✅ |
| updated_at | DateTime | ✅ | ✅ |
| deleted_at | DateTime | ✅ | ✅ |

**Missing fields (vs spec):**
- Risk scoring fields: `risk_severity`, `risk_occurrence`, `risk_detectability`, `rpn_score` (3-factor RPN model from spec)
- `recurrence_monitoring_active` — Boolean for post-closure monitoring
- `closed_by` — Who closed it
- `effectiveness_results` — Details of verification

**CAPAAction (`capa_actions` table)**

| Field | Type | Code |
|-------|------|------|
| id | UUID PK | ✅ |
| capa_id | UUID FK | ✅ |
| action_type | String(50) | ✅ Corrective/Preventive |
| description | Text | ✅ |
| assigned_to | UUID | ✅ |
| due_date | DateTime | ✅ |
| completed_at | DateTime | ✅ |
| status | String(50) | ✅ pending/completed |
| evidence | Text | ✅ |
| created_at | DateTime | ✅ |
| updated_at | DateTime | ✅ |

**Missing action fields (vs spec):**
- `expected_outcome` — Not present
- `sign_off` / `approved_by` — Not captured
- Action escalation tracking (7/14/30 day overdue escalations)

#### State Machine (Code)

```
open ──start_investigation──> under_investigation
  │                                  │
  │                    identify_root_cause
  │                                  │
  │                                  ▼
  │                    root_cause_identified
  │                                  │
  │                    implement_actions
  │                                  │
  │                                  ▼
  │                    implementation ──close──> closed
  │                                  │
  │                    verify_effectiveness
  │                                  │
  │                                  ▼
  │                    effectiveness_check ──close──> closed
  │                                        ↑
  └──────────────────────reopen────────────┘
```

**Spec vs Code state comparison:**
- Spec: Identification → Investigation → Action Planning → Implementation → Effectiveness Check → Closure
- Code: open → under_investigation → root_cause_identified → implementation → effectiveness_check → closed

**Difference:** Code has `root_cause_identified` between investigation and implementation (more granular). Code lacks explicit `Action Planning` state (actions are added ad-hoc). Code allows closing directly from `implementation` without effectiveness check.

#### API Endpoints (11 implemented)

| Method | Path | Permission | Code |
|--------|------|-----------|------|
| GET | `/capas` | CAPA_READ | ✅ |
| POST | `/capas` | CAPA_WRITE | ✅ |
| GET | `/{capa_id}` | CAPA_READ | ✅ |
| PATCH | `/{capa_id}` | CAPA_WRITE | ✅ |
| POST | `/{capa_id}/close` | CAPA_APPROVE | ✅ |
| POST | `/{capa_id}/verify-effectiveness` | CAPA_APPROVE | ✅ |
| GET | `/{capa_id}/actions` | CAPA_READ | ✅ |
| POST | `/{capa_id}/actions` | CAPA_WRITE | ✅ |
| POST | `/{capa_id}/actions/{action_id}/complete` | CAPA_WRITE | ✅ |

**Missing endpoints (vs spec):**
- No `start_investigation`, `identify_root_cause`, `implement_actions`, `reopen` endpoints
- No analytics/dashboard endpoints (CAPA by Department, etc.)
- No escalation/overdue-tracking endpoint

#### Workflow Steps (Spec)

1. **Identification** — CAPA created from source (QE, audit finding, complaint, etc.)
2. **Investigation** — RCA with tools; AI suggests causes (Phase 3)
3. **Action Planning** — Define actions with owners, due dates, expected outcomes
4. **QM Approve Plan** — E-signs the action plan
5. **Implementation** — Action owners execute; evidence uploaded
6. **Effectiveness Check** — 30/60/90 day verification
7. **Close** — QM final e-signature; recurrence monitoring begins

**Code coverage:**
- ✅ Create CAPA with source linking
- ✅ Add actions with owners, due dates
- ✅ Complete actions with evidence
- ✅ Verify effectiveness (pass/fail)
- ✅ Close CAPA
- 🔴 No automatic escalation at 7/14/30 days
- 🔴 No AI root cause suggestion
- 🔴 No recurrence monitoring
- 🔴 No effectiveness scheduling
- 🔴 No auto-create CAPA from other services (no Kafka)

---

### M4: Audit Management

**Status: 🔴 Not started — 0% implemented**

#### Purpose
Manages internal audits, external accreditation audits, supplier audits, and regulatory inspections. Includes annual planning, checklist execution, finding classification, and auto-CAPA creation.

#### Roles Involved
| Role | What they do |
|------|-------------|
| Audit Program Manager | Plans annual schedule |
| Lead Auditor | Plans/executes specific audit |
| Auditor(s) | Assist Lead Auditor |
| Auditee | Provides evidence, responds to findings |
| Quality Manager | Approves program, oversees findings→CAPA |

#### Spec-Defined Fields (not in code)

**Audit record:**
| Field | Example |
|-------|---------|
| Audit ID | AUD-2026-0011 |
| Audit Type | Internal / External / Supplier / Regulatory |
| Scope | "Microbiology Section" |
| Criteria | ISO 17025:2017 |
| Lead Auditor | Julie Cook |
| Auditors[] | Sarah Chen, Mark Dombrro |
| Auditee | Rajesh Patel |
| Scheduled Date | 13 Mar 2026 |
| Performed Date | 14 Mar 2026 |
| Checklist ID | CHK-ISO17025-001 |
| Findings[] | Major NC / Minor NC / Observation / OFI |
| Status | Planned / In Progress / Reporting / Auditee Response / Follow-Up / Closed |
| Audit Report | Auto-generated PDF |

**Audit Finding:**
| Field | Example |
|-------|---------|
| Finding ID | FND-2026-0034 |
| Classification | Major NC / Minor NC / Observation / OFI |
| ISO Clause | 6.4.5 |
| CAPA ID | (auto-linked) |

#### Workflow Steps (Spec)

1. **Annual Plan** — QM drags audits onto calendar
2. **Preparation** — Lead Auditor selects checklist, notifies auditee
3. **Execution** — Opening meeting → Walk checklist → Record findings → Closing meeting
4. **Report** — Auto-generated PDF; findings with Major/Minor NC → auto-CAPA
5. **Auditee Response** — Response for each finding
6. **Follow-up** — Track CAPAs to closure
7. **Program Review** — Annual effectiveness review

**Nothing is implemented.** No Audit service folder exists under `backend/qms/`.

---

### M5: Training & Competency

**Status: ✅ Implemented**

#### Purpose
Ensures every employee is trained on relevant documents/procedures, passes assessments, and competency is on record for auditors.

#### Roles Involved
| Role | What they do |
|------|-------------|
| Trainee | Any employee assigned training |
| Trainer | Delivers training |
| Supervisor (Section Head) | Verifies competence, signs off |
| Quality Manager | Owns training program |
| Tenant Admin | Sets up Job Codes and Courses |

#### Entity Fields

**TrainingCourse (`training_courses` table)**

| Field | Type | Spec'd | Code |
|-------|------|--------|------|
| id | UUID PK | ✅ | ✅ |
| tenant_id | UUID | ✅ | ✅ |
| course_code | String(50) | ✅ | ✅ |
| title | String(255) | ✅ | ✅ |
| description | Text | ✅ | ✅ |
| course_type | String(100) | ✅ | ✅ online/document/classroom |
| department | String(100) | ✅ | ✅ |
| document_id | UUID | ✅ | ✅ Links to Document |
| duration_hours | Float | ✅ | ✅ |
| passing_score | Integer | ✅ | ✅ Default 80 |
| requires_certification | Boolean | ✅ | ✅ |
| recurrence_days | Integer | ✅ | ✅ For recurring training |
| is_mandatory | Boolean | ✅ | ✅ |
| is_active | Boolean | ✅ | ✅ |
| created_by | UUID | ✅ | ✅ |
| created_at | DateTime | ✅ | ✅ |
| updated_at | DateTime | ✅ | ✅ |

**TrainingAssignment (`training_assignments` table)**

| Field | Type | Code |
|-------|------|------|
| id | UUID PK | ✅ |
| tenant_id | UUID | ✅ |
| course_id | UUID FK | ✅ |
| user_id | UUID | ✅ |
| assigned_by | UUID | ✅ |
| due_date | DateTime | ✅ |
| status | String(50) | ✅ assigned/in_progress/completed |
| score | Integer | ✅ |
| passed | Boolean | ✅ |
| completed_at | DateTime | ✅ |
| cert_expiry_date | DateTime | ✅ |
| notes | Text | ✅ |
| created_at | DateTime | ✅ |
| updated_at | DateTime | ✅ |

**⚠️ Spec gaps not in code:**
- **JobCode** entity — Not a separate entity in code (spec requires it)
- **JobCodeAssignment** — No user×jobcode linking
- **Trainer** — Not a distinct entity (spec says Trainer as separate role)
- **CourseClass** — No scheduled class instances
- Job Code Status matrix — No implementation
- 5-step training task UX — Not in API (single `complete` endpoint)

#### API Endpoints (9 implemented)

| Method | Path | Permission | Code |
|--------|------|-----------|------|
| GET | `/training/courses` | TRAINING_READ | ✅ |
| POST | `/training/courses` | TRAINING_WRITE | ✅ |
| GET | `/training/courses/{course_id}` | TRAINING_READ | ✅ |
| POST | `/training/courses/{course_id}/assign` | TRAINING_ASSIGN | ✅ |
| GET | `/training/assignments` | TRAINING_READ | ✅ |
| POST | `/training/assignments/{assignment_id}/complete` | TRAINING_WRITE | ✅ |
| GET | `/training/assignments/overdue` | TRAINING_READ | ✅ |

**Missing endpoints (vs spec):**
- No Job Code management endpoints
- No Job Code Status matrix endpoint
- No bulk import endpoint
- No trainer management endpoints
- No exam/question management endpoints
- No automatic assignment from document approval (no Kafka listener)

#### Workflow Steps (Spec)

1. **Auto-assigned** — Document Effective → Training auto-assigned to distribution list
2. **Open Task** — Trainee sees 5-step screen: Intro → Materials → Exam → Overview → Sign Off
3. **Read Materials** — Read document in-app
4. **Take Exam** — Auto-graded; pass/fail threshold
5. **Sign Off** — E-signature with timestamp
6. **Compliance Reporting** — Job Code Status matrix for auditors

**Code coverage:**
- ✅ Create courses
- ✅ Assign training to users (manual via API)
- ✅ Complete training with score, e-signature, pass/fail
- ✅ Get overdue assignments
- 🔴 No auto-assignment from document approval (no Kafka listener)
- 🔴 No 5-step training task UX (single `complete` endpoint)
- 🔴 No Job Codes
- 🔴 No Job Code Status matrix
- 🔴 No exam management (model has score/passing, no question bank)

---

### M6: Equipment & Calibration

**Status: ✅ Implemented**

#### Purpose
Tracks lab instruments from purchase to retirement, manages calibration schedules, and handles out-of-tolerance situations. This is RainerQMS's **biggest differentiator** vs. generic QMS products.

#### Roles Involved
| Role | What they do |
|------|-------------|
| Equipment Coordinator | Maintains equipment register |
| Calibration Technician | Performs calibrations |
| Qualified Reviewer | Reviews calibration results |
| Quality Manager | Handles OOT impact assessments |
| Analyst | Uses equipment, logs usage |

#### Entity Fields

**Equipment (`equipment` table)**

| Field | Type | Spec'd | Code |
|-------|------|--------|------|
| id | UUID PK | ✅ | ✅ |
| tenant_id | UUID | ✅ | ✅ |
| asset_tag | String(100) | ✅ | ✅ |
| name | String(255) | ✅ | ✅ |
| description | Text | ✅ | ✅ |
| equipment_type | String(100) | ✅ | ✅ |
| manufacturer | String(255) | ✅ | ✅ |
| model | String(255) | ✅ | ✅ |
| serial_number | String(100) | ✅ | ✅ |
| location | String(255) | ✅ | ✅ |
| department | String(100) | ✅ | ✅ |
| status | String(50) | ✅ | ✅ active/calibration_due/out_of_service/etc. |
| requires_calibration | Boolean | ✅ | ✅ |
| calibration_frequency_days | Integer | ✅ | ✅ |
| last_calibration_date | DateTime | ✅ | ✅ |
| next_calibration_date | DateTime | ✅ | ✅ |
| requires_pm | Boolean | ✅ | ✅ Preventive maintenance |
| pm_frequency_days | Integer | ✅ | ✅ |
| last_pm_date | DateTime | ✅ | ✅ |
| next_pm_date | DateTime | ✅ | ✅ |
| purchase_date | DateTime | ✅ | ✅ |
| warranty_expiry | DateTime | ✅ | ✅ |
| assigned_to | UUID | ✅ | ✅ |
| notes | Text | ✅ | ✅ |
| tags | JSONB | ✅ | ✅ |
| metadata | JSONB | ✅ | ✅ |
| created_by | UUID | ✅ | ✅ |
| created_at | DateTime | ✅ | ✅ |
| updated_at | DateTime | ✅ | ✅ |
| deleted_at | DateTime | ✅ | ✅ |

**CalibrationRecord (`calibration_records` table)**

| Field | Type | Code |
|-------|------|------|
| id | UUID PK | ✅ |
| equipment_id | UUID FK | ✅ |
| tenant_id | UUID | ✅ |
| calibration_date | DateTime | ✅ |
| performed_by | String(255) | ✅ |
| passed | Boolean | ✅ |
| standards_used | Text | ✅ |
| as_found_readings | Text | ✅ |
| as_left_readings | Text | ✅ |
| result | String(10) | ✅ Pass/Fail |
| measurement_uncertainty | String(100) | ✅ |
| notes | Text | ✅ |
| next_due_date | DateTime | ✅ |
| certificate_file_id | String(255) | ✅ |

**Missing fields (vs spec):**
- Usage-based calibration trigger (every N uses) — Not in model
- Digital usage logbook — No log entry model
- Standards traceability tree — No reference standard model
- Calibration certificate generation — No auto-PDF endpoint

#### API Endpoints (10 implemented)

| Method | Path | Permission | Code |
|--------|------|-----------|------|
| GET | `/equipment` | EQUIPMENT_READ | ✅ |
| POST | `/equipment` | EQUIPMENT_WRITE | ✅ |
| GET | `/equipment/due-for-calibration` | EQUIPMENT_READ | ✅ |
| GET | `/{equipment_id}` | EQUIPMENT_READ | ✅ |
| PATCH | `/{equipment_id}` | EQUIPMENT_WRITE | ✅ |
| POST | `/{equipment_id}/calibrate` | EQUIPMENT_WRITE | ✅ |
| POST | `/{equipment_id}/decommission` | EQUIPMENT_WRITE | ✅ |
| GET | `/{equipment_id}/calibrations` | EQUIPMENT_READ | ✅ |
| DELETE | `/{equipment_id}` | EQUIPMENT_WRITE | ✅ |

**Missing endpoints (vs spec):**
- No usage logbook endpoint
- No OOT→Quality Event auto-creation endpoint
- No calibration certificate generation/download endpoint

#### Workflow Steps (Spec)

1. **Scheduling** — Auto reminders at 30/14/7/1 days before calibration due
2. **Preparation** — Technician reviews SOP, verifies standards and environmental conditions
3. **Execution** — As-found readings → adjustment → as-left readings
4. **Review** — Qualified reviewer approves; Pass → return to service; Fail → OOT
5. **OOT Handling** — Quality Event auto-created, impact assessment, client notifications, possible CAPA
6. **Record** — Certificate generated, next due date scheduled

**Code coverage:**
- ✅ Register equipment
- ✅ Record calibration (passed/failed, as-found/as-left, standards, uncertainty)
- ✅ Decommission equipment
- ✅ List due-for-calibration
- ✅ Calibration history
- 🔴 No OOT→Quality Event auto-creation
- 🔴 No automatic scheduling/reminders (no schedule service)
- 🔴 No calibration certificate generation
- 🔴 No usage logbook
- 🔴 No blocking calibration if standards expired (logic not implemented)

---

### M7: Environmental Monitoring

**Status: 🔴 Not started**

#### Purpose
Tracks lab environmental conditions (temperature, humidity, particulates, differential pressure) with manual and IoT sensor readings. Exceeding limits triggers alerts and auto-creates Quality Events.

#### Spec-Defined Fields (not in code)

**Monitoring Point:**
| Field | Example |
|-------|---------|
| Point ID | EM-FRIDGE-MICRO-01 |
| Location | Microbiology Lab Room 3 |
| Parameter | Temperature |
| Alert Limit | 8 °C |
| Action Limit | 10 °C |
| Frequency | Continuous (IoT) / Every 4 hours (manual) |
| Last Reading | 5.2 °C |
| Status | Within Limits / Alert / Excursion |

#### Workflow Steps (Spec)

1. **Continuous Monitoring** — IoT sensors report via MQTT/HTTP
2. **Excursion Detection** — Alert/Action limits exceeded
3. **Immediate Action** — Analyst investigates, documents action
4. **Investigation** — QM reviews, escalates to CAPA if recurring
5. **Closure** — Event closed after confirmation

**Nothing is implemented.** No Environmental Monitoring service exists.

---

### M8: Supplier Quality

**Status: 🔴 Not started**

#### Purpose
Manages external supplier qualification, approval status, performance monitoring, and material/part linking. Auto-disables material links when supplier status drops.

#### Spec-Defined Fields (not in code)

**Supplier:**
| Field | Example |
|-------|---------|
| Supplier ID | SUP-2024-0012 |
| Name | Sigma-Aldrich |
| Type | Reagent / Reference Material / Service / Equipment |
| Status | Approved / Conditionally Approved / Under Qualification / Inactive / Certified / Disapproved |
| Criticality | Critical / Major / Minor |
| Risk Score | Low / Medium / High |
| Contacts[] | Name, Phone, Email |
| Materials/Parts/Services[] | Linked items with part numbers |

**⚠️ Spec gap:** Spec defines 3 statuses (Approved/Conditionally Approved/Rejected). Industry uses 7. Should expand to: Approved, Not Approved, Conditionally Approved, Under Qualification, Inactive, Certified, Disapproved.

#### Workflow Steps (Spec)

1. **New Supplier Request** — Section Head identifies need
2. **Initial Evaluation** — QM sends qualification questionnaire; on-site audit for Critical
3. **Approval Decision** — Approved / Conditionally Approved / Disapproved
4. **Material Linking** — QA Officer links part numbers
5. **Ongoing Monitoring** — CoA verification, scorecard, NCR tracking
6. **Re-qualification** — Annual/biannual review
7. **Auto-Disable** — Status drop → material links disabled

**Nothing is implemented.** Not even a stub service folder exists under `backend/qms/`.

---

### M9: Risk Management

**Status: 🔴 Not started**

#### Purpose
Proactively identifies and tracks risks before they become events. Includes Operational Risk and **Impartiality Risk Register** (ISO 17025 Clause 4.1 specific).

#### Spec-Defined Fields (not in code)

**Risk Record:**
| Field | Example |
|-------|---------|
| Risk ID | RSK-2026-0021 |
| Category | Operational / Impartiality / Financial / Regulatory / Safety |
| Description | "Reference standards may degrade" |
| Severity | 1–5 |
| Likelihood | 1–5 |
| Risk Score | Severity × Likelihood = 12 |
| Mitigation Plan | Text |
| Owner | Rajesh Patel |
| Status | Identified / Mitigated / Accepted / Monitoring |
| Review Date | Quarterly |

**Nothing is implemented.** No Risk Management service exists.

---

### M10: Proficiency Testing (PT)

**Status: 🔴 Not started**

#### Purpose
Manages inter-laboratory comparison programs required by ISO 17025. Tracks PT round participation, calculates z-scores/En numbers, and auto-creates CAPAs for unsatisfactory results.

#### Spec-Defined Fields (not in code)

**PT Round:**
| Field | Example |
|-------|---------|
| PT ID | PT-2026-Q2-MICRO-001 |
| Provider | LGC / NSI / FAPAS / Bipea |
| Scheme Name | "Microbiological Examination of Water" |
| Round | Q2 2026 |
| Sample Received Date | 5 Apr 2026 |
| Reported Result | "TVC: 45 CFU/mL" |
| Reference Value | 47 CFU/mL |
| z-score | -0.4 |
| En number | 0.3 |
| Status | Pending / Submitted / Awaiting Score / Satisfactory / Unsatisfactory |

**Nothing is implemented.** No PT service exists.

---

### M11: Customer Complaint Management

**Status: 🔴 Not started**

#### Purpose
Captures and resolves client complaints per ISO 17025 Clause 7.9. Investigates, responds, and escalates systemic issues to CAPA.

#### Spec-Defined Fields (not in code)

| Field | Example |
|-------|---------|
| Complaint ID | CMP-2026-0044 |
| Customer | ABC Foods Inc. |
| Received Via | Email / Phone / Web Form / Client Portal |
| Severity | Critical / Major / Minor |
| Category | Test Result Dispute / Turnaround / Communication / Invoice |
| Date Received | 15 May 2026 |
| Investigator | Rajesh Patel |
| CAPA Reference | (if escalated) |

**Nothing is implemented.** No Complaint service exists.

---

### M12: Management Review

**Status: 🔴 Not started**

#### Purpose
ISO 17025 Clause 8.9 requires annual leadership review of the QMS. This module auto-compiles 12 required inputs from all other modules and tracks decisions/action items.

#### Spec-Defined Inputs (12 categories)
1. Status of actions from previous review
2. Policy/objectives suitability
3. Audit results (internal & external)
4. CAPA status
5. External assessments
6. Quality indicators/KPIs
7. Supplier performance
8. Customer feedback
9. Risk register status
10. Training status
11. Resource adequacy
12. PT performance

**Nothing is implemented.** No Management Review service exists.

---

### M13: Reporting & Analytics

**Status: 🔴 Not started**

#### Purpose
Business intelligence layer over all modules. Provides dashboards, KPIs, scorecards, trend charts, and (Phase 3) AI-powered insights.

#### Spec-Defined Dashboards
| Dashboard | What it shows |
|-----------|--------------|
| Quality Scorecard | Open CAPAs, overdue training, calibration compliance |
| CAPA by Department | Pie chart |
| Complaints by Product | Pie chart |
| NCMR Disposition | Scrap / Rework / Return / Accept |
| Training Compliance | % completed |
| Audit Findings Trend | Over time, by type, by area |
| PT Performance | z-score trends |
| Equipment Calibration Status | In Service / Due / Overdue / OOS |

#### Phase 3 AI Features
- Trend Detection
- Root Cause Suggestion
- Exam Generation
- Predictive Compliance

**Nothing is implemented.** The `reporting-service` and `analytics-service` are stubs only (pyproject.toml + Dockerfile). A simple analytics frontend page exists at `frontend/apps/web/app/(qms)/qms/analytics/` but has no backend.

---

### M14: Lab-Specific Features

**Status: ⚠️ Spec'd (gaps acknowledged) — 🔴 Not started in code**

These are distributed capabilities, not a single module:

| Feature | Lab Type | Spec Status | Code |
|---------|----------|------------|------|
| Method Validation | Chemistry, Microbiology | G-01 (High gap) | 🔴 |
| Measurement Uncertainty | All testing labs | G-02 (Medium gap) | 🔴 |
| Control Charts (Shewhart, CUSUM, EWMA, Westgard) | Chemistry, Calibration | G-03 (Medium gap) | 🔴 |
| Media Prep QC | Microbiology | G-04 (Medium gap) | 🔴 |
| Culture Collection | Microbiology | G-04 (Medium gap) | 🔴 |
| CRM Tracking | Chemistry | G-05 (Medium gap) | 🔴 |
| HPLC/GC/ICP Workflows | Chemistry | G-05 (Medium gap) | 🔴 |
| Calibration Certificates | Calibration Labs | G-10 (Medium gap) | 🔴 |
| Aseptic Technique Assessment | Microbiology | G-08 (Low gap) | 🔴 |
| Scope of Accreditation Management | All labs | G-06 (Low gap) | 🔴 |

**These are RainerQMS's competitive moat vs MasterControl/TrackWise, but none are implemented.**

---

## 4. User Roles & Permissions

### 4.1 Code-Defined Roles

The `rainer_auth_lib/permissions.py` defines 5 roles with 76 permissions:

| Role | Code Constant | Description |
|------|--------------|-------------|
| Super Admin | `SUPER_ADMIN` | All 76 permissions |
| Tenant Admin | `TENANT_ADMIN` | All permissions within a tenant (admin panel + all modules) |
| Tenant User | `TENANT_USER` | Read-only access to all QMS/EM/CCV modules |
| Company Admin | `COMPANY_ADMIN` | Company-scoped admin (full access to all modules + company management) |
| Company User | `COMPANY_USER` | Company-scoped read-only access |

### 4.2 Permission Categories

**Platform (28 permissions):**
- `tenant:read/write/delete`, `user:read/write/delete`, `role:read/write`, `audit:read/export`, `config:read/write`
- `company:read/write/delete`, `company_user:read/write/delete`

**QMS (12 permissions):**
- `document:read/write/approve/delete`
- `quality_event:read/write`
- `capa:read/write/approve`
- `training:read/write/assign`
- `equipment:read/write`

**EM (6 permissions):** `plate:read/write`, `job:read/write`, `qa_review:read/write/approve`

**CCV (14 permissions):** `crm:read/write`, `contract:read/write`, `workorder:read/write/execute`, `certificate:read/write/issue`, `billing:read/write`

**Reporting (4 permissions):** `report:read/generate`, `analytics:read`

### 4.3 Spec Roles vs Code Roles Comparison

| Spec Role | Closest Code Role | Match |
|-----------|------------------|-------|
| Tenant Admin | `TENANT_ADMIN` | ✅ Matches |
| Quality Manager | Not in code enum | ⚠️ Would need QM-specific permissions |
| Lab Director | Not in code enum | ⚠️ Would need Director-specific permissions |
| Section Head | Not in code enum | ⚠️ Would need Section Head permissions |
| Analyst / Technician | `TENANT_USER` | ⚠️ Read-only; spec says write access for events |
| Viewer | Not in code enum | ⚠️ Not separately defined |
| Auditor | Not in code enum | ⚠️ Not separately defined |
| API User | Not in code enum | ⚠️ Not separately defined |

**⚠️ Key gap:** The spec defines 8 roles. Code defines only 5 roles. The QMS-specific roles (Quality Manager, Lab Director, Section Head, Auditor, Viewer) are not mapped to distinct code roles. Currently, every user with `TENANT_USER` role has identical permissions.

**Spec role ambiguities (R-01 to R-04):**
- R-01: Auditor read-access boundaries on non-audit modules not explicit
- R-02: Section Head "related sections" not defined
- R-03: Analyst write permissions on Equipment unclear
- R-04: Viewer role scope authority not specified

---

## 5. Cross-Module Event Flows

### 5.1 9 Key Event Flows (Spec)

| # | Trigger | Source | Target | Spec'd | Code Status |
|---|---------|--------|--------|--------|-------------|
| 1 | Document Approved → Effective | M1: Document | M5: Training | ✅ | 🔴 Not wired |
| 2 | Document Approved | M1: Document | Notification | ✅ | 🔴 Not wired |
| 3 | Critical Quality Event Created | M2: Quality Event | M3: CAPA | ✅ | 🔴 Not wired |
| 4 | Major/Minor Audit Finding | M4: Audit | M3: CAPA | ✅ | 🔴 M4 doesn't exist |
| 5 | Calibration Failed (OOT) | M6: Equipment | M2: Quality Event | ✅ | 🔴 Not wired |
| 6 | Environmental Excursion | M7: Env. Monitoring | M2: Quality Event | ✅ | 🔴 M7 doesn't exist |
| 7 | PT Unsatisfactory (|z|>3) | M10: PT | M3: CAPA | ✅ | 🔴 M10 doesn't exist |
| 8 | CAPA Action Overdue | M3: CAPA | Notification | ✅ | 🔴 Not wired |
| 9 | Training Overdue | M5: Training | Notification | ✅ | 🔴 Not wired |

### 5.2 Event Bus Implementation

The `rainer_events` shared library has:
✅ `DomainEvent` base schema with `event_type`, `aggregate_type`, `aggregate_id`, `tenant_id`, `actor_id`, `data`, `metadata`
✅ `EventEnvelope` wire format wrapper (`event_id`, `occurred_at`, `schema_version`)
✅ `EventPublisher` class with `publish()` and `publish_batch()` methods
✅ Singleton `AIOKafkaProducer` with idempotent delivery and gzip compression
✅ Topic routing: `rainer.{aggregate_type}.events`

**But:**
- No QMS service imports `EventPublisher` or publishes any events
- No Kafka consumer/listener exists in any service
- The `producer.py` has a `TODO` comment about training events

### 5.3 Configuration vs Reality

| Config Variable | Value | Used Where? |
|----------------|-------|-------------|
| `kafka_bootstrap_servers` | localhost:9092 | Configured, never connected |
| `audit_service_url` | http://audit-service:8004 | Configured, never called |
| `notification_service_url` | http://notification-service:8005 | Configured, never called |
| `file_service_url` | http://file-service:8009 | Configured, never called |
| `workflow_service_url` | http://workflow-engine:8007 | Configured, never called |

---

## 6. Platform Services

### 6.1 Fully Implemented

| Service | Location | Endpoints |
|---------|----------|-----------|
| **Workflow Engine** | `backend/platform/workflow-engine/` | 10 endpoints (definitions, instances, transitions, tasks, history) |

The workflow-engine is a **generic state machine** supporting arbitrary entity types. It has its own state machine with definitions, instances, history, and tasks. This was meant to be used by QMS services but **no QMS service integrates with it** (all QMS services have their own hardcoded state machines).

### 6.2 Stub Only (pyproject.toml + Dockerfile, no Python code)

| Service | Location |
|---------|----------|
| Auth Service | `backend/platform/auth-service/` |
| Tenant Service | `backend/platform/tenant-service/` |
| User Service | `backend/platform/user-service/` |
| Audit Service | `backend/platform/audit-service/` |
| Notification Service | `backend/platform/notification-service/` |
| Config Service | `backend/platform/config-service/` |
| Gateway Service | `backend/platform/gateway-service/` |
| File Service | `backend/platform/file-service/` |
| Schedule Service | `backend/platform/schedule-service/` |
| Reporting Service | `backend/platform/reporting-service/` |
| Analytics Service | `backend/platform/analytics-service/` |

### 6.3 Shared Libraries (All Implemented)

| Library | Function |
|---------|----------|
| `rainer_common` | Exception hierarchy, response envelopes, health checks, middleware, pagination, tracing |
| `rainer_auth_lib` | JWT management, 76 permissions, 5 roles, FastAPI dependencies |
| `rainer_events` | Domain event schemas, Kafka producer |
| `rainer_cache` | Async Redis client with cache-aside pattern |
| `rainer_tenant_lib` | Tenant DB resolution, per-tenant engine pools |

---

## 7. Gaps & Issues Registry

### 7.1 Code Defects (Showstoppers)

| ID | Issue | Location | Severity |
|----|-------|----------|----------|
| D-1 | `last_rejection_reason` column drift — Was added in migration 002 but WAS missing from ORM. **Now fixed** (present in current `models.py`) | db/models.py | 🐞 Was Critical, Now Fixed |
| D-2 | Dead transition `create_new_version` in `VALID_TRANSITIONS` with no handler method or API endpoint | domain/services.py:20 | 🐞 Critical |
| D-3 | Dead acknowledgment code — `document_acknowledgments` table + model exist, no API/service/repository | infra/db/models.py | 🐞 Critical |
| D-4 | Missing `Superseded` and `Effective` states — only 4 states, industry standard is 6 | domain/services.py | 🐞 Critical |

### 7.2 Config Without Implementation

| Config | Status |
|--------|--------|
| Kafka bootstrap servers configured, zero events emitted | 🔴 |
| Audit service URL configured, no audit events sent | 🔴 |
| Notification service URL configured, no notifications sent | 🔴 |
| File service URL configured, no upload/download | 🔴 |
| Workflow service URL configured, no integration | 🔴 |
| `max_document_versions` (100) configured, never checked | 🔴 |

### 7.3 Spec Gaps (From 01_Spec_vs_Industry.md)

#### Document Control Gaps
| # | Gap | Source |
|---|-----|--------|
| NW-01 | Document Vaults (QA-rel, QA-dft, Course Release) not specified | MasterControl |
| NW-02 | Hierarchical Taxonomies / Folders not specified | MasterControl |
| NW-03 | Controlled Copies tracking not specified | MasterControl |
| NW-04 | InfoCard canonical view UI not specified | MasterControl |
| NW-05 | Explorer view with breadcrumbs not specified | MasterControl |
| NW-06 | Collaboration Workspace pattern not specified | MasterControl |
| NW-07 | Lifecycle naming (e.g. "Quality Lifecycle") not specified | MasterControl |

#### Quality Event Gaps
| # | Gap | Source |
|---|-----|--------|
| NW-08 | Event Analyzer cross-event matching pattern absent | MasterControl |
| NW-09 | Forms-Based System (FBS) multi-tab form pattern absent | MasterControl |

#### Audit Gaps
| # | Gap | Source |
|---|-----|--------|
| NW-10 | Audit Workspace 4-tab UI not specified | MasterControl |
| NW-11 | Drag-and-drop audit calendar absent | MasterControl |
| NW-12 | Cascading entity picker (supplier) not specified | MasterControl |
| NW-13 | Qualified auditor two-column picker not specified | MasterControl |

#### Supplier Gaps
| # | Gap | Source |
|---|-----|--------|
| NW-14 | Status enum too narrow (3 vs. industry 7) | MasterControl |
| NW-15 | Auto-disable material links on status drop not specified | MasterControl |
| NW-16 | Secure Guest Connect for external suppliers not specified | MasterControl |
| NW-17 | Advanced Search builder not specified | MasterControl |
| NW-18 | Material/Part linking subsection not specified | MasterControl |

#### Training Gaps
| # | Gap | Source |
|---|-----|--------|
| NW-19 | Job Codes as first-class entity absent | MasterControl |
| NW-20 | Job Code Status matrix UI absent (major compliance gap) | MasterControl |
| NW-21 | 5-step training task UX not specified | MasterControl |
| NW-22 | Trainers/Classes/Trainees as separate entities absent | MasterControl |
| NW-23 | Bulk import of training records not specified | MasterControl |

#### Dashboard Gaps
| # | Gap | Source |
|---|-----|--------|
| NW-24 | Personalized dashboard composition not specified | MasterControl |
| NW-25 | Always-visible left nav rail not specified | MasterControl |
| NW-26 | Quick-access tiles (MY TASKS, MY RECENT, START TASK) not specified | MasterControl |

### 7.4 Cross-Cutting Compliance Gaps

| Requirement | Expected | Actual |
|------------|----------|--------|
| 21 CFR Part 11 §11.10(e) — Audit trails | All operations logged | 🔴 No audit trail emission |
| 21 CFR Part 11 §11.50 — Signature manifestations | Name + Date/Time + Meaning | ⚠️ Meaning not captured |
| 21 CFR Part 11 §11.100(b) — Re-authentication | Re-enter password to sign | 🔴 Not implemented |
| 21 CFR Part 11 §11.200(a)(1) — Two distinct components | UserID + Password re-entry | 🔴 Not implemented |
| 21 CFR Part 11 §11.10(g) — Authority checks | Role-based authorization on signing | 🔴 No role enforcement |
| ALCOA+ Attributable | Every record linked to user | ⚠️ User on create/approve, not on all ops |
| ALCOA+ Contemporaneous | Real-time entry; late entry flagging | ⚠️ Impacted by no audit trail |
| ALCOA+ Original | First-entry preserved | ⚠️ Updates overwrite without before/after snapshots |

### 7.5 Missing Modules

| Module | Priority | Dependencies |
|--------|----------|-------------|
| Audit Management | High | Document service (for checklist docs), CAPA service (for auto-CAPA) |
| Supplier Quality | High | Document service (for supplier docs) |
| Environmental Monitoring | Medium | Quality Event service (for excursion→QE) |
| Risk Management | Medium | Standalone |
| Proficiency Testing | Medium | CAPA service (for unsatisfactory→CAPA) |
| Customer Complaints | Medium | CAPA service (for escalation) |
| Management Review | Low | All other modules (aggregates data from them) |
| Reporting & Analytics | Low | All other modules |
| Lab-Specific Features | Medium | Equipment service (for cal certs) |

---

## 8. Frontend Implementation

### 8.1 Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Framework | Next.js | 15.1.6 |
| Language | TypeScript | ESNext |
| Styling | Tailwind CSS + CSS Variables | shadcn/ui (New York style) |
| UI Library | Radix UI primitives + custom shadcn/ui | Latest |
| State (Server) | TanStack React Query | 5.62.0 |
| State (Client) | Zustand | 5.0.2 |
| Forms | react-hook-form + zod resolver | 7.54.0 / 3.23.8 |
| Validation | Zod | 3.23.8 |
| HTTP Client | Axios | 1.7.9 |
| Auth | NextAuth v5 (beta) | @auth/core beta.25 |
| Charts | Recharts (via `useDashboard`) | — |
| Tables | @tanstack/react-table | 8.20.0 |
| Icons | Lucide React | Latest |
| Animation | Framer Motion | Latest |
| Toast | Sonner | Latest |
| Real-time | Socket.io-client (dep) | 4.8.1 |
| Testing | Vitest + Playwright | Latest |
| Package Manager | npm | — |

### 8.2 Route Structure

```
/ (root)                        → redirect: /signin or /dashboard or /super-admin
/signin                         → User login page (email + password + MFA)
/super-admin/signin             → Super admin login (separate restricted login)

/(platform)                     → Authenticated platform layout
  /dashboard                    → Product cards (QMS/EM/CCV) + KPI widgets
  /profile                      → Personal info tabs (Personal Info, Security/MFA)
  /settings                     → Tenant settings (general, notifications, security, appearance)
  /settings/users               → User management list (search, CRUD, role assignment)
  /settings/users/[userId]      → User detail (profile, permissions, activity tabs)
  /settings/companies           → Company list
  /settings/companies/new       → Create company wizard
  /settings/companies/[id]      → Company detail + users

/(qms)                          → QMS product layout
  /qms/documents                → Document Control list (table + filters)
  /qms/documents/[id]           → Document detail (overview/versions/distribution tabs)
  /qms/quality-events           → Quality Events list (table + filters)
  /qms/quality-events/[id]      → Quality Event detail (details, assignment, escalate/close)
  /qms/capa                     → CAPA list (table + filters)
  /qms/capa/[id]                → CAPA detail (lifecycle viz, root cause, actions, verify/close)
  /qms/training                 → Training courses list
  /qms/training/my-training     → Current user's training assignments
  /qms/equipment                → Equipment list (table + filters)
  /qms/equipment/[id]           → Equipment detail (asset details, calibrate, decommission, edit)
  /qms/analytics                → QMS Analytics (KPI cards + doc status + CAPA aging charts)

/(admin)                        → Super admin layout
  /admin                        → Super Admin Panel (overview/users/services/audit tabs)
  /admin/tenants                → Tenant directory (search, filter, CRUD)
  /admin/tenants/new            → Create tenant wizard (core details, contact, company, address, billing)
  /admin/tenants/[slug]         → Tenant detail (workspace, contacts, users)
  /admin/tenants/[slug]/edit    → Edit tenant (name, products, tier)
  /admin/tenants/[slug]/settings → Tenant settings (max_users, storage, timezone, locale)
  /super-admin                  → Alias of /admin
  /super-admin/signin           → Admin login

/(ccv)                          → CCV product layout (mostly stubs)
  /ccv/dashboard, /ccv/crm, /ccv/contracts, /ccv/work-orders,
  /ccv/technicians, /ccv/billing, /ccv/certificates, /ccv/analytics

/(em)                           → EM product layout (mostly stubs)
  /em/dashboard, /em/plates, /em/jobs, /em/analytics
```

### 8.3 Component Architecture

```
Root Layout (app/layout.tsx)
├── AppSessionProvider (NextAuth SessionProvider)
│   └── SessionToAuthStoreSync (syncs session → Zustand auth store)
├── QueryProvider (TanStack React Query)
│   ├── ThemeProvider (dark/light/system)
│   └── Toaster (Sonner toast notifications)
│       └── Platform Shell
│           ├── Sidebar (navigation)
│           ├── Header (search, theme toggle, notifications, user menu)
│           └── Page Content (module-specific)
```

**Sidebar Navigation** (`components/platform/Sidebar.tsx`):
- QMS: Documents, Quality Events, CAPA, Training, My Training, Equipment, Analytics
- EM: Plates, Jobs, Analytics
- CCV: CRM, Contracts, Work Orders, Technicians, Billing, Certificates, Analytics
- Platform: Dashboard, Users (tenant_admin), Companies (tenant_admin), My Company (company_admin), Settings
- Admin: Platform admin (red highlight), Tenants
- Collapsible (64px collapsed / 256px expanded), active route highlighting

**Header** (`components/platform/Header.tsx`):
- Search bar (debounced, syncs to URL `q` param)
- Theme toggle (light/dark/system)
- Notification bell (unread count dot, dropdown panel with mark-read)
- User menu (avatar with initials, email, role, sign out)

**Dashboard Products** (`components/platform/DashboardProducts.tsx`):
- Super admins see: Total Tenants, Active Tenants, Directory Users, Audit Entries
- Tenant users see: 3 product cards (RainerQMS, EndGameBiotech, RainerCCV) with per-product KPIs
- 4 QMS dashboard widgets below

### 8.4 QMS Page-by-Page UI Binding

#### 8.4.1 Document Control

**List Page** (`app/(qms)/qms/documents/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Breadcrumb | Back > Home > Document Control |
| Search | Text input, client-side status filter |
| Table columns | Doc #, Title, Type, Status (colored badge), Version, Updated |
| Status badges | `draft` (gray), `under_review` (yellow), `approved` (green), `obsolete` (red) |
| Pagination | 20 per page, prev/next with page count |
| New Document dialog | doc_number (required), title (required), doc_type (select: SOP/WI/Policy/Form/Record), description |
| Row click | Navigates to `/qms/documents/{id}` |
| API binding | `useDocuments({search, status, page, page_size})` → `documentsApi.list()` |
| API call | `GET /documents?search=&status=&page=&page_size=` |

**Detail Page** (`app/(qms)/qms/documents/[id]/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Breadcrumb | Back > Documents > {doc_number} |
| Header | Title + doc_number, action buttons conditionally shown |
| Tabs | Overview, Versions, Distribution |
| Action buttons | Reject + Approve (when `under_review`), Make obsolete (when `approved`) |
| **Overview tab** | Status, Version, Approver (single), Owner, Review date, Effective date, Last rejection reason (amber alert), Description |
| **Versions tab** | List of `DocumentVersion[]`: version, change_summary, created_at |
| **Distribution tab** | User ID input (UUID) + Add button, current members list |
| Reject dialog | Reason textarea (required) |
| Approve dialog | E-signature input (required), optional review date (datetime-local) |
| Make obsolete dialog | Confirmation |
| **Training auto-assign** | On approval, if user has `training:assign`: fetches distribution members → fetches linked courses (by `document_id`) → bulk assigns training |
| API bindings | `useDocument(id)`, `useDocumentVersions(id)`, `useDocumentDistribution(id)` |
| Mutations | `useApproveDocument()`, `useRejectDocument()`, `useMakeDocumentObsolete()`, `useAddDistributionMember()` |
| API calls | `GET /documents/{id}`, `GET /documents/{id}/versions`, `GET /documents/{id}/distribution`, `POST /documents/{id}/approve`, `POST /documents/{id}/reject`, `POST /documents/{id}/make-obsolete`, `POST /documents/{id}/distribution` |

**Frontend fields NOT bound in detail page:**
- `doc_type` (shown only in list, not detail)
- `department` (exists in API response, not displayed in detail overview)
- `expiry_date` (exists in API response, not displayed)
- `tags`, `regulatory_frameworks` (exists in API, not displayed)
- `file_id` (exists in API, no file download/view)
- `is_controlled` (exists in API, not displayed)

#### 8.4.2 Quality Events

**List Page** (`app/(qms)/qms/quality-events/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Breadcrumb | Back > Home > Quality Events |
| Search + filter | Text search + status dropdown (syncs to URL `status` param) |
| Status config | `open` (blue), `under_investigation` (amber), `pending_capa` (purple), `closed` (green), `cancelled` (slate) |
| Severity colors | `critical` (red), `major` (orange), `minor` (yellow), `observation` (slate) |
| Table columns | Event #, Title, Severity (badge), Department, Status (badge), Reported |
| Pagination | 10 per page |
| Report Event dialog | title, description, event_type (deviation/oos/complaint/incident), severity (critical/major/minor/observation) |
| Wraps in `Suspense` | For `useSearchParams` |
| API binding | `useQualityEvents({search, status, page, page_size})` |
| API call | `GET /quality-events?search=&status=&page=&page_size=` |

**Detail Page** (`app/(qms)/qms/quality-events/[id]/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Header | Title + event_number + actions |
| Linked CAPA card | If `capa_id` exists, shows "Open CAPA" link |
| Details card | Status, Severity, Type, Detected_at, Description |
| Assignment card | Assigned_to, Department |
| Escalate to CAPA dialog | Pre-fills CAPA title/description from event, calls `useCreateCAPA()` + `useUpdateQualityEvent()` to link `capa_id` |
| Close dialog | Resolution textarea (optional) |
| Delete dialog | AlertDialog confirmation |
| API calls | `GET /quality-events/{id}`, `POST /quality-events/{id}/close`, `DELETE /quality-events/{id}`, `POST /capas` (to create linked CAPA) |

**Frontend fields NOT bound:**
- `root_cause` (exists in API, not displayed)
- `immediate_action` (exists in API, not displayed)
- `priority` (exists in API, not displayed)
- `capa_required` (exists in API, not displayed)
- `due_date` (exists in API, not displayed)
- `tags`, `attachments` (exists in API, not displayed)

#### 8.4.3 CAPA Management

**List Page** (`app/(qms)/qms/capa/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Table columns | CAPA #, Title, Type, Severity (badge), Status (badge), Due Date |
| Status filter | Open, Under investigation, Root cause, Implementation, Effectiveness, Closed, Cancelled |
| Pagination | 10 per page |
| Severity colors | `critical` (red), `major`/`high` (orange), `minor`/`medium` (yellow), `low` (slate) |
| API call | `GET /capas?status=&severity=&page=&page_size=` |

**Detail Page** (`app/(qms)/qms/capa/[id]/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Lifecycle visualization | 6-step progress bar: Open → Investigation → Root cause → Implementation → Effectiveness → Closed (green check/circles) |
| Header | Title + capa_number + Linked quality event button (if source) |
| Overview card | Type, Severity, Owner, Due, Description |
| Effectiveness card | Verified status, Verify effectiveness button, Close CAPA button |
| Actions section | List of actions with Complete button per action |
| Edit root cause dialog | root_cause textarea + method input |
| Add action dialog | action_type (text) + description textarea |
| Verify effectiveness dialog | Mark effective (checkbox) + notes |
| Complete action dialog | Evidence textarea |
| API calls | `GET /capas/{id}`, `GET /capas/{id}/actions`, `PATCH /capas/{id}`, `POST /capas/{id}/close`, `POST /capas/{id}/verify-effectiveness`, `POST /capas/{id}/actions`, `POST /capas/{id}/actions/{actionId}/complete` |

**Frontend fields NOT bound:**
- `source_type` / `source_id` (shown only if quality_event link exists)
- `target_close_date` (exists in API, not displayed)
- `actual_close_date` (exists in API, not displayed)
- `effectiveness_check_date` (exists in API, not displayed directly)
- `department` (exists in API, not displayed in detail)
- `tags`, `attachments` (exists in API, not displayed)

#### 8.4.4 Training

**Courses List Page** (`app/(qms)/qms/training/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Breadcrumb | Back > Home > Training Management |
| Search | Client-side filter on code, title, department |
| Filters | Department text input + Mandatory (All/Mandatory Only) |
| Table columns | Code, Title, Department, Type, Duration, Mandatory (Yes/No), Status (Active/Inactive badge) |
| Pagination | 10 per page |
| New Course dialog | Uses `react-hook-form` + `zodResolver` with `createCourseSchema` |
| Course form fields | course_code, title, department, course_type (online/classroom/blended/document_read), duration_hours, passing_score (80 default), requires_certification (checkbox), is_mandatory (checkbox), description |
| API call | `GET /training/courses?page=&page_size=` |

**My Training Page** (`app/(qms)/qms/training/my-training/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Header | "My training" with assignment count |
| Assignment list | Course ID, Due date, Status, Complete button (if not completed) |
| Complete dialog | Score (optional), Notes, E-signature (required if course requires_certification) |
| API calls | `GET /training/assignments`, `POST /training/assignments/{id}/complete` |

**Frontend fields NOT bound:**
- Course detail view (no `[id]` page for training courses)
- Job Code management (not implemented)
- Job Code Status matrix (not implemented)
- Trainer management (not implemented)
- Exam/question bank (not implemented)
- `document_id` link (exists in API, not displayed)
- `recurrence_days` (exists in API, not displayed)

#### 8.4.5 Equipment

**List Page** (`app/(qms)/qms/equipment/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Breadcrumb | Back > Home > Equipment Management |
| Search | Text search |
| Status filter | Active, Cal Due, Cal Overdue, Maintenance, Out of Service, Decommissioned |
| Table columns | Asset Tag, Name, Manufacturer, Location, Status (badge), Next Calibration |
| Pagination | 10 per page |
| API call | `GET /equipment?status=&page=&page_size=` |

**Detail Page** (`app/(qms)/qms/equipment/[id]/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| Header | Name + asset_tag + action buttons (Record calibration, Edit, Decommission, Delete) |
| Asset details card | Status, Type, Next calibration, Location, Notes |
| Record calibration dialog | Calibration date (datetime-local), Passed checkbox, Notes |
| **Auto QE on failure** | If calibration fails + user has `quality_event:write`: auto-creates quality event with `event_type: "calibration_failure"` |
| Decommission dialog | Reason textarea |
| Edit dialog | Name, Description, Location, Department, Assigned To, Notes, Requires Calibration (Checkbox), Calibration Frequency Days |
| Delete | AlertDialog confirmation |
| API calls | `GET /equipment/{id}`, `POST /equipment/{id}/calibrate`, `POST /equipment/{id}/decommission`, `PATCH /equipment/{id}`, `DELETE /equipment/{id}`, `POST /quality-events` (on cal failure) |

**Frontend fields NOT bound:**
- `manufacturer` (shown in list, NOT in detail page)
- `model` (exists in API, not displayed at all)
- `serial_number` (exists in API, not displayed)
- `requires_pm`, `pm_frequency_days` (exists in API, not displayed)
- `last_pm_date`, `next_pm_date` (exists in API, not displayed)
- `purchase_date`, `warranty_expiry` (exists in API, not displayed)
- Calibration history (no UI for calibration_records list)
- No "Add Equipment" endpoint bound to UI (button exists but no dialog)

#### 8.4.6 Analytics

**QMS Analytics Page** (`app/(qms)/qms/analytics/page.tsx`):

| UI Element | Implementation |
|-----------|---------------|
| 4 KPI cards | Open CAPAs, Documents Total, Upcoming Trainings, Equipment Cal Due |
| Document Status Distribution | Bar chart: Draft, Under Review, Approved, Obsolete with counts and percentages |
| CAPA Aging Summary | Bar chart: 0-30 days, 31-60 days, 61-90 days, 90+ days with counts and percentages |
| API calls | `GET /analytics/kpis`, `GET /analytics/dashboards/qms_overview` |

### 8.5 API Client Architecture

**Client Layer** (`lib/api/`):

```
lib/api/
├── client.ts              → Platform API client (axios instance)
├── qms-client.ts          → Per-QMS-service clients (documents, quality-events, capa, training, equipment)
├── session.ts             → Cached session + auth context resolution
└── services/
    ├── index.ts           → Re-exports all types + API objects
    ├── qms.ts             → QMS API functions + TypeScript interfaces
    ├── platform.ts        → Platform API functions (users, tenants, auth, audit, companies, roles)
    ├── analytics.ts       → Analytics API functions (KPIs, dashboards, time series)
    ├── ccv.ts             → CCV API functions (customers, contracts, work orders, etc.)
    └── em.ts              → EM API functions (plates, images, AI runs, jobs, QA reviews)
```

**QMS TypeScript Interfaces (`lib/api/services/qms.ts`):**

```typescript
interface Document {
  id: string; doc_number: string; title: string; doc_type: string;
  status: string; current_version: string; description?: string | null;
  department?: string | null; owner_id?: string | null; approver_id?: string | null;
  effective_date?: string | null; review_date?: string | null; expiry_date?: string | null;
  file_id?: string | null; tags?: string[]; regulatory_frameworks?: string[];
  is_controlled?: boolean; created_by?: string; last_rejection_reason?: string | null;
  created_at: string; updated_at: string;
}

interface DocumentVersion {
  id: string; document_id: string; version: string; file_id: string | null;
  change_summary: string | null; approved_by: string | null; approved_at: string | null;
  signature_hash: string | null; created_by: string; created_at: string;
}

interface DocumentDistribution {
  id: string; document_id: string; user_id: string; added_by: string; created_at: string;
}

interface QualityEvent {
  id: string; event_number: string; title: string; event_type: string;
  description?: string; status: string; severity: string; priority?: string;
  department: string | null; location?: string | null; detected_at: string;
  detected_by?: string | null; assigned_to?: string | null; root_cause?: string | null;
  immediate_action?: string | null; capa_required?: boolean; capa_id?: string | null;
  due_date?: string | null; closed_at?: string | null; tags?: unknown[];
  created_by?: string; created_at: string; updated_at?: string;
  reported_by?: string; reported_at?: string;
}

interface CAPA {
  id: string; capa_number: string; title: string; capa_type: string;
  severity: string; description?: string; status: string;
  source_type?: string | null; source_id?: string | null; source_event_id?: string | null;
  owner_id?: string | null; department?: string | null; root_cause?: string | null;
  root_cause_method?: string | null; due_date: string | null;
  target_close_date?: string | null; actual_close_date?: string | null;
  effectiveness_verified?: boolean; effectiveness_check_date?: string | null;
  tags?: unknown[]; created_by?: string; created_at: string; updated_at?: string;
}

interface CAPAAction {
  id: string; capa_id: string; action_type: string; description: string;
  assigned_to: string | null; due_date: string | null; status: string;
  completed_at: string | null; evidence: string | null; created_at: string;
}

interface Course {
  id: string; tenant_id: string; course_code: string; title: string;
  description: string | null; course_type: string; department: string | null;
  document_id: string | null; duration_hours: number | null; passing_score: number;
  requires_certification: boolean; recurrence_days: number | null;
  is_mandatory: boolean; is_active: boolean; created_by: string;
  created_at: string; updated_at: string;
}

interface TrainingAssignment {
  id: string; tenant_id: string; course_id: string; course_title?: string | null;
  user_id: string; assigned_by: string | null; due_date: string | null;
  status: string; score: number | null; passed: boolean | null;
  completed_at: string | null; cert_expiry_date: string | null;
  notes: string | null; created_at: string; updated_at: string;
}

interface Equipment {
  id: string; tenant_id?: string; asset_tag: string; name: string;
  description?: string | null; equipment_type: string; manufacturer: string | null;
  model: string | null; serial_number: string | null; status: string;
  location: string | null; department?: string | null;
  requires_calibration?: boolean; calibration_frequency_days?: number | null;
  last_calibration_date?: string | null; next_calibration_date?: string | null;
  next_calibration?: string | null; requires_pm?: boolean;
  pm_frequency_days?: number | null; last_pm_date?: string | null;
  next_pm_date?: string | null; assigned_to?: string | null; notes?: string | null;
  tags?: unknown[]; created_by?: string; created_at: string; updated_at?: string;
}
```

**Request/Response Wrappers:**
- `PaginatedResponse<T>`: `{ items: T[], total: number, page: number, page_size: number }`
- `SuccessEnvelope<T>`: `{ success: boolean, data: T }`
- `normalizePaginated()`: Normalizes both `{ items: [] }` and `{ data: [], pagination: {} }` response shapes
- `unwrapSuccessData()`: Extracts `.data` from `{ success: true, data: T }` envelopes

### 8.6 Auth & State Management

**Authentication Flow:**

```
Login page → NextAuth authorize() → POST /api/v1/auth/login → JWT issued
  ↓
JWT callback copies user fields (id, role, tenant_id, access_token, refresh_token)
  ↓
Session callback merges into session.user
  ↓
SessionToAuthStoreSync → Zustand auth store (persisted to localStorage: "rainer-auth")
  ↓
API client interceptor reads auth store → sets Authorization header
```

**Zustand Stores:**

| Store | Key State | Persisted |
|-------|-----------|-----------|
| `auth.store.ts` | user, tenant_id, access_token, isLoading, permissions | ✅ localStorage ("rainer-auth") |
| `ui.store.ts` | sidebarOpen, sidebarCollapsed, activeProduct, theme, commandPaletteOpen | ✅ partial ("rainer-ui") |
| `notifications.store.ts` | items (InAppNotification[]) | ✅ ("rainer-in-app-notifications") |

**React Query Hooks:**

| Domain | Query Hooks | Mutation Hooks |
|--------|------------|----------------|
| Documents | `useDocuments`, `useDocument`, `useDocumentVersions`, `useDocumentDistribution`, `useDocumentsDueForReview` | `useCreateDocument`, `useUpdateDocument`, `useApproveDocument`, `useRejectDocument`, `useMakeDocumentObsolete`, `useAddDistributionMember` |
| Quality Events | `useQualityEvents`, `useQualityEvent`, `useQualityEventsSummary` | `useCreateQualityEvent`, `useUpdateQualityEvent`, `useCloseQualityEvent`, `useDeleteQualityEvent` |
| CAPA | `useCAPAs`, `useCAPA`, `useCAPAActions` | `useCreateCAPA`, `useUpdateCAPA`, `useCloseCAPA`, `useDeleteCAPA`, `useVerifyCapaEffectiveness`, `useAddCapaAction`, `useCompleteCapaAction` |
| Training | `useCourses`, `useCourse`, `useMyTrainingAssignments`, `useTrainingOverdueAssignments` | `useCreateCourse`, `useCompleteTrainingAssignment` |
| Equipment | `useEquipment`, `useEquipmentItem`, `useEquipmentDueCalibration` | `useCreateEquipment`, `useCalibrateEquipment`, `useDecommissionEquipment`, `useUpdateEquipment`, `useDeleteEquipment` |

**RBAC in Frontend (`lib/hooks/usePermission.ts`):**
- Defines 5 roles (super_admin, tenant_admin, tenant_user, company_admin, company_user)
- 76 permission strings (same as backend `Permission` enum)
- `ROLE_PERMISSIONS` map per role
- Returns: `role`, `hasPermission(perm)`, `hasAnyPermission(perms)`, `hasAllPermissions(perms)`
- `withRBAC()` HOC: wraps components with permission guard, shows loading skeleton, redirects on insufficient permissions

### 8.7 Frontend–Backend Data Flow

```
User Action → React Component → React Query Hook → API Client (Axios) 
  → Next.js Rewrite (/api/:path* → {API_URL}/api/v1/:path*)
  → Backend Service → FastAPI Route → Permission Decorator 
  → Domain Service → Repository → Database

← Response ← JSON Response Envelope ←
  → Axios Response → normalizePaginated/unwrapSuccessData 
  → React Query Cache → Component Re-render → UI Update
```

### 8.8 Frontend Gaps & Missing Features

| Feature | Status | Impact |
|---------|--------|--------|
| **No create/register equipment dialog bound** | Button exists but no dialog/API binding | Cannot register new equipment from UI |
| **No document file upload/download** | `file_id` in API, no UI for upload or download | Documents have no content |
| **No document edit UI** | Detail page is read-only, no edit dialog | Cannot update document metadata |
| **No Job Code management UI** | Not implemented | Cannot manage job codes |
| **No Job Code Status matrix** | Not implemented | Major compliance UX gap per spec |
| **No training course detail page** | No `[id]` page for courses | Cannot view course details |
| **No training assignment management** | No UI to manually assign training | Only auto-assign on document approval |
| **No CAPA create-from-scratch dialog** | "New CAPA" button exists but no dialog | Must escalate from quality event |
| **No supplier module UI** | Not started | M4 module 0% |
| **No audit module UI** | Not started | M8 module 0% |
| **No risk management UI** | Not started | M9 module 0% |
| **No PT module UI** | Not started | M10 module 0% |
| **No complaint management UI** | Not started | M11 module 0% |
| **No management review UI** | Not started | M12 module 0% |
| **Calibration history not displayed** | No UI for calibration_records list | Cannot see past calibrations |
| **Equipment manufacturer/model/serial not shown in detail** | Fields exist in API, not displayed | Data hidden |
| **Equipment PM fields not shown** | `requires_pm`, `pm_frequency_days` in API, not displayed | PM tracking hidden |
| **No notification service consumer** | Socket.io-client installed but no consumer | Real-time updates not working |
| **No file service integration** | `file_service_url` configured, no frontend file operations | File operations broken |
| **Document field gaps in detail view** | `doc_type`, `department`, `expiry_date`, `tags`, `regulatory_frameworks` not displayed | Data hidden |
| **Quality Event field gaps** | `root_cause`, `immediate_action`, `priority`, `due_date` not displayed | Data hidden |
| **CAPA field gaps** | `target_close_date`, `actual_close_date`, `department` not displayed | Data hidden |
| **Training field gaps** | `document_id`, `recurrence_days`, `course_title` not displayed in My Training | Data hidden |

---

## 9. Glossary

| Term | Meaning |
|------|---------|
| **ALCOA+** | Data integrity: Attributable, Legible, Contemporaneous, Original, Accurate, +Complete, Consistent, Enduring, Available |
| **ASL** | Approved Supplier List |
| **CAPA** | Corrective Action / Preventive Action |
| **CoA** | Certificate of Analysis |
| **CRM** | Certified Reference Material |
| **FBS** | Forms-Based System (multi-tab quality event form pattern) |
| **FMEA** | Failure Mode and Effects Analysis |
| **GUM** | Guide to the Expression of Uncertainty in Measurement |
| **ILC** | Inter-Laboratory Comparison |
| **NC** | Non-Conformance (Major NC, Minor NC) |
| **NCMR** | Non-Conforming Material Report |
| **NCR** | Non-Conformance Report |
| **OFI** | Opportunity for Improvement (audit finding) |
| **OOS / OOT** | Out-of-Spec / Out-of-Tolerance |
| **PT** | Proficiency Testing |
| **QMS** | Quality Management System |
| **RBAC** | Role-Based Access Control |
| **RCA** | Root Cause Analysis |
| **RPN** | Risk Priority Number (Severity × Occurrence × Detectability) |
| **SCAR** | Supplier Corrective Action Request |
| **SDS** | Safety Data Sheet |
| **SOP** | Standard Operating Procedure |

---

*End of RainerQMS Complete System Reference — generated from `01_Spec_vs_Industry.md`, `02_Code_vs_Industry.md`, `03_Module_Workflows.md`, and codebase audit.*
