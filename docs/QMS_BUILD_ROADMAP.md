# RainerQMS — Build Roadmap & Remaining Implementation Guide

**Generated:** 2026-05-13  
**Stack:** FastAPI + SQLAlchemy 2.0 async + Alembic (backend) | Next.js 15 App Router + TanStack Query + shadcn/ui (frontend)  
**Source of truth for APIs:** `docs/APIs/qms/*.json` and `docs/APIs/platform/*.json`

---

## 1. What Is Already Complete (Phases 1–10)

All ten binding phases from the original prompt are confirmed complete in staged code.

| Phase | Description | Evidence |
|-------|-------------|----------|
| 1 | Gateway proxies for all QMS + analytics routes | `gateway-service/app/api/v1/__init__.py` registers all 7 routers |
| 2 | FE client path fixes — `/capas`, `/equipment`, `severity` | `lib/api/services/qms.ts` — no `/capa/capas`, no `/assets`, no `transition` |
| 3 | Paginated response normalization for CAPA + equipment | `normalizePaginated()` in `qms.ts` handles both `{items}` and `{data, pagination}` envelopes |
| 4 | Document module — reject, versions, make-obsolete, distribution, due-for-review | `documents/[id]/page.tsx` has three tabs; training assigned on approve |
| 5 | CAPA detail page — 6-step lifecycle, root cause, actions, verify, close | `capa/[id]/page.tsx` fully wired |
| 6 | Quality Events — edit, close, delete, escalate-to-CAPA, summary widget | `quality-events/[id]/page.tsx`; `QualityEventsSummaryWidget.tsx` |
| 7 | Equipment — calibration form, failed-cal → quality event, decommission, widget | `equipment/[id]/page.tsx`; `EquipmentDueCalibrationWidget.tsx` |
| 8 | Training — my-training page, complete with e-signature, overdue widget | `training/my-training/page.tsx`; `TrainingOverdueWidget.tsx` |
| 9 | ENV_REFERENCE.md + all `.env.example` files updated | `ENV_REFERENCE.md` at repo root |
| 10 | Permission matrix, UI guards on all QMS actions | `docs/permission-matrix.md`; guards in all detail pages |

---

## 2. Remaining Gaps — Immediate (P1)

These are bugs and missing hooks in the already-built modules that need to be fixed before the new modules are built.

### 2.1 Equipment: `update` function missing from FE client

**File:** [frontend/apps/web/lib/api/services/qms.ts](frontend/apps/web/lib/api/services/qms.ts)  
**Gap:** `equipmentApi` has no `update` method. The backend exposes `PATCH /api/v1/equipment/{id}` (confirmed in `docs/APIs/qms/equipment-service.json`, path `/api/v1/equipment/{equipment_id}`, method `patch`).

**Fix — add to `equipmentApi`:**
```ts
update: (id: string, data: Partial<{
  name: string;
  description: string | null;
  location: string | null;
  department: string | null;
  assigned_to: string | null;
  notes: string | null;
  requires_calibration: boolean;
  calibration_frequency_days: number | null;
}>) =>
  qmsEquipmentApiClient
    .patch<unknown>(`/equipment/${id}`, data)
    .then((r) => unwrapSuccessData<Equipment>(r.data)),

delete: (id: string) =>
  qmsEquipmentApiClient
    .delete<unknown>(`/equipment/${id}`)
    .then((r) => unwrapSuccessData<{ message: string }>(r.data)),
```

**Wire to UI:** Add an "Edit" dialog on the equipment detail page and a "Delete" button (with confirmation) gated behind `equipment:write`.

### 2.2 Equipment: No calibration history shown on detail page

**File:** [frontend/apps/web/app/(qms)/qms/equipment/[id]/page.tsx](frontend/apps/web/app/(qms)/qms/equipment/[id]/page.tsx)  
**Gap:** The equipment detail page shows `next_calibration_date` and an action button, but shows no calibration history. The `calibrate` endpoint returns the updated `EquipmentResponse`, but there is no `GET /equipment/{id}/calibration-records` endpoint in the current `equipment-service.json`.

**Decision needed — choose one:**
- **Option A (preferred):** Add `GET /api/v1/equipment/{id}/calibration-records` to the equipment service backend, returning a list of past calibrations. Then add a Calibration History tab on the detail page.
- **Option B:** Use platform audit logs filtered by `resource_type=equipment` and `resource_id={id}` to show the history, as a stopgap until Option A is built.

