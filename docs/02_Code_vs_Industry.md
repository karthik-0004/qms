# RainerQMS Codebase vs. Industry References — Implementation Gap Analysis

> **Document Purpose:** This document compares the **current RainerQMS codebase** against three industry-leading QMS products — **MasterControl**, **FreeQMS**, and **Sparta TrackWise**. The goal is to map where the implementation stands today against industry-standard capability, identify what is built, what is partially built, and what is entirely missing — with file-level references where applicable.
>
> **This document does NOT analyze the spec.** It is a pure code-vs-industry comparison.
>
> **Sources analyzed:**
> - Current `document-service` codebase (state machine in `app/domain/services.py`, ORM in `app/infra/db/models.py`, migrations in `migrations/versions/`, API routes in `app/api/v1/routes/documents.py`, E2E tests in `tests/e2e/`, unit tests in `tests/unit/`)
> - MasterControl product website (mastercontrol.com) + Quality Excellence Suite UI screenshots covering 5 core modules (Documents, Audit, CAPA, Supplier, Training)
> - FreeQMS (freeqms.com)
> - Sparta Systems TrackWise (spartasystems.com/trackwise)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Methodology](#2-methodology)
3. [Current Codebase Inventory](#3-current-codebase-inventory)
4. [Industry Reference Capability Map](#4-industry-reference-capability-map)
5. [Document Service — Detailed Code vs. Industry Analysis](#5-document-service--detailed-code-vs-industry-analysis)
6. [Missing Modules — Code Reality vs. Industry Expectation](#6-missing-modules--code-reality-vs-industry-expectation)
7. [Codebase Defects & Inconsistencies](#7-codebase-defects--inconsistencies)
8. [Platform & Infrastructure Service Status](#8-platform--infrastructure-service-status)
9. [Compliance Readiness Assessment](#9-compliance-readiness-assessment)
10. [UI & UX Implementation Gap](#10-ui--ux-implementation-gap)
11. [Critical Issues Ranked by Priority](#11-critical-issues-ranked-by-priority)
12. [Recommended 90-Day Implementation Plan](#12-recommended-90-day-implementation-plan)
13. [Appendix A — Glossary](#appendix-a--glossary)
14. [Appendix B — File Reference Index](#appendix-b--file-reference-index)

---

## 1. Executive Summary

### 1.1 Top-line findings

The current RainerQMS codebase represents a **partial implementation of one module (`document-service`)** against an industry-reference QMS that typically delivers 5–8 fully functional modules. Specifically:

| Dimension | Status |
|---|---|
| **Modules implemented** | 1 of 14 expected (`document-service`, partial) |
| **Endpoints functional** | ~10 endpoints (create, read, update, soft-delete, list, submit-for-review, approve, reject, distribution-list, due-for-review, get-versions, health checks) |
| **Cross-service event flows** | 0 of 9 expected event flows are wired (Kafka installed, never published-to) |
| **Industry pattern coverage** | Approximately **5%** of the MasterControl feature surface is implemented |
| **Compliance readiness** | **Not 21 CFR Part 11 compliant today** — no audit trail emission, no signature manifest export, no re-auth on signing |
| **Critical defects** | 4 showstopper bugs (broken ORM column, dead transition, dead acknowledgment code, missing "Superseded" state) |

### 1.2 What is built

- 5 CRUD endpoints in `document-service` (create with auto doc_number, read, update — draft only, soft-delete — non-approved only, list)
- 5 workflow endpoints (submit-for-review, approve with e-sign + SHA-256, reject, distribution-list management, due-for-review query)
- 1 read-only version history endpoint (`GET /{document_id}/versions`)
- 4-state state machine (draft → under_review → approved → obsolete) with strict transition validation
- Tenant isolation enforced at the query level via JWT `tenant_id`
- 14 E2E tests covering the implemented lifecycle (requires Postgres + Docker)
- 8 unit tests (incomplete coverage)
- Health checks (`/health/live`, `/health/ready` with DB ping)

### 1.3 What is NOT built (vs. industry baseline)

Of MasterControl's 5 core modules (Documents, Audit, CAPA, Supplier, Training):
- **Documents** — partially built; missing version creation, file handling, acknowledgment, events
- **Audit** — 0% built
- **CAPA** — 0% built
- **Supplier** — 0% built
- **Training** — 0% built

Of MasterControl's interconnected event flows:
- Document Approved → Training auto-assign: **not wired**
- Audit Finding → CAPA auto-create: **not wired** (CAPA service doesn't exist)
- Event Analyzer cross-event matching: **not implemented**
- Quality Event → CAPA escalation: **not wired** (Quality Event service doesn't exist)

### 1.4 Critical issues requiring immediate attention

1. **ORM column drift:** `last_rejection_reason` exists in migration 002 but is missing from the `Document` SQLAlchemy model. Reads and writes silently fail.
2. **Dead transition:** `create_new_version` is defined in `VALID_TRANSITIONS` as valid from `approved`, but no handler method or API endpoint exists. The entire revision lifecycle is broken.
3. **Dead acknowledgment code:** `document_acknowledgments` table and model exist, but no API, no service, no repository. The required acknowledgment workflow cannot execute.
4. **Missing state:** Industry-standard `Superseded` state is absent — only 4 states exist (`draft`, `under_review`, `approved`, `obsolete`).
5. **No event emission:** `aiokafka` is installed, `kafka_bootstrap_servers` is configured, but zero events are published on any lifecycle transition.
6. **No audit trail emission:** `audit_service_url` is configured but no events are sent — a 21 CFR Part 11 blocker.
7. **No file handling:** `file_service_url` and `file_id` exist in the model, but there are no upload/download endpoints — documents have no content.
8. **No notifications:** `notification_service_url` is configured but never called — reviewers and approvers never receive task notifications.

---

## 2. Methodology

### 2.1 Comparison framework

For each capability, this document presents three columns:

| **MasterControl (Industry)** | **TrackWise / FreeQMS** | **RainerQMS Code** |
|---|---|---|

The reference column is MasterControl because it has the richest UI evidence and is the dominant QMS in life sciences.

### 2.2 Status legend

| Symbol | Meaning |
|---|---|
| ✅ | Implemented and matches industry parity |
| ⚠️ | Partially implemented (storage exists, workflow incomplete) |
| 🔴 | Industry-standard capability that is not implemented |
| ❌ | Not implemented and not expected (mutual omission) |
| 🐞 | Implemented but broken / has defects |

### 2.3 Evidence basis

All code claims are based on the `document-service` audit covering:
- `app/domain/services.py` — state machine and business logic
- `app/infra/db/models.py` — SQLAlchemy ORM models
- `migrations/versions/001_initial_schema.py` — initial DB schema
- `migrations/versions/002_*` — subsequent migrations (where `last_rejection_reason` column was added)
- `app/api/v1/routes/documents.py` — REST API routes
- `tests/e2e/` — 14 E2E tests
- `tests/unit/` — 8 unit tests
- Service config — `aiokafka`, `kafka_bootstrap_servers`, `audit_service_url`, `notification_service_url`, `file_service_url`, `workflow_service_url`, `max_document_versions`

---

## 3. Current Codebase Inventory

### 3.1 Endpoints implemented

| Endpoint | Method | Behavior |
|---|---|---|
| `/api/v1/documents` | POST | Create document (auto-generates `doc_number` as `DOC-YYYYMMDD-{random}`); auto-records version 1.0 in `document_versions` table |
| `/api/v1/documents/{id}` | GET | Read document by ID (tenant-scoped) |
| `/api/v1/documents/{id}` | PUT | Update document (only when status = `draft`) |
| `/api/v1/documents/{id}` | DELETE | Soft-delete (only when status ≠ `approved`) |
| `/api/v1/documents` | GET | List documents (tenant-scoped, paginated) |
| `/api/v1/documents/{id}/submit-for-review` | POST | Transition `draft` → `under_review` |
| `/api/v1/documents/{id}/approve` | POST | Transition `under_review` → `approved`; capture e-signature; SHA-256 hash of `{approved_by}:{document_id}:{version}:{signature}` |
| `/api/v1/documents/{id}/reject` | POST | Transition `under_review` → `draft`; store rejection reason (⚠️ broken — column missing from ORM) |
| `/api/v1/documents/{id}/distribution-list` | POST/GET | Add/list distribution members |
| `/api/v1/documents/due-for-review` | GET | List approved documents past their review date |
| `/api/v1/documents/{id}/versions` | GET | List version history (ordered by created_at desc) |
| `/health/live` | GET | Liveness probe |
| `/health/ready` | GET | Readiness probe with DB connection check |

### 3.2 Data model implemented

**Tables (with ORM coverage):**

| Table | Model | Status |
|---|---|---|
| `documents` | `Document` | ⚠️ Most fields covered; `last_rejection_reason` column from migration 002 missing from ORM |
| `document_versions` | `DocumentVersion` | ✅ Complete; stores version snapshots with approval metadata |
| `document_acknowledgments` | `DocumentAcknowledgment` | ⚠️ Table + model exist but **no API/service/repository — dead code** |
| `document_distribution_list` | (inline relationship) | ✅ Add/list functional |

**Document fields present in ORM:**
- `id`, `tenant_id`, `doc_number`, `title`, `type`, `status`, `current_version`, `effective_date`, `review_date`, `owner_id`, `created_at`, `updated_at`, `file_id`, `workflow_instance_id`

**Document fields specified by industry but missing from ORM:**
- `last_rejection_reason` (in DB, not in ORM — broken)
- `change_summary`
- `retention_period`
- `iso_clause_mapping`
- `vault` / `taxonomy_id` / `folder_id`
- `controlled_copies[]`
- `expires_date`
- `moved_to_phase`
- `lifecycle_name`

### 3.3 State machine

```
            ┌─────────────────────┐
            │      draft          │ ◄──────────┐
            └──────────┬──────────┘            │
                       │ submit_for_review     │ reject
                       ▼                       │
            ┌─────────────────────┐            │
            │   under_review      │ ───────────┘
            └──────────┬──────────┘
                       │ approve (e-sign + SHA-256)
                       ▼
            ┌─────────────────────┐
            │     approved        │ ─── create_new_version ──► (DEAD: no handler, no endpoint)
            └──────────┬──────────┘
                       │ obsolete
                       ▼
            ┌─────────────────────┐
            │     obsolete        │
            └─────────────────────┘
```

**Missing states (industry-standard):**
- `Effective` — between Approved and Superseded (industry distinguishes these)
- `Superseded` — when a new version becomes effective and the previous version retires
- `Expired` — when a document passes its expiration date

### 3.4 Tests

| Test Type | Count | Coverage |
|---|---|---|
| E2E | 14 | Full lifecycle (create → submit → approve → reject paths; distribution; due-for-review; versions); requires Postgres + Docker |
| Unit | 8 | Create, submit-for-review, approve happy paths only |

**Missing unit tests:** reject, update, delete, list, due-for-review, distribution, get-versions.

---

## 4. Industry Reference Capability Map

This section enumerates capabilities observed in MasterControl that an industry-trained QMS user expects to find in any QMS — including RainerQMS.

### 4.1 MasterControl module surface

**Core modules (8):** QMS Overview, Document Control, Change Control, Training Management, Audit Management, Risk Management, Quality Event Management, Quality Management.

**Add-ons (5):** Postmarket, Supplier, Regulatory, Clinical, Data & Analytics.

Each module has a personalized dashboard, list views, detail/InfoCard views, and is interconnected via cross-module flows (Document Approved → Training, Audit Finding → CAPA, etc.).

### 4.2 MasterControl capability matrix

| Category | Capability | Industry standard? |
|---|---|---|
| **Dashboard** | Personalized "My X" homepage with task tiles | ✅ |
| | Always-visible left navigation rail | ✅ |
| | Calendar view with drag-and-drop | ✅ |
| **Documents** | Hierarchical taxonomies + folders | ✅ |
| | Document Vaults (release / draft / external) | ✅ |
| | Document InfoCard canonical view with tabs | ✅ |
| | Explorer view with breadcrumbs | ✅ |
| | Collaboration Workspace with comments | ✅ |
| | Controlled Copies tracking | ✅ |
| | Version + Revision (e.g., Rev 04 Version 2) | ✅ |
| | Distribution + acknowledgment | ✅ |
| | E-signature with manifest on gateway export | ✅ |
| | File upload, download, view | ✅ |
| | Periodic review | ✅ |
| **Quality Events** | Forms-Based System (FBS) multi-tab forms | ✅ |
| | Event Analyzer cross-event matching | ✅ |
| | RCA tools (5-Why, Fishbone, Fault Tree, Pareto) | ✅ |
| | Auto-escalate to CAPA | ✅ |
| **CAPA** | 6-step lifecycle | ✅ |
| | F×I risk scoring | ✅ |
| | Source linking (event, audit, complaint, etc.) | ✅ |
| | Effectiveness verification | ✅ |
| | Analytics dashboards (by Department, Product, Disposition) | ✅ |
| **Audit** | 4-tab Audit Workspace (Information / Documentation / Observations / Checklist) | ✅ |
| | Drag-and-drop Audit Calendar | ✅ |
| | Auditor qualification tracking | ✅ |
| | Cascading entity dropdown (supplier picker) | ✅ |
| | Finding classification (Major NC / Minor NC / Observation / OFI) | ✅ |
| | Auto-create CAPA from finding | ✅ |
| **Supplier** | 7-status supplier model | ✅ |
| | Risk Score + Status + Supplier Type columns | ✅ |
| | Advanced Search builder | ✅ |
| | Material/Part linking with auto-disable on status drop | ✅ |
| | Secure Guest Connect for external suppliers | ✅ |
| **Training** | Job Codes as first-class entity | ✅ |
| | Job Code Status matrix (per-employee × per-course heatmap) | ✅ |
| | 5-step training task (Introduction → Materials → Exam → Overview → Sign Off) | ✅ |
| | Trainers / Classes / Trainees as distinct entities | ✅ |
| | Auto-assign on document approval | ✅ |
| | Document release gated on training | ✅ |
| **Platform** | Audit trail (append-only) | ✅ |
| | Notifications (email, in-app) | ✅ |
| | File storage with virus scanning | ✅ |
| | Full-text search | ✅ |
| | E-signature compliance (21 CFR Part 11) | ✅ |

---

## 5. Document Service — Detailed Code vs. Industry Analysis

This is the only implemented module. The comparison below maps each industry capability to its code reality.

### 5.1 Document creation

| Industry capability (MasterControl) | RainerQMS Code |
|---|---|
| Create document with document number scheme (e.g., SOP-0001 sequential) | ⚠️ `DOC-YYYYMMDD-{random}` — not sequential, not prefix-typed |
| Assign document type (SOP, SDS, POL, etc.) with subtype (Quality, etc.) | ⚠️ `type` field exists but enum not enforced; no subtype |
| Place document in Vault (QA-rel, QA-dft, Course Release) | 🔴 Not implemented |
| Place document in Taxonomy/Folder | 🔴 Not implemented |
| Attach main file + supporting attachments | 🔴 `file_id` field exists, no upload endpoint |
| Auto-record version 1.0 | ✅ |
| Capture creator + creation timestamp | ✅ |
| Emit creation event to audit trail | 🔴 `audit_service_url` configured, no emission |

### 5.2 Document editing

| Industry capability | RainerQMS Code |
|---|---|
| Rich text editor with tracked changes | 🔴 No editor; only `content` field |
| Edit only when in Draft status | ✅ Update endpoint enforces `draft` only |
| Track every edit with before/after snapshot | 🔴 No audit trail capture |
| Multi-user collaborative editing | 🔴 Not implemented |

### 5.3 Submit for review

| Industry capability | RainerQMS Code |
|---|---|
| Transition Draft → Under Review | ✅ |
| Notify reviewers | 🔴 `notification_service_url` configured, no call |
| Set review deadline | 🔴 Not implemented |
| Allow comments during review (Collaboration Workspace) | 🔴 Not implemented |
| Allow reviewer to approve, request changes, or reject | ⚠️ Approve and reject only — no "request changes" path |

### 5.4 Approval

| Industry capability | RainerQMS Code |
|---|---|
| Approver(s) receive notification | 🔴 No notification |
| Multi-approver routing (sequential or parallel) | 🔴 Single approver only |
| Re-authentication on signing (21 CFR Part 11 §11.50) | 🔴 No re-auth |
| Signature meaning declaration ("Approved", "Reviewed", etc.) | 🔴 No declaration UX |
| Timestamp (server-generated, UTC) | ✅ |
| Cryptographic link to record | ✅ SHA-256 hash of `{approved_by}:{document_id}:{version}:{signature}` |
| Signature manifest export | 🔴 "Include signature manifest on gateway export" toggle exists in MasterControl; not implemented |
| Audit trail entry for signature | 🔴 No emission |
| Auto-publish event to event bus | 🔴 `aiokafka` installed, no event published |

### 5.5 Effective / Superseded states

| Industry capability | RainerQMS Code |
|---|---|
| Approved document becomes "Effective" on effective_date | 🔴 No `Effective` state; `effective_date` is just a date field |
| Previous version auto-marked "Superseded" | 🔴 No `Superseded` state |
| Master Document List auto-updated | 🔴 No Master Document List entity |
| Distribution notifications sent | 🔴 No notification |
| AI-generated change summary | 🔴 `change_summary` field not in ORM |

### 5.6 Distribution and acknowledgment

| Industry capability | RainerQMS Code |
|---|---|
| Maintain distribution list of users/roles | ✅ Add/list endpoints exist |
| Send acknowledgment request to each distribution list member | 🔴 No notification, no acknowledgment workflow |
| Capture acknowledgment with e-signature | 🐞 **Dead code:** table + model exist, no API/service/repo |
| Track acknowledgment status (Pending / Acknowledged / Overdue) | 🔴 Not implemented |
| Report on acknowledgment compliance | 🔴 Not implemented |

### 5.7 Version control (revision lifecycle)

| Industry capability | RainerQMS Code |
|---|---|
| Initial version recorded | ✅ |
| Read version history | ✅ `GET /{document_id}/versions` |
| Create new version of approved document | 🐞 **Dead transition:** `create_new_version` defined in `VALID_TRANSITIONS` as valid from `approved`, but no handler and no endpoint |
| Auto-increment version number (1.0 → 2.0 or 1.1) | 🔴 No logic |
| Revision letter suffix (Rev A, Rev B) | 🔴 Not implemented |
| Version diff / comparison | 🔴 No endpoint |
| Supersession relationship (Doc A supersedes Doc B) | 🔴 Not implemented |
| Enforce `max_document_versions` limit (config = 100) | 🔴 Config defined, never checked |
| Upload new file with new version | 🔴 No file handling |

### 5.8 Periodic review

| Industry capability | RainerQMS Code |
|---|---|
| Schedule periodic review based on config | ⚠️ `review_date` field exists |
| Identify documents due for review | ✅ `GET /due-for-review` endpoint |
| Reminder cascade (30 / 14 / 7 days before due) | 🔴 No scheduler, no notifications |
| Owner confirms current or initiates revision | 🔴 No confirmation endpoint; revision workflow broken |
| Next review date auto-set | 🔴 Not implemented |

### 5.9 Document obsolescence

| Industry capability | RainerQMS Code |
|---|---|
| Transition to Obsolete (manual or via supersession) | ✅ Transition exists |
| Hide from active search but preserve in archive | 🔴 No search service; obsolete docs still queryable |
| Retain per `retention_period` policy | 🔴 `retention_period` field not in ORM |

### 5.10 Cross-module integration

| Industry capability | RainerQMS Code |
|---|---|
| Document Approved → Training auto-assignment | 🔴 No event published; Training service doesn't exist |
| Document Approved → CAPA closure verification | 🔴 — |
| Document Effective → audit trail event | 🔴 — |
| Document linked to Quality Event / CAPA / Audit Finding | 🔴 No cross-module references in ORM |

### 5.11 Tenant isolation

| Industry capability | RainerQMS Code |
|---|---|
| Schema-per-tenant or row-level tenant scoping | ✅ Tenant ID extracted from JWT and injected into every query |
| Cross-tenant data leak prevention | ✅ Repository layer enforces tenant filter |

**This is the strongest area of the implementation.**

### 5.12 Authorization

| Industry capability | RainerQMS Code |
|---|---|
| RBAC enforcement at endpoint level (role required to approve, reject, etc.) | 🔴 No role checks visible — any authenticated user with valid JWT can approve a document in their tenant |
| Approval signature tied to authorized signer with declared meaning | 🔴 No role gate, no meaning declaration |
| Audit log of authorization decisions | 🔴 No emission |

**This is a 21 CFR Part 11 compliance blocker.**

---

## 6. Missing Modules — Code Reality vs. Industry Expectation

Beyond `document-service`, the codebase has no other modules implemented. Each row below states what an industry user expects vs. the code reality of "not started."

### 6.1 Quality Event Management

| Industry capability (MasterControl) | RainerQMS Code |
|---|---|
| Multi-channel event intake (UI, LIMS, equipment, environmental) | 🔴 Service not started |
| Forms-Based System (FBS) multi-tab forms | 🔴 — |
| Severity classification (Critical / Major / Minor) | 🔴 — |
| Linked records (equipment, document, personnel) | 🔴 — |
| RCA tools (5-Why, Fishbone, Fault Tree, Pareto) | 🔴 — |
| Event Analyzer cross-event matching (Proposed Matches / Confirmed Matches) | 🔴 — |
| Auto-escalate Critical events to CAPA | 🔴 — |
| Client notification flag for NC work | 🔴 — |
| Effectiveness check date | 🔴 — |

### 6.2 CAPA Management

| Industry capability | RainerQMS Code |
|---|---|
| 6-step lifecycle (Identify → Investigate → Plan → Implement → Effectiveness → Close) | 🔴 Service not started |
| Source linking (Quality Event, Audit Finding, Complaint, PT Result, Management Review, Standalone) | 🔴 — |
| Risk scoring (F×I or RPN) | 🔴 — |
| Multi-action records with owner + due date + evidence | 🔴 — |
| AI-suggested root cause | 🔴 — |
| Effectiveness verification at 30/60/90 days | 🔴 — |
| Escalation emails at 7/14/30 days overdue | 🔴 — |
| QM final approval with e-signature | 🔴 — |
| Recurrence monitoring after closure | 🔴 — |
| CAPA analytics (by Department / Product / NCMR Disposition) | 🔴 — |

### 6.3 Audit Management

| Industry capability | RainerQMS Code |
|---|---|
| Audit types (Internal, External: FDA, ISO, Supplier, Client) | 🔴 Service not started |
| 4-tab Audit Workspace (Information / Documentation / Observations / Checklist) | 🔴 — |
| Annual audit plan / risk-based schedule | 🔴 — |
| Drag-and-drop Audit Calendar with event grouping | 🔴 — |
| Auditor qualification tracking | 🔴 — |
| Cascading entity dropdown (Supplier picker) | 🔴 — |
| Checklist (ISO 17025 / custom) | 🔴 — |
| Finding classification (Major NC / Minor NC / Observation / OFI) | 🔴 — |
| Auto-create CAPA from Major/Minor NC | 🔴 — |
| Auditee response collection | 🔴 — |
| Audit report generation (PDF) | 🔴 — |
| Global trending reports | 🔴 — |

### 6.4 Supplier Management

| Industry capability | RainerQMS Code |
|---|---|
| 7-status supplier model | 🔴 Service not started |
| Risk-driven audit frequency | 🔴 — |
| Initial qualification questionnaire | 🔴 — |
| Re-qualification (annual / biannual by criticality) | 🔴 — |
| Approved Supplier List (ASL) | 🔴 — |
| Material/Part/Service linking | 🔴 — |
| Auto-disable material links on status drop | 🔴 — |
| Secure Guest Connect for external suppliers | 🔴 — |
| Multi-filter sidebar | 🔴 — |
| Advanced Search builder | 🔴 — |
| View Supplier InfoCard | 🔴 — |

### 6.5 Training Management

| Industry capability | RainerQMS Code |
|---|---|
| Auto-assignment from document approval | 🔴 Service not started |
| Auto-assignment from role change | 🔴 — |
| 5-step training task (Introduction → Materials → Exam → Overview → Sign Off) | 🔴 — |
| Job Codes as first-class entity | 🔴 — |
| Job Code Status matrix (per-employee × per-course heatmap) | 🔴 — |
| Exam administration + auto-grading | 🔴 — |
| E-signature on completion | 🔴 — |
| Trainers / Classes / Trainees as distinct entities | 🔴 — |
| Bulk import of training records | 🔴 — |
| Multi-supervisor completion notification | 🔴 — |
| Training deficiency flagging | 🔴 — |
| Document release gated on training | 🔴 — |
| Continuous verification of tasks | 🔴 — |

### 6.6 Equipment & Calibration Management

| Industry capability | RainerQMS Code |
|---|---|
| Equipment register with full lifecycle | 🔴 Service not started |
| Calibration scheduling (time or usage-based) | 🔴 — |
| Reminder notifications (30/14/7/1 day) | 🔴 — |
| As-found / as-left readings | 🔴 — |
| Measurement uncertainty | 🔴 — |
| Auto-create quality event on OOT | 🔴 — |
| Calibration certificate generation | 🔴 — |
| Standards traceability tree | 🔴 — |
| Digital usage logbook | 🔴 — |

### 6.7 Other modules (Environmental Monitoring, PT, Complaint, Risk, Management Review, Analytics)

All 6 remaining modules: **0% implemented.**

---

## 7. Codebase Defects & Inconsistencies

### 7.1 Showstopper defects

| # | Defect | File / Location | Symptom | Severity |
|---|---|---|---|---|
| D-1 | `last_rejection_reason` column drift | DB has it (migration 002); ORM `Document` model does not | Reject endpoint silently fails to persist rejection reason | 🐞 Critical |
| D-2 | Dead transition `create_new_version` | Defined in `VALID_TRANSITIONS` in `services.py`; no handler, no API endpoint | Entire revision lifecycle is broken — only v1.0 is ever recorded | 🐞 Critical |
| D-3 | Dead acknowledgment code | `document_acknowledgments` table + `DocumentAcknowledgment` model exist; no API, no service, no repository | Spec/industry-required acknowledgment workflow cannot execute | 🐞 Critical |
| D-4 | Missing `Superseded` state | Only 4 states in code (`draft`, `under_review`, `approved`, `obsolete`) — no `Superseded` state and no transition logic | ISO 17025 Clause 8.3.2 traceability incomplete; previous versions cannot be properly marked | 🐞 Critical |

### 7.2 Configuration without implementation

These configs are defined and consumed at startup, but the code that should use them is missing entirely:

| Config | Purpose | Status |
|---|---|---|
| `kafka_bootstrap_servers` | Kafka broker endpoint for event emission | 🔴 Zero events emitted; `aiokafka` installed but unused |
| `audit_service_url` | Audit trail service endpoint | 🔴 No audit events sent |
| `notification_service_url` | Notification service endpoint | 🔴 No notifications sent |
| `file_service_url` | File service endpoint | 🔴 No upload/download |
| `workflow_service_url` | Temporal workflow service endpoint | 🔴 No Temporal calls; workflow hardcoded in code |
| `max_document_versions` | Limit (default 100) | 🔴 Never checked |

### 7.3 Test coverage gaps

| Test type | Endpoint | Status |
|---|---|---|
| Unit | Create document | ✅ |
| Unit | Submit for review | ✅ |
| Unit | Approve | ✅ |
| Unit | Reject | 🔴 Missing |
| Unit | Update | 🔴 Missing |
| Unit | Delete | 🔴 Missing |
| Unit | List | 🔴 Missing |
| Unit | Due-for-review | 🔴 Missing |
| Unit | Distribution list add/list | 🔴 Missing |
| Unit | Get versions | 🔴 Missing |
| E2E | Full lifecycle (14 tests) | ✅ Comprehensive |

### 7.4 ORM ↔ migration consistency check

| Column in migration 002 | In ORM `Document`? |
|---|---|
| `last_rejection_reason` (text) | 🔴 Missing — **Defect D-1** |

(Any further migration-vs-ORM drift would need full file inspection — only D-1 is in evidence.)

---

## 8. Platform & Infrastructure Service Status

Industry-standard QMS deployments rely on a set of supporting platform services. Below is the status of each in the current codebase.

| Service | Industry Expectation | Code Status |
|---|---|---|
| **API Gateway** | Kong / AWS API GW for routing, rate limiting, auth, tenant resolution | 🔴 Not in evidence |
| **Auth Service** | Keycloak / OIDC provider | ⚠️ JWT consumed downstream; no Keycloak server reference visible |
| **Tenant Service** | Tenant provisioning, configuration, lifecycle | ⚠️ `tenant_id` consumed via JWT; provisioning service not visible |
| **Notification Service** | Email, SMS, in-app, webhook delivery | 🔴 `notification_service_url` configured, never called |
| **Workflow Engine** | Temporal for long-running workflows | 🔴 `workflow_service_url` + `workflow_instance_id` configured, no Temporal calls |
| **File Service** | S3 + virus scanning + signed URLs | 🔴 `file_service_url` configured, no upload/download |
| **Search Service** | OpenSearch full-text + cross-module search | 🔴 Not in evidence |
| **Audit Trail Service** | Append-only audit log (21 CFR Part 11) | 🔴 `audit_service_url` configured, no events emitted |
| **AI/ML Service** | Trend detection, RCA suggestion, exam generation | 🔴 Not in evidence (Phase 3 in roadmap) |
| **E-Signature Module** | 21 CFR Part 11 signing with re-auth, meaning declaration, manifest | ⚠️ SHA-256 hash recorded on approval; no manifest, no re-auth, no meaning UX |

### 8.1 Event bus status

Industry-standard cross-module event flows expected:

| Source → Target | Action | Code Status |
|---|---|---|
| Document Approved → Training Service | Auto-assign training | 🔴 Not wired; Training service doesn't exist |
| Document Approved → Notification Service | Notify owner + distribution | 🔴 Not wired |
| Quality Event Created → CAPA Service | Auto-create CAPA | 🔴 Neither service exists |
| Audit Finding Created → CAPA Service | Create CAPA from NC | 🔴 Neither service exists |
| Calibration Failed → Quality Event Service | Create NC | 🔴 Neither service exists |
| Environmental Excursion → Quality Event Service | Create deviation | 🔴 Neither service exists |
| PT Result Unsatisfactory → CAPA Service | Initiate CAPA | 🔴 Neither service exists |
| CAPA Overdue → Notification Service | Escalate to management | 🔴 Neither service exists |
| Training Overdue → Notification Service | Alert employee + supervisor | 🔴 Neither service exists |

**The entire interconnected QMS theme — the central value proposition of an integrated quality management system — is not wired in code.**

---

## 9. Compliance Readiness Assessment

The industry references all claim 21 CFR Part 11, ISO 17025, and ALCOA+ compliance as table stakes. The current codebase does not meet these standards.

### 9.1 21 CFR Part 11 — Electronic Records & Signatures

| Requirement | Industry Standard | Code Status |
|---|---|---|
| §11.10(a) — Validation of system | Validated, with IQ/OQ/PQ documentation | 🔴 No validation package |
| §11.10(b) — Records protection | Append-only audit log; immutable history | 🔴 No audit trail emission |
| §11.10(c) — Records retention | Configurable retention policies | 🔴 `retention_period` field not in ORM |
| §11.10(d) — Limit access to authorized individuals | RBAC enforced at endpoint level | 🔴 No role checks visible |
| §11.10(e) — Secure, computer-generated, time-stamped audit trails | All operations logged with timestamp | 🔴 No audit trail emission |
| §11.10(f) — Operational system checks | Workflow gates prevent invalid transitions | ✅ State machine enforces transitions |
| §11.10(g) — Authority checks | Role-based authorization on signing | 🔴 No role gate |
| §11.10(h) — Device checks | n/a for cloud | n/a |
| §11.10(i) — Persons have education, training, experience | Training records linked to system access | 🔴 No training service |
| §11.10(j) — Accountability policies | Audit trail of accountability | 🔴 No audit trail |
| §11.10(k) — Document control | Document control system | ⚠️ Partial |
| §11.50(a) — Signature manifestations include name, date/time, meaning | Manifested in record | ⚠️ Hash recorded; no meaning declaration |
| §11.50(b) — Signature manifestations in subsequent printouts | Exportable manifest | 🔴 No export |
| §11.70 — Signature/record linking | Cryptographic link cannot be excised | ✅ SHA-256 hash |
| §11.100(a) — Signatures unique to one individual | User identity verification | ⚠️ Captured at login; no re-auth on signing |
| §11.100(b) — Signature verification before use | Re-authentication | 🔴 No re-auth |
| §11.200(a)(1) — Two distinct components | UserID + password re-entry | 🔴 No re-entry on signing |
| §11.200(a)(2) — Used in series | Either component requires the other | 🔴 — |
| §11.200(a)(3) — Used by genuine owner | Anti-impersonation controls | ⚠️ JWT only |
| §11.300 — Controls for IDs/passwords | Periodic rotation, account lockout, etc. | n/a (auth service responsibility) |

**Summary:** Current code is **not 21 CFR Part 11 compliant** today. Closing the audit trail emission, signature manifest, role gate, and re-auth gaps are mandatory for any regulated lab to use the system.

### 9.2 ALCOA+ — Data Integrity

| Principle | Industry Enforcement | Code Status |
|---|---|---|
| **Attributable** | Every record linked to user | ⚠️ User captured at approve; not on all operations (no audit trail) |
| **Legible** | Structured electronic forms | ✅ Structured forms |
| **Contemporaneous** | Real-time entry; late entry flagging | ⚠️ Timestamps on approve only |
| **Original** | First-entry preserved; no overwriting | ⚠️ Soft-delete preserves; updates overwrite without before/after capture |
| **Accurate** | Input validation; range checks | ✅ Pydantic validation |
| **Complete** | Required field enforcement; workflow gates | ⚠️ Partial; state machine present, field-level required-field enforcement varies |
| **Consistent** | Controlled vocabularies; enums | ⚠️ Some enums defined, not all enforced |
| **Enduring** | Cloud storage; backups; retention | ✅ Postgres + backup assumed |
| **Available** | Role-based access; search; API | ⚠️ API present; search service not present; RBAC not enforced |

**Summary:** Current code is **partially ALCOA+ compliant** — Legible, Accurate, and Enduring are met; Attributable, Contemporaneous, Original, Complete, and Consistent have gaps that must close.

### 9.3 ISO 17025 — Document Control (Clause 8.3.2)

| Requirement | Industry Standard | Code Status |
|---|---|---|
| Documents uniquely identified | Sequential doc numbers (SOP-0001, etc.) | ⚠️ `DOC-YYYYMMDD-{random}` is unique but not sequential |
| Revision status identified | Rev letter + version number | 🔴 No revision letter; only version number |
| Documents reviewed, updated, re-approved | Periodic review workflow | ⚠️ Review-due query exists; revision workflow broken |
| Changes identified | Change request linkage | 🔴 Not implemented |
| Current versions available at points of use | Distribution + acknowledgment | 🐞 Acknowledgment dead code |
| Documents legible and readily identifiable | Structured metadata | ✅ |
| Documents of external origin identified and controlled | External doc type | ⚠️ `type` field has "External" option; no separate workflow |
| Obsolete documents protected from unintended use | Obsolete state hides from active use | ⚠️ Obsolete state exists; no search service to hide from |

---

## 10. UI & UX Implementation Gap

The codebase is API-only at present. The frontend is either not started or is outside the audited scope. Industry references all have polished UIs that go far beyond bare API access.

### 10.1 Dashboard UI

| Industry pattern (MasterControl) | Code Status |
|---|---|
| Personalized "My MasterControl" homepage | 🔴 No UI in evidence |
| MY TASKS / MY SUBSCRIPTIONS / MY TRAINING FOLDER / MY RECENT tiles | 🔴 — |
| START TASK quick-create button | 🔴 — |
| Left navigation rail | 🔴 — |
| Date/time display | 🔴 — |

### 10.2 Document UI

| Industry pattern | Code Status |
|---|---|
| Hierarchical Explorer with breadcrumbs | 🔴 No UI |
| List/Grid view toggle | 🔴 — |
| Document InfoCard canonical view (Information / Training / Controlled Copies / Attachments & Links / Custom Fields / History / Status / Versions tabs) | 🔴 — |
| Collaboration Workspace with comments thread | 🔴 — |
| Add Comments dialog | 🔴 — |
| Status banner | 🔴 — |
| Main File area with download/view/link icons | 🔴 — |
| Date Information grid | 🔴 — |

### 10.3 Audit / CAPA / Supplier / Training UI

All 🔴 — no UI in evidence for any of the missing modules.

---

## 11. Critical Issues Ranked by Priority

### 11.1 Tier 1 — Showstopper bugs (fix immediately)

| Rank | Issue | Effort | Why critical |
|---|---|---|---|
| 1 | **D-1: ORM column drift** — `last_rejection_reason` missing from `Document` model | Hours | Silent read/write failures; reject reason is lost |
| 2 | **D-2: Dead transition `create_new_version`** — listed in `VALID_TRANSITIONS` with no handler | Days | Revision lifecycle is broken; only v1.0 is ever created |
| 3 | **D-3: Dead acknowledgment code** — table + model with no API/service/repo | Days | Required workflow cannot execute |
| 4 | **D-4: Missing `Superseded` state** — only 4 states; industry standard is 5 | Days | ISO 17025 Clause 8.3.2 traceability incomplete |

### 11.2 Tier 2 — Interconnect blockers (next 30 days)

| Rank | Issue | Why critical |
|---|---|---|
| 5 | **No Kafka event emission on document approval** | Blocks all downstream services (training, notification, audit) — breaks the entire interconnected QMS value proposition |
| 6 | **No audit trail emission** | 21 CFR Part 11 §11.10(e) non-compliance — pilot labs cannot accredit |
| 7 | **No file upload/download** | Documents have no content — Module 1 is unusable for real SOPs |
| 8 | **No notification emission** | Reviewers/approvers never know they have tasks; no workflow can actually run end-to-end |
| 9 | **No RBAC enforcement** | Anyone with a valid JWT can approve anything in their tenant — 21 CFR Part 11 §11.10(g) non-compliance |

### 11.3 Tier 3 — Phase 1 MVP completeness (60–90 days)

| Rank | Issue | Why critical |
|---|---|---|
| 10 | **Quality Event service not built** | Required for Phase 1 MVP |
| 11 | **CAPA service not built** | Required for Phase 1 MVP |
| 12 | **Audit service not built** | Required for Phase 1 MVP |
| 13 | **Training service not built** | Required for Phase 1 MVP |
| 14 | **Equipment service not built** | Required for Phase 1 MVP — RainerQMS differentiator |
| 15 | **Multi-approver approval routing** | Industry standard; current code is single-approver |
| 16 | **Periodic review reminder cascade (30/14/7 days)** | Required by workflow |
| 17 | **Change request linkage** | Required by workflow |
| 18 | **E-signature manifest export** | 21 CFR Part 11 §11.50(b) |
| 19 | **E-signature meaning declaration UX + re-auth on signing** | 21 CFR Part 11 §11.200(a)(1) |

### 11.4 Tier 4 — Industry pattern gaps (Phase 2 onwards)

| Rank | Issue | Why important |
|---|---|---|
| 20 | **Event Analyzer pattern** | Cross-event matching for trend detection — central to MasterControl, missing from RainerQMS |
| 21 | **Job Code Status matrix** | Compliance UX gap — auditors expect exactly this view |
| 22 | **Document Vaults / Taxonomies / Folders** | Required for >1,000 documents |
| 23 | **Audit Calendar drag-and-drop** | Industry-standard scheduling UX |
| 24 | **Secure Guest Connect** | Lightweight external supplier collaboration |
| 25 | **Advanced Search builder** | Cross-module search with Field + Operator + Value + Logic |
| 26 | **Document InfoCard canonical view** | Standard record view pattern |
| 27 | **Controlled Copies tracking** | Paper-hybrid lab requirement |
| 28 | **Auto-disable material links on supplier status drop** | Risk containment |
| 29 | **Forms-Based System (FBS) multi-tab form pattern** | Standard quality event UX |

---

## 12. Recommended 90-Day Implementation Plan

A pragmatic 90-day plan to bring the codebase to "MVP-pilot-ready" state on the Document module, then start Quality Events.

| Week | Focus | Deliverables |
|---|---|---|
| **1** | Fix showstoppers D-1 to D-4 | ORM column fix; `Superseded` state added with transition logic; acknowledgment dead code either wired or removed; documented `Effective` state design |
| **2–3** | Implement `create_new_version` end-to-end | Handler method; API endpoint `POST /api/v1/documents/{id}/versions`; version increment logic (1.0 → 2.0); file linkage to new version |
| **4–5** | Wire Kafka event emission | Events: `Document.Created`, `Document.SubmittedForReview`, `Document.Approved`, `Document.Rejected`, `Document.Effective`, `Document.Superseded`, `Document.Obsolete`, `Document.VersionCreated`; publish via `aiokafka` to `document-events` topic |
| **6** | Wire audit trail emission | Every create / update / approve / reject / sign / delete operation publishes an event to `audit-trail-events` topic for the audit-trail-service to consume |
| **7–8** | Implement file-service integration | Upload endpoint with multipart; virus-scan stub call; signed URL download endpoint; attach file to document version |
| **9** | Wire notification emission | Notification calls on submit-for-review (notify reviewers), approve (notify owner + distribution), reject (notify author), periodic-review-due (notify owner) |
| **10** | Implement RBAC enforcement | Role gate decorators on approve, reject, delete; role required for create varies by document type; `403 Forbidden` for unauthorized |
| **11** | Wire document acknowledgment workflow | API + service + repo for the existing model; acknowledgment notification to distribution list members; e-signature on acknowledge; acknowledgment status reporting |
| **12** | Approval routing + periodic review cascade | Multi-approver sequential routing; periodic review reminders at 30/14/7 days; auto-set next review date on confirm |
| **13** | E-signature compliance hardening | Re-auth modal on signing; signature meaning declaration UX; signature manifest export endpoint |
| **14–15** | Stand up `quality-event-service` skeleton | Service scaffold; entity + ORM; CRUD endpoints; state machine; tenant isolation; first E2E tests |

### 12.1 Test coverage targets

| Test Type | Target |
|---|---|
| Unit tests for `document-service` | 100% endpoint coverage (currently 8 of ~15 = ~50%) |
| E2E tests for `document-service` | Maintain 14 + add tests for new endpoints (versions, acknowledge, file upload/download) |
| Integration tests | Add tests for Kafka event publication, audit trail emission, notification emission |
| Compliance tests | Add tests verifying 21 CFR Part 11 signature manifest contents, audit trail completeness |

---

## Appendix A — Glossary

| Term | Meaning |
|---|---|
| **ALCOA+** | Data integrity principles: Attributable, Legible, Contemporaneous, Original, Accurate, plus Complete, Consistent, Enduring, Available |
| **ASL** | Approved Supplier List |
| **CAPA** | Corrective Action / Preventive Action |
| **FBS** | Forms-Based System (MasterControl's multi-tab quality-event form pattern) |
| **InfoCard** | MasterControl's canonical single-record view |
| **IQ/OQ/PQ** | Installation / Operational / Performance Qualification — software validation lifecycle |
| **MOC** | Management of Change |
| **NC** | Non-Conformance |
| **NCMR** | Non-Conforming Material Report |
| **OFI** | Opportunity for Improvement (audit finding classification) |
| **OOS / OOT** | Out-of-Spec / Out-of-Tolerance |
| **ORM** | Object-Relational Mapper (SQLAlchemy in this codebase) |
| **PT** | Proficiency Testing |
| **QMS** | Quality Management System |
| **RBAC** | Role-Based Access Control |
| **RCA** | Root Cause Analysis |
| **RPN** | Risk Priority Number (Severity × Occurrence × Detectability) |
| **SCAR** | Supplier Corrective Action Request |
| **SOP** | Standard Operating Procedure |

## Appendix B — File Reference Index

| File Path | Purpose | Coverage in this Doc |
|---|---|---|
| `app/api/v1/routes/documents.py` | REST endpoints for documents | Section 3.1, 5 |
| `app/domain/services.py` | Business logic + state machine (`VALID_TRANSITIONS`, `create_document`, `approve_document`, etc.) | Section 3.3, 5.4, 7.1 |
| `app/infra/db/models.py` | SQLAlchemy ORM models (`Document`, `DocumentVersion`, `DocumentAcknowledgment`) | Section 3.2, 7.1 |
| `migrations/versions/001_initial_schema.py` | Initial DB schema including `documents`, `document_versions`, `document_acknowledgments` tables | Section 3.2 |
| `migrations/versions/002_*` | Added `last_rejection_reason` column (not propagated to ORM — defect D-1) | Section 7.1 |
| `tests/e2e/` | 14 E2E tests covering implemented lifecycle | Section 3.4 |
| `tests/unit/` | 8 unit tests covering happy paths | Section 3.4, 7.3 |
| Config (env / settings) | `kafka_bootstrap_servers`, `audit_service_url`, `notification_service_url`, `file_service_url`, `workflow_service_url`, `max_document_versions` | Section 7.2, 8 |

---

*End of RainerQMS Codebase vs. Industry References — Implementation Gap Analysis*