**Backend work (Option A):**
1. Add `CalibrationRecord` model to `backend/qms/equipment-service/app/infra/db/models.py`
2. Add `GET /api/v1/equipment/{equipment_id}/calibration-records` route
3. Update `RecordCalibrationRequest` to include the full fields from Phase 7 spec (technician, standards, as-found/as-left readings, uncertainty)
4. Update OpenAPI doc at `docs/APIs/qms/equipment-service.json`

### 2.3 CAPA: `updateAction` not in API (backend gap)

**Gap:** Phase 2 spec included `PATCH /capas/{id}/actions/{action_id}` (update a CAPA action). This path **does not exist** in `docs/APIs/qms/capa-service.json`. The CAPA service only has `GET`, `POST` (actions), and `POST /{action_id}/complete`.

**Fix — either:**
- Add `PATCH /api/v1/capas/{capa_id}/actions/{action_id}` to `backend/qms/capa-service/app/api/v1/routes/capas.py` and update `docs/APIs/qms/capa-service.json`
- Or decide action updates are out of scope and leave as-is

### 2.4 Audit Log: No frontend viewer

**API:** `GET /api/v1/audit/logs` + `GET /api/v1/audit/logs/{log_id}` (confirmed in `docs/APIs/platform/audit-service.json`)  
**Gateway:** `audit_proxy_router` is registered — the route works.  
**Gap:** No frontend page to view audit logs.

The `AuditLogResponse` schema fields:
```
id, tenant_id, user_id, action, resource_type, resource_id, 
ip_address, user_agent, metadata (JSON), severity, source_service, event_id, created_at
```

**What to build:**
1. Add `auditApi` in a new `lib/api/services/audit.ts` (or the platform client):
   ```ts
   export const auditApi = {
     list: (params?: {
       tenant_id?: string; user_id?: string; action?: string;
       resource_type?: string; resource_id?: string; severity?: string;
       from_date?: string; to_date?: string; page?: number; page_size?: number;
     }) => platformApiClient.get('/audit/logs', { params })
         .then(r => normalizePaginated(r.data)),
     get: (id: string) => platformApiClient.get(`/audit/logs/${id}`)
         .then(r => unwrapSuccessData(r.data)),
   };
   ```
2. Build `app/(admin)/admin/audit-logs/page.tsx` with:
   - Filter bar: `resource_type`, `action`, `severity`, date range, user ID
   - Table: `created_at | action | resource_type | resource_id | user_id | severity`
   - Click row → open detail dialog showing full `metadata` JSON
3. Add an "Audit Trail" tab on document, CAPA, and quality-event detail pages that calls `GET /audit/logs?resource_type=document&resource_id={id}` to show inline history for that specific record.

### 2.5 Audit Service: Compliance field gap (ALCOA+)

**File:** `docs/APIs/platform/audit-service.json` — `AuditLogResponse` schema  
**Gap:** Schema stores changes in `metadata` JSON blob. Master doc requires `before_value` / `after_value` at the column level for 21 CFR Part 11 compliance. Auditors need to verify exactly what changed.

**Fix:**
1. Add `before_value` (JSONB nullable) and `after_value` (JSONB nullable) columns to the `audit_logs` table in `backend/platform/audit-service`
2. Create Alembic migration
3. Update `AuditLogResponse` Pydantic schema + `docs/APIs/platform/audit-service.json`
4. Update QMS services (document-service, capa-service, quality-event-service) to pass `before_value`/`after_value` in their audit log publish calls
5. Update the audit log viewer UI to show a before/after diff

---

## 3. Next New QMS Modules (Phase C) — Build Order

These are the nine modules documented but not yet implemented as microservices. Build them **in this priority order** based on regulatory importance and inter-module dependencies.

### Priority 1 — QMS Audit Management Module (Module 4)

> Do not confuse with the platform `audit-service` which is a tamper-proof log store. This is the **ISO-standard audit program**: scheduling audits, executing checklists, recording findings, raising CAPAs from findings.

**New service:** `backend/qms/audit-management-service/`

**Database entities:**
```
AuditProgram: id, tenant_id, name, year, status, created_by, created_at
AuditSchedule: id, program_id, tenant_id, audit_type (internal/supplier/regulatory),
               scope, auditor_ids[], auditee_dept, planned_date, status
AuditFinding: id, schedule_id, tenant_id, finding_type (major/minor/observation/ofi),
              description, iso_clause, evidence, capa_id (nullable), status
AuditChecklist: id, schedule_id, requirement, response (yes/no/na), notes
```

**API endpoints to build:**

| Method | Path | Description | Permission |
|--------|------|-------------|------------|
| GET | `/api/v1/audit-programs` | List programs | `audit:read` |
| POST | `/api/v1/audit-programs` | Create program | `audit:write` |
| GET | `/api/v1/audit-programs/{id}` | Get program | `audit:read` |
| GET | `/api/v1/audit-schedules` | List schedules | `audit:read` |
| POST | `/api/v1/audit-schedules` | Schedule an audit | `audit:write` |
| GET | `/api/v1/audit-schedules/{id}` | Get schedule | `audit:read` |
| PATCH | `/api/v1/audit-schedules/{id}` | Update | `audit:write` |
| POST | `/api/v1/audit-schedules/{id}/start` | Start audit | `audit:write` |
| POST | `/api/v1/audit-schedules/{id}/complete` | Complete audit | `audit:approve` |
| GET | `/api/v1/audit-schedules/{id}/findings` | List findings | `audit:read` |
| POST | `/api/v1/audit-schedules/{id}/findings` | Add finding | `audit:write` |
| PATCH | `/api/v1/audit-schedules/{id}/findings/{finding_id}` | Update finding | `audit:write` |
| POST | `/api/v1/audit-schedules/{id}/findings/{finding_id}/raise-capa` | Create CAPA from finding | `audit:write` |

**Gateway:** Add `audit_mgmt_proxy.py` + register in `__init__.py` at `/api/v1/audit-programs` and `/api/v1/audit-schedules`.

**Frontend pages:**
- `app/(qms)/qms/audit/page.tsx` — list programs + schedules
- `app/(qms)/qms/audit/[id]/page.tsx` — schedule detail with findings checklist
- Component: `RaiseCapaFromFindingDialog` that pre-fills `source_type: "audit_finding"`

---

### Priority 2 — Customer Complaints Module (Module 11)

Closely related to Quality Events. High regulatory visibility.

**New service:** `backend/qms/complaint-service/`

**Database entities:**
```
Complaint: id, tenant_id, complaint_number, customer_name, customer_ref,
           product_lot, received_date, description, complaint_type,
           severity, status (open/under_review/resolved/closed),
           root_cause, corrective_action, capa_id, closed_at,
           regulatory_reportable (bool), reported_to_reg (bool), created_by
```

**API endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/complaints` | List (paginated, filterable by status/severity/reportable) |
| POST | `/api/v1/complaints` | Create |
| GET | `/api/v1/complaints/{id}` | Detail |
| PATCH | `/api/v1/complaints/{id}` | Update |
| POST | `/api/v1/complaints/{id}/close` | Close with resolution |
| POST | `/api/v1/complaints/{id}/escalate-capa` | Create CAPA from complaint |
| POST | `/api/v1/complaints/{id}/mark-reported` | Flag as reported to regulator |

**Frontend pages:**
- `app/(qms)/qms/complaints/page.tsx` — list with "Regulatory Reportable" filter
- `app/(qms)/qms/complaints/[id]/page.tsx` — detail with regulatory flags

---

### Priority 3 — Risk Management Module (Module 9)

**New service:** `backend/qms/risk-service/`

**Database entities:**
```
RiskRegister: id, tenant_id, name, description, process_area, created_by
Risk: id, register_id, tenant_id, risk_number, title, description, category,
      likelihood (1-5), impact (1-5), detectability (1-5), rpn (computed),
      status, owner_id, mitigation_plan, residual_likelihood, residual_impact,
      residual_rpn, review_date, capa_id
```

**API endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/risks` | List risks (filter by register, status, rpn threshold) |
| POST | `/api/v1/risks` | Create risk |
| GET | `/api/v1/risks/{id}` | Detail |
| PATCH | `/api/v1/risks/{id}` | Update (recalculates RPN = likelihood × impact × detectability) |
| POST | `/api/v1/risks/{id}/mitigate` | Record mitigation |
| POST | `/api/v1/risks/{id}/accept` | Accept risk |
| GET | `/api/v1/risk-registers` | List registers |
| POST | `/api/v1/risk-registers` | Create register |

**Frontend pages:**
- `app/(qms)/qms/risk/page.tsx` — risk register list + heat map (5×5 grid coloured by RPN)
- `app/(qms)/qms/risk/[id]/page.tsx` — risk detail with before/after RPN after mitigation

---

### Priority 4 — Supplier & Reagent Quality Module (Module 8)

**New service:** `backend/qms/supplier-service/`

**Database entities:**
```
Supplier: id, tenant_id, supplier_number, name, category, contact_name,
          contact_email, status (approved/conditional/suspended/dequalified),
          qualification_date, requalification_date, created_by
SupplierAudit: id, supplier_id, tenant_id, audit_date, auditor, result (pass/fail/conditional),
               findings, capa_id
```

**API endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/suppliers` | List (filter status) |
| POST | `/api/v1/suppliers` | Create |
| GET | `/api/v1/suppliers/{id}` | Detail |
| PATCH | `/api/v1/suppliers/{id}` | Update |
| POST | `/api/v1/suppliers/{id}/qualify` | Set qualified |
| POST | `/api/v1/suppliers/{id}/suspend` | Suspend with reason |
| POST | `/api/v1/suppliers/{id}/audits` | Record supplier audit |
| GET | `/api/v1/suppliers/{id}/audits` | List audits |

---

### Priority 5 — Environmental Monitoring Module (Module 7)

**New service:** `backend/qms/envmon-service/`

**Database entities:**
```
MonitoringLocation: id, tenant_id, name, location_code, area_type, alert_limits, action_limits
MonitoringRecord: id, location_id, tenant_id, sample_date, parameter (temp/humidity/pressure/particulates),
                  value, unit, within_limits (bool), quality_event_id (nullable)
```

**API endpoints:**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/env-monitoring/locations` | List locations |
| POST | `/api/v1/env-monitoring/locations` | Create |
| GET | `/api/v1/env-monitoring/records` | List records (filter by location, date, parameter) |
| POST | `/api/v1/env-monitoring/records` | Record measurement — auto creates QE if out of limits |
| GET | `/api/v1/env-monitoring/excursions` | List out-of-limit records |

---

### Priority 6 — Management Review Module (Module 12)

**New service:** `backend/qms/management-review-service/`

**Database entities:**
```
ManagementReview: id, tenant_id, review_number, review_date, attendees[],
                  agenda_items[], status (draft/in_progress/approved),
                  summary, action_items[]
ReviewActionItem: id, review_id, description, owner_id, due_date, status
```

**API endpoints:** Standard CRUD + `POST /{id}/approve`

---

### Priority 7 — Proficiency Testing & ILC Module (Module 10)

**New service:** `backend/qms/proficiency-testing-service/`

Lower priority — only needed when lab accreditation is being targeted. Scaffold after modules 4, 11, 9.

---

## 4. Kafka Event Publishing (Missing Cross-Service Triggers)

Currently all cross-service triggers are direct API calls (e.g., approve document → call training API). The master doc defines a Kafka event bus (`rainer_events`). This section documents what needs to be connected.

### 4.1 Events that must be published by QMS services

All QMS services should use the shared `rainer_events` Kafka library (already in platform shared libs).

| Service | Event | Topic | Consumers |
|---------|-------|-------|-----------|
| document-service | `document.approved` | `qms.documents` | training-service (auto-assign) |
| document-service | `document.rejected` | `qms.documents` | notification-service |
| quality-event-service | `quality_event.created` | `qms.events` | notification-service (alert assignee) |
| quality-event-service | `quality_event.closed` | `qms.events` | capa-service (if capa_required) |
| capa-service | `capa.created` | `qms.capas` | notification-service |
| capa-service | `capa.closed` | `qms.capas` | audit-service (log closure) |
| equipment-service | `calibration.failed` | `qms.equipment` | quality-event-service (auto-create QE) |
| training-service | `training.overdue` | `qms.training` | notification-service |

### 4.2 Implementation steps per service

For each QMS service that needs to publish events:

1. Import the shared Kafka publisher:
   ```python
   from rainer_events import EventPublisher
   publisher = EventPublisher(topic="qms.documents")
   ```
2. In the service domain layer (e.g., `document-service/app/domain/services.py`), after a state change, call:
   ```python
   await publisher.publish("document.approved", {
     "document_id": doc.id, "tenant_id": doc.tenant_id,
     "approved_by": user_id, "timestamp": utcnow().isoformat()
   })
   ```
3. In consuming services, add a Kafka consumer that subscribes to the topic and performs the downstream action
4. Remove the direct API call from the frontend once the consumer is working (keep as fallback initially)

---

## 5. Audit Service — Compliance Fix (21 CFR Part 11 / ALCOA+)

**Priority:** High — required for regulatory submission  
**File:** `backend/platform/audit-service/`

### 5.1 Current schema problem

`AuditLogResponse` stores `metadata: dict` as a JSON blob. Auditors need structured `before_value` / `after_value` to verify what specifically changed (immutable field-level audit trail).

### 5.2 Migration steps

1. **Add columns** to `audit_logs` table:
   ```python
   # New Alembic migration
   op.add_column('audit_logs', sa.Column('before_value', JSONB, nullable=True))
   op.add_column('audit_logs', sa.Column('after_value', JSONB, nullable=True))
   ```

2. **Update `AuditLogResponse` Pydantic schema:**
   ```python
   before_value: dict | None = None
   after_value: dict | None = None
   ```

3. **Update `docs/APIs/platform/audit-service.json`** to include these new fields in `AuditLogResponse`.

4. **Update each QMS service** to pass before/after state when writing audit events:
   - In `document-service`: on `approve`, capture `before = {status: "under_review"}`, `after = {status: "effective"}`
   - In `capa-service`: on `close`, capture before/after CAPA status
   - In `equipment-service`: on `calibrate`, capture before/after calibration dates

5. **Update the audit log viewer** (section 2.4) to show a before → after diff panel.

---

## 6. Audit Log Viewer (Frontend) — Build Specification

**API route:** Already proxied via gateway at `/api/v1/audit/logs`  
**Permission required:** `analytics:read` (admin only for full view) or per-resource for inline views

### 6.1 Admin audit log page

**File to create:** `frontend/apps/web/app/(admin)/admin/audit-logs/page.tsx`

```
Layout:
┌─────────────────────────────────────────────────────────────────┐
│ Audit Logs                              [Export CSV]            │
├─────────────────────────────────────────────────────────────────┤
│ Filters: [Resource Type ▾] [Action ▾] [Severity ▾] [From] [To] │
│          [User ID search input]       [Search]                  │
├─────────────────────────────────────────────────────────────────┤
│ Timestamp       │ Action         │ Resource    │ User  │ Sev   │
│ 2026-05-13 10:01│ document.appro │ document/ab │ usr1  │ info  │
│ ...             │                │             │       │       │
├─────────────────────────────────────────────────────────────────┤
│                    Pagination                                   │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation:**
```ts
// lib/api/services/audit.ts
import { platformApiClient } from '../client';

export interface AuditLog {
  id: string; tenant_id: string | null; user_id: string | null;
  action: string; resource_type: string | null; resource_id: string | null;
  ip_address: string | null; user_agent: string | null;
  metadata: Record<string, unknown>; severity: string;
  source_service: string | null; event_id: string | null;
  before_value?: Record<string, unknown> | null;
  after_value?: Record<string, unknown> | null;
  created_at: string;
}

export const auditApi = {
  list: (params?: {
    user_id?: string; action?: string; resource_type?: string;
    resource_id?: string; severity?: string;
    from_date?: string; to_date?: string;
    page?: number; page_size?: number;
  }) =>
    platformApiClient.get<unknown>('/audit/logs', { params })
      .then(r => normalizePaginated<AuditLog>(r.data)),

  get: (id: string) =>
    platformApiClient.get<unknown>(`/audit/logs/${id}`)
      .then(r => unwrapSuccessData<AuditLog>(r.data)),
};
```

### 6.2 Inline audit trail tab on record detail pages

Add an "Audit trail" tab to:
- Document detail page (`documents/[id]/page.tsx`) — already has tabs, add `"audit"` tab type
- CAPA detail page (`capa/[id]/page.tsx`) — add section or tab
- Quality event detail page (`quality-events/[id]/page.tsx`) — add section

Query: `GET /audit/logs?resource_type=document&resource_id={id}&page_size=50`

Show: timestamp, action, user_id, metadata summary (or before/after diff when available).

---

## 7. Dashboard Completion — QMS Widgets

The following dashboard widgets are staged:

| Component | API call | Status |
|-----------|----------|--------|
| `DocumentsDueReviewWidget` | `documentsApi.dueForReview()` | Staged |
| `EquipmentDueCalibrationWidget` | `equipmentApi.dueForCalibration()` | Staged |
| `QualityEventsSummaryWidget` | `qualityEventsApi.summary()` | Staged |
| `TrainingOverdueWidget` | `trainingApi.listOverdueAssignments()` | Staged |

**Check and verify:** Confirm these widgets are imported and rendered in the QMS dashboard page (`app/(qms)/qms/dashboard/page.tsx` or equivalent). If not, import and add them.

**Still missing from dashboard:**
- CAPA overdue count — call `capaApi.list({ overdue_only: true, page_size: 1 })` and display `total`
- Open quality events by severity — use `qualityEventsApi.summary()` `by_status` field

---

## 8. API Endpoint Complete Reference (All 5 Existing QMS Services)

Use this as the definitive checklist when verifying frontend ↔ backend alignment.

### 8.1 Document Service (`/api/v1/documents`)

| Method | Path | FE Function | Permission | Status |
|--------|------|-------------|------------|--------|
| GET | `/documents` | `documentsApi.list()` | `document:read` | ✅ |
| POST | `/documents` | `documentsApi.create()` | `document:write` | ✅ |
| GET | `/documents/{id}` | `documentsApi.get()` | `document:read` | ✅ |
| PATCH | `/documents/{id}` | `documentsApi.update()` | `document:write` | ✅ |
| POST | `/documents/{id}/submit-for-review` | `documentsApi.submitForReview()` | `document:write` | ✅ |
| POST | `/documents/{id}/approve` | `documentsApi.approve()` | `document:approve` | ✅ |
| POST | `/documents/{id}/reject` | `documentsApi.reject()` | `document:approve` | ✅ |
| POST | `/documents/{id}/make-obsolete` | `documentsApi.makeObsolete()` | `document:approve` | ✅ |
| GET | `/documents/{id}/versions` | `documentsApi.getVersions()` | `document:read` | ✅ |
| GET | `/documents/due-for-review` | `documentsApi.dueForReview()` | `document:read` | ✅ |
| GET | `/documents/{id}/distribution` | `documentsApi.listDistribution()` | `document:read` | ✅ |
| POST | `/documents/{id}/distribution` | `documentsApi.addDistributionMember()` | `document:write` | ✅ |

### 8.2 Quality Event Service (`/api/v1/quality-events`)

| Method | Path | FE Function | Permission | Status |
|--------|------|-------------|------------|--------|
| GET | `/quality-events` | `qualityEventsApi.list()` | `quality_event:read` | ✅ |
| POST | `/quality-events` | `qualityEventsApi.create()` | `quality_event:write` | ✅ |
| GET | `/quality-events/{id}` | `qualityEventsApi.get()` | `quality_event:read` | ✅ |
| PATCH | `/quality-events/{id}` | `qualityEventsApi.update()` | `quality_event:write` | ✅ |
| POST | `/quality-events/{id}/close` | `qualityEventsApi.close()` | `quality_event:write` | ✅ |
| DELETE | `/quality-events/{id}` | `qualityEventsApi.delete()` | `quality_event:write` | ✅ |
| GET | `/quality-events/summary` | `qualityEventsApi.summary()` | `quality_event:read` | ✅ |

### 8.3 CAPA Service (`/api/v1/capas`)

| Method | Path | FE Function | Permission | Status |
|--------|------|-------------|------------|--------|
| GET | `/capas` | `capaApi.list()` | `capa:read` | ✅ |
| POST | `/capas` | `capaApi.create()` | `capa:write` | ✅ |
| GET | `/capas/{id}` | `capaApi.get()` | `capa:read` | ✅ |
| PATCH | `/capas/{id}` | `capaApi.update()` | `capa:write` | ✅ |
| POST | `/capas/{id}/close` | `capaApi.close()` | `capa:approve` | ✅ |
| POST | `/capas/{id}/verify-effectiveness` | `capaApi.verifyEffectiveness()` | `capa:approve` | ✅ |
| GET | `/capas/{id}/actions` | `capaApi.listActions()` | `capa:read` | ✅ |
| POST | `/capas/{id}/actions` | `capaApi.addAction()` | `capa:write` | ✅ |
| POST | `/capas/{id}/actions/{action_id}/complete` | `capaApi.completeAction()` | `capa:write` | ✅ |
| PATCH | `/capas/{id}/actions/{action_id}` | — | `capa:write` | ❌ Backend missing |

### 8.4 Training Service (`/api/v1/training`)

| Method | Path | FE Function | Permission | Status |
|--------|------|-------------|------------|--------|
| GET | `/training/courses` | `trainingApi.list()` | `training:read` | ✅ |
| POST | `/training/courses` | `trainingApi.create()` | `training:write` | ✅ |
| GET | `/training/courses/{id}` | `trainingApi.get()` | `training:read` | ✅ |
| POST | `/training/courses/{id}/assign` | `trainingApi.assign()` | `training:assign` | ✅ |
| GET | `/training/assignments` | `trainingApi.listMyAssignments()` | `training:read` | ✅ |
| POST | `/training/assignments/{id}/complete` | `trainingApi.completeAssignment()` | `training:write` | ✅ |
| GET | `/training/assignments/overdue` | `trainingApi.listOverdueAssignments()` | `training:read` | ✅ |

### 8.5 Equipment Service (`/api/v1/equipment`)

| Method | Path | FE Function | Permission | Status |
|--------|------|-------------|------------|--------|
| GET | `/equipment` | `equipmentApi.list()` | `equipment:read` | ✅ |
| POST | `/equipment` | `equipmentApi.create()` | `equipment:write` | ✅ |
| GET | `/equipment/{id}` | `equipmentApi.get()` | `equipment:read` | ✅ |
| PATCH | `/equipment/{id}` | — | `equipment:write` | ❌ FE missing |
| DELETE | `/equipment/{id}` | — | `equipment:write` | ❌ FE missing |
| GET | `/equipment/due-for-calibration` | `equipmentApi.dueForCalibration()` | `equipment:read` | ✅ |
| POST | `/equipment/{id}/calibrate` | `equipmentApi.calibrate()` | `equipment:write` | ✅ |
| POST | `/equipment/{id}/decommission` | `equipmentApi.decommission()` | `equipment:write` | ✅ |
| GET | `/equipment/{id}/calibration-records` | — | `equipment:read` | ❌ Backend missing |

### 8.6 Platform Audit Service (`/api/v1/audit`)

| Method | Path | FE Function | Permission | Status |
|--------|------|-------------|------------|--------|
| GET | `/audit/logs` | — | `analytics:read` | ❌ FE missing |
| GET | `/audit/logs/{id}` | — | `analytics:read` | ❌ FE missing |

---

## 9. New Service Scaffold Template

Use this as a cookie-cutter for Modules 4 and 11 (highest priority).

### 9.1 Backend directory structure

```
backend/qms/{module-name}-service/
├── app/
│   ├── main.py                         # FastAPI app factory, lifespan, middleware
│   ├── api/
│   │   └── v1/
│   │       ├── routes/
│   │       │   └── {module}.py         # APIRouter, Depends(require_permission(...))
│   │       └── __init__.py
│   ├── domain/
│   │   └── services.py                 # Business logic, calls repository
│   ├── infra/
│   │   └── db/
│   │       ├── models.py               # SQLAlchemy 2.0 mapped classes
│   │       └── repositories.py         # Async repository pattern
│   └── schemas/
│       ├── requests.py                 # Pydantic v2 request models
│       └── responses.py                # Pydantic v2 response models (PaginatedResponse, SuccessResponse)
├── migrations/
│   ├── env.py
│   └── versions/
│       └── 001_initial.py
├── tests/
│   └── unit/
├── .env.example
├── alembic.ini
└── requirements.txt
```

### 9.2 `main.py` pattern (copy from capa-service)

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.routes.{module} import router
from app.infra.db.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="Rainer {Module} Service", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router, prefix="/api/v1")
```

### 9.3 Gateway proxy pattern (copy from `capas_proxy.py`)

```python
from fastapi import APIRouter, Request, Response, Depends
from app.core.proxy import proxy_request
from app.core.config import settings

router = APIRouter(prefix="/{module-plural}", tags=["{Module}"])

@router.api_route("/{path:path}", methods=["GET","POST","PATCH","PUT","DELETE","OPTIONS"])
async def proxy_{module}(request: Request, path: str = ""):
    return await proxy_request(
        request, f"{settings.{MODULE}_SERVICE_URL}/api/v1/{module-plural}/{path}"
    )
```

### 9.4 Frontend page pattern

```tsx
// app/(qms)/qms/{module}/page.tsx — list page
"use client";
import { useMyModuleList } from "@/lib/hooks/queries/qms";

// app/(qms)/qms/{module}/[id]/page.tsx — detail page
// - Read permission check at top
// - isLoading / isError early returns
// - Mutation handlers with toast.success / toast.error
// - Permission-gated action buttons (canWrite, canApprove)
```

### 9.5 TanStack Query hook pattern

```ts
// lib/hooks/queries/qms.ts — add alongside existing hooks
export function useMyModuleList(params?: { ... }) {
  return useQuery({
    queryKey: ["my-module", "list", params],
    queryFn: () => myModuleApi.list(params),
  });
}

export function useCreateMyModule() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: ...) => myModuleApi.create(data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["my-module"] }),
  });
}
```

---

## 10. Prioritized Implementation Backlog

Work in this order:

| # | Task | Effort | Blocks |
|---|------|--------|--------|
| B1 | Add `equipmentApi.update()` + edit dialog in equipment detail page | S | Nothing |
| B2 | Add `equipmentApi.delete()` + confirm dialog | S | Nothing |
| B3 | Add calibration history endpoint to equipment-service backend | M | B4 |
| B4 | Add calibration history tab in equipment detail page | S | B3 |
| B5 | Build `auditApi` in `lib/api/services/audit.ts` | S | B6 |
| B6 | Build admin audit log page (`/admin/audit-logs`) | M | B5 |
| B7 | Add inline audit trail tab to document, CAPA, QE detail pages | M | B5 |
| B8 | Add `before_value`/`after_value` to audit-service schema + migration | M | B7 |
| B9 | Update QMS services to pass before/after in audit events | L | B8 |
| C1 | Scaffold QMS Audit Management service (Module 4) | L | — |
| C2 | Build audit management frontend pages | M | C1 |
| C3 | Scaffold Customer Complaints service (Module 11) | L | — |
| C4 | Build complaints frontend pages | M | C3 |
| C5 | Scaffold Risk Management service (Module 9) | L | — |
| C6 | Build risk matrix frontend (heat map) | M | C5 |
| C7 | Add CAPA `PATCH /actions/{id}` to capa-service backend | S | — |
| C8 | Implement Kafka publishing in QMS services | XL | — |
| C9 | Scaffold Supplier service (Module 8) | L | — |
| C10 | Scaffold Environmental Monitoring service (Module 7) | L | — |
| C11 | Scaffold Management Review service (Module 12) | L | — |
| C12 | Scaffold Proficiency Testing service (Module 10) | XL | — |

---

## 11. Testing Requirements Per New Module

For each new module (C1–C12), the test checklist must cover:

**Backend (pytest + httpx):**
- [ ] List endpoint returns empty `{ data: [], pagination: { total: 0 } }` for new tenant
- [ ] Create returns 201 with correct schema
- [ ] Get returns 404 for wrong tenant (tenant isolation)
- [ ] Permission check returns 403 when token lacks the required scope
- [ ] State transition (e.g., approve/close) rejects invalid current status
- [ ] Audit log event is published after each mutation

**Frontend (manual or Playwright):**
- [ ] List page loads with correct columns and empty state message
- [ ] Create form validates required fields before submit
- [ ] Toast shows on success and error
- [ ] Permission-gated buttons are hidden for `tenant_user` role
- [ ] Detail page navigates from list row click
- [ ] Pagination controls work for >20 items

---

## 12. Environment Variables for New Services

For each new service add these to:
1. `backend/qms/{service}/.env.example`
2. Root `.env.example`
3. `ENV_REFERENCE.md`

```bash
# {SERVICE}_SERVICE
{SERVICE}_DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/{service}_db
{SERVICE}_SERVICE_PORT=80{XX}
JWT_SECRET_KEY=change-me-in-production
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
LOG_LEVEL=INFO
```

And add to `backend/platform/gateway-service/.env.example`:
```bash
{SERVICE}_SERVICE_URL=http://localhost:80{XX}
```

And add to `frontend/apps/web/.env.example`:
```bash
NEXT_PUBLIC_QMS_{SERVICE}_API_URL=    # optional direct override
```

---

*End of build roadmap.*
