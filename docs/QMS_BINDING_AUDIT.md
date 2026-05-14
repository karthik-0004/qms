# RainerQMS — Full API Binding Audit

> **Date:** 2026-05-13  
> **Purpose:** For every backend service, audit whether each endpoint has a correct frontend client function, correct API path, matching request body fields, and a UI page that actually calls it.  
> **Scope:** All 27 services across Platform, QMS, EM, and CCV groups.

---

## Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Bound correctly — client function exists, path matches, fields match, UI calls it |
| ⚠️ | Partially bound — client exists but UI doesn't call it, or field mismatch |
| ❌ | Not bound — no client function, or client exists but path/fields are wrong |
| 🔇 | Internal only — service-to-service endpoint, no FE binding needed |

---

## Summary of Critical Broken Items

| # | Severity | Issue |
|---|----------|-------|
| 1 | **CRITICAL** | Settings page (`/settings`) is 100% static. No API calls on load or save. `tenantsApi.getSettings()` and `tenantsApi.updateSettings()` exist but are never called. |
| 2 | **CRITICAL** | `auditApi.list()` calls `/audit/entries` but backend exposes `/audit/logs` — always 404. |
| 3 | **CRITICAL** | All EM frontend paths are wrong. FE uses `/plates/plates`, `/images/plates/{id}/images`, `/ai/runs`, `/jobs/jobs`, `/qa-reviews/reviews/{id}/approve` — none of these match actual API JSON paths. |
| 4 | **HIGH** | No profile page exists. Logged-in users cannot view or edit their own profile. |
| 5 | **HIGH** | Users page edit/deactivate: `usersApi.update()` and `usersApi.deactivate()` exist in `platform.ts` but the MoreHorizontal menu in the users list has no wired actions. |
| 6 | **HIGH** | MFA setup/disable flow missing entirely. Backend has 3 MFA endpoints (setup, verify, disable) with zero frontend UI. |
| 7 | **HIGH** | Analytics chart data is hardcoded. KPI cards are live, but "Document Status Distribution" and "CAPA Aging Summary" charts use static mock arrays. |
| 8 | **MEDIUM** | No frontend client for Config Service, File Service, or Reporting Service. |
| 9 | **MEDIUM** | `equipmentApi.update()` and `equipmentApi.delete()` missing from frontend qms.ts (backend has PATCH + DELETE). |
| 10 | **MEDIUM** | QA Review `/approve` and `/reject` FE actions call non-existent paths; correct backend action is `/transition`. |

---

## PLATFORM SERVICES

---

### 1. Auth Service

**File:** `docs/APIs/platform/auth-service.json`  
**FE Client:** None (handled by NextAuth `credentials` provider in `[...nextauth]/route.ts`)

| Endpoint | Method | FE Client | UI | Status | Notes |
|----------|--------|-----------|-----|--------|-------|
| `/auth/login` | POST | NextAuth credentials | `/signin` page | ✅ | Calls `/api/v1/auth/login` |
| `/auth/refresh` | POST | `apiClient` interceptor | Automatic | ✅ | Auto-retry on 401 in `client.ts` |
| `/auth/logout` | POST | NextAuth `signOut()` | Header button | ✅ | |
| `/auth/logout-all` | POST | ❌ None | ❌ None | ❌ | No "logout all devices" button anywhere |
| `/auth/mfa/setup` | POST | ❌ None | ❌ None | ❌ | No MFA setup flow in account settings |
| `/auth/mfa/verify` | POST | ❌ None | ❌ None | ❌ | No second-factor prompt during login |
| `/auth/mfa/disable` | POST | ❌ None | ❌ None | ❌ | No MFA disable option |
| `/auth/access-keys` | POST | ❌ None | ❌ None | ❌ | No API key management page |
| `/auth/access-keys/{id}` | DELETE | ❌ None | ❌ None | ❌ | |

**Request body for `/auth/login`:**
```json
{ "email": "string", "password": "string" }
```
Response fields used by FE: `access_token`, `refresh_token`, `user.id`, `user.email`, `user.role`, `tenant_id`.

---

### 2. User Service

**File:** `docs/APIs/platform/userservice.json`  
**FE Client:** `frontend/apps/web/lib/api/services/platform.ts` → `usersApi`, `companiesApi`

| Endpoint | Method | FE Function | UI Page | Status | Notes |
|----------|--------|-------------|---------|--------|-------|
| `/users` | GET | `usersApi.list()` | `/settings/users` | ✅ | Params: `search`, `role`, `status`, `page`, `page_size` |
| `/users` | POST | `usersApi.create()` | `/settings/users` dialog | ✅ | |
| `/users/{id}` | GET | `usersApi.get(id)` | None | ⚠️ | Function exists; no page navigates to user detail |
| `/users/{id}` | PATCH | `usersApi.update(id, data)` | ❌ No UI | ⚠️ | Function exists; MoreHorizontal menu is empty — no edit dialog |
| `/users/{id}` | DELETE | `usersApi.deactivate(id)` | ❌ No UI | ⚠️ | Function exists; no deactivate confirmation dialog |
| `/users/{id}/permissions` | GET | ❌ None | ❌ None | ❌ | |
| `/roles` | GET | ❌ None | ❌ None | ❌ | |
| `/roles` | POST | ❌ None | ❌ None | ❌ | |
| `/roles/{id}` | GET | ❌ None | ❌ None | ❌ | |
| `/roles/{id}` | PATCH | ❌ None | ❌ None | ❌ | |
| `/roles/{id}` | DELETE | ❌ None | ❌ None | ❌ | |
| `/users/{id}/roles` | POST | ❌ None | ❌ None | ❌ | Only company-scoped role assign in `companiesApi` |
| `/users/{id}/roles/{roleId}` | DELETE | ❌ None | ❌ None | ❌ | |
| SCIM 2.0 routes | — | — | — | 🔇 | IdP integration only |

**Field mismatch in `/users` POST:**  
Backend `CreateUserRequest` expects: `email, first_name, last_name, role, display_name?, phone?, department?, job_title?`  
FE `usersApi.create()` sends all those — ✅ aligned.

**Field mismatch in users list response:**  
Backend returns `{ data: User[], pagination: { total, page, page_size } }`.  
FE correctly unwraps with `r.data.data` / `r.data.pagination` — ✅ aligned.

---

### 3. Tenant Service

**File:** `docs/APIs/platform/tenantservice.json`  
**FE Client:** `frontend/apps/web/lib/api/services/platform.ts` → `tenantsApi`

| Endpoint | Method | FE Function | UI Page | Status | Notes |
|----------|--------|-------------|---------|--------|-------|
| `/tenants` | GET | `tenantsApi.list()` | Super-admin tenant list | ✅ | |
| `/tenants` | POST | `tenantsApi.create()` | Create tenant wizard | ✅ | |
| `/tenants/{id}` | GET | `tenantsApi.get(id)` | Tenant detail | ✅ | |
| `/tenants/{id}` | PATCH | `tenantsApi.update(id, data)` | Tenant edit dialog | ✅ | |
| `/tenants/{id}` | DELETE | `tenantsApi.delete(id)` | Tenant detail | ✅ | |
| `/tenants/{id}/suspend` | POST | `tenantsApi.suspend(id)` | Tenant detail | ✅ | |
| `/tenants/{id}/activate` | POST | `tenantsApi.activate(id)` | Tenant detail | ✅ | |
| `/tenants/{id}/settings` | GET | `tenantsApi.getSettings(id)` | ❌ NOT called | ⚠️ | **Settings page is static — never calls this** |
| `/tenants/{id}/settings` | PATCH | `tenantsApi.updateSettings(id, data)` | ❌ NOT called | ⚠️ | **Save button does nothing — never calls this** |
| `/tenants/by-slug/{slug}` | GET | `tenantsApi.getBySlug(slug)` | Auth flow | ✅ | |
| `/tenants/resend-welcome-email` | POST | `tenantsApi.resendWelcomeEmail(id)` | Tenant detail | ✅ | |

**CRITICAL — Settings Page Bug (`frontend/apps/web/app/(platform)/settings/page.tsx`):**

```tsx
// ALL STATE IS HARDCODED — nothing loaded from API:
const [orgName, setOrgName] = useState("Rainer Technologies");  // hardcoded
const [timezone, setTimezone] = useState("America/New_York");    // hardcoded
const [emailNotifications, setEmailNotifications] = useState(true); // hardcoded
const [mfaEnforced, setMfaEnforced] = useState(false);           // hardcoded

// Save button calls NOTHING:
<Button>Save Settings</Button>  // no onClick handler with API call
```

**Fix required:**
1. On mount: `tenantsApi.getSettings(session.tenant_id)` → populate `orgName` from `tenant.tenant_name`, `timezone` from `settings.timezone`, `features.enforce_mfa` → `mfaEnforced`
2. On save: `tenantsApi.updateSettings(tenantId, { timezone, features })` + optionally `tenantsApi.update(tenantId, { tenant_name: orgName })`

---

### 4. Analytics Service

**File:** `docs/APIs/platform/analytics-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/analytics.ts` → `analyticsApi`

| Endpoint | Method | FE Function | UI Page | Status | Notes |
|----------|--------|-------------|---------|--------|-------|
| `/analytics/dashboards` | GET | `analyticsApi.listDashboards()` | QMS analytics | ✅ | |
| `/analytics/dashboards/{id}` | GET | `analyticsApi.getDashboard(id)` | QMS analytics | ⚠️ | Function called but chart data NOT used — charts are hardcoded |
| `/analytics/kpis` | GET | `analyticsApi.getKPIs()` | QMS analytics | ✅ | KPI cards are live |
| `/analytics/time-series` | GET | `analyticsApi.getTimeSeries()` | None | ⚠️ | Function exists; no UI uses it |

**Hardcoded chart data in `/qms/analytics/page.tsx`:**
```tsx
// These should come from analyticsApi.getDashboard("qms_overview"):
const documentStatusData = [
  { name: "Approved", value: 45 },    // HARDCODED
  { name: "Draft", value: 23 },        // HARDCODED
  ...
];
const capaAgingData = [
  { name: "0-30 days", count: 8 },     // HARDCODED
  ...
];
```

---

### 5. Config Service

**File:** `docs/APIs/platform/config-service.json`  
**FE Client:** ❌ None

| Endpoint | Method | FE Function | UI | Status |
|----------|--------|-------------|-----|--------|
| `/config/features` | GET | ❌ None | ❌ None | ❌ |
| `/config/features/{flag_key}` | GET | ❌ None | ❌ None | ❌ |
| `/config/enums` | GET | ❌ None | ❌ None | ❌ |

**Impact:** Enum values for dropdowns (document types, CAPA severity levels, etc.) are hardcoded strings in FE components. If they need to match backend validation, they must come from `/config/enums`.

---

### 6. File Service

**File:** `docs/APIs/platform/file-service.json`  
**FE Client:** ❌ None

| Endpoint | Method | FE Function | UI | Status |
|----------|--------|-------------|-----|--------|
| `/files/upload` | POST (multipart) | ❌ None | ❌ None | ❌ |
| `/files` | GET | ❌ None | ❌ None | ❌ |

**Impact:** No document file attachment UI. Document service stores content but there's no way to upload/view actual files through the gateway file service.

---

### 7. Reporting Service

**File:** `docs/APIs/platform/reporting-service.json`  
**FE Client:** ❌ None

| Endpoint | Method | FE Function | UI | Status |
|----------|--------|-------------|-----|--------|
| `/reports/generate` | POST (async, returns 202) | ❌ None | ❌ None | ❌ |
| `/reports/jobs/{id}` | GET (poll for result) | ❌ None | ❌ None | ❌ |

---

### 8. Notification Service

**File:** `docs/APIs/platform/notification-service.json`  
**FE Client:** N/A

| Endpoint | Notes |
|----------|-------|
| `/notifications/send-email` | 🔇 Internal service-to-service |
| `/notifications/send-from-template` | 🔇 Internal service-to-service |

No FE binding needed — these are called by other backend services only.

---

### 9. Audit Service

**File:** `docs/APIs/platform/audit-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/platform.ts` → `auditApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/audit/logs` | GET | `auditApi.list()` calls `/audit/entries` | None | ❌ | **PATH MISMATCH — always 404** |
| `/audit/logs/{id}` | GET | ❌ None | ❌ None | ❌ | |
| `/audit/logs` | POST (internal) | N/A | N/A | 🔇 | Append-only, called by other services |

**The Bug:**
```ts
// platform.ts line 291 — WRONG PATH:
export const auditApi = {
  list: (params?) =>
    apiClient.get<PaginatedResponse<AuditEntry>>("/audit/entries", { params })
    // Should be: "/audit/logs"
```

**Fix:** Change `/audit/entries` → `/audit/logs`.

**Response shape mismatch:** Backend `AuditLogResponse` schema has fields: `id`, `tenant_id`, `user_id`, `action`, `entity_type`, `entity_id`, `metadata` (JSON object), `created_at`.  
FE `AuditEntry` interface has `details` (not `metadata`) → **field rename needed**: `details` → `metadata`.

**Missing audit viewer page:** No page exists at any route to display audit logs. The `auditApi` is defined but never imported in any page.

---

### 10. Schedule Service

**File:** `docs/APIs/platform/schedule-service.json`

Service exists but has **empty `paths` object** — no endpoints defined yet. No FE binding needed.

---

### 11. Workflow Engine

Service file is empty — shell only. No FE binding needed.

---

### 12. Profile Page (Missing)

There is **no profile page** anywhere in the frontend. After login, users cannot:
- View their own profile (`first_name`, `last_name`, `email`, `job_title`, `department`, `avatar_url`)
- Edit their profile fields
- Change their password
- View their login history

The backend exposes `PATCH /api/v1/users/{id}` for updating a user. The `usersApi.get(id)` and `usersApi.update(id, data)` functions exist in `platform.ts` but no profile route uses them.

**Missing pages:**
- `/profile` — "My Account" page for the logged-in user
- No password change endpoint in user-service (would need auth-service change-password endpoint)

---

## QMS SERVICES

---

### 13. Document Service

**File:** `docs/APIs/qms/document-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/qms.ts` → `documentsApi`

| Endpoint | Method | FE Function | UI | Status |
|----------|--------|-------------|-----|--------|
| `/documents` | GET | `documentsApi.list()` | `/qms/documents` | ✅ |
| `/documents` | POST | `documentsApi.create()` | Create dialog | ✅ |
| `/documents/{id}` | GET | `documentsApi.get(id)` | `/qms/documents/[id]` | ✅ |
| `/documents/{id}` | PATCH | `documentsApi.update(id, data)` | Edit dialog | ✅ |
| `/documents/{id}/submit` | POST | `documentsApi.submit(id)` | Detail page | ✅ |
| `/documents/{id}/approve` | POST | `documentsApi.approve(id, data)` | Detail page | ✅ |
| `/documents/{id}/reject` | POST | `documentsApi.reject(id, data)` | Detail page | ✅ |
| `/documents/{id}/publish` | POST | `documentsApi.publish(id)` | Detail page | ✅ |

**All bindings correct.** Response envelope unwrapped correctly. Signature validation uses `approved_by` + `signature` fields — ✅ aligned.

---

### 14. Quality Event Service

**File:** `docs/APIs/qms/quality-event-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/qms.ts` → `qualityEventsApi`

| Endpoint | Method | FE Function | UI | Status |
|----------|--------|-------------|-----|--------|
| `/quality-events` | GET | `qualityEventsApi.list()` | `/qms/quality-events` | ✅ |
| `/quality-events` | POST | `qualityEventsApi.create()` | Create dialog | ✅ |
| `/quality-events/{id}` | GET | `qualityEventsApi.get(id)` | `/qms/quality-events/[id]` | ✅ |
| `/quality-events/{id}` | PATCH | `qualityEventsApi.update(id, data)` | Edit | ✅ |
| `/quality-events/{id}/close` | POST | `qualityEventsApi.close(id, data)` | Detail page | ✅ |
| `/quality-events/{id}/escalate` | POST | `qualityEventsApi.escalateToCapa(id, data)` | Detail page | ✅ |

**All bindings correct.**

---

### 15. CAPA Service

**File:** `docs/APIs/qms/capa-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/qms.ts` → `capasApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/capas` | GET | `capasApi.list()` | `/qms/capa` | ✅ | |
| `/capas` | POST | `capasApi.create()` | Create dialog | ✅ | |
| `/capas/{id}` | GET | `capasApi.get(id)` | `/qms/capa/[id]` | ✅ | |
| `/capas/{id}` | PATCH | `capasApi.update(id, data)` | Edit | ✅ | |
| `/capas/{id}` | DELETE | ❌ None | ❌ None | ❌ | Backend has DELETE; FE missing |
| `/capas/{id}/start-investigation` | POST | `capasApi.startInvestigation(id)` | Detail | ✅ | |
| `/capas/{id}/root-cause` | POST | `capasApi.submitRootCause(id, data)` | Detail | ✅ | |
| `/capas/{id}/actions` | POST | `capasApi.addAction(id, data)` | Detail | ✅ | |
| `/capas/{id}/actions/{actionId}/complete` | POST | `capasApi.completeAction(id, actionId, data)` | Detail | ✅ | |
| `/capas/{id}/verify-effectiveness` | POST | `capasApi.verifyEffectiveness(id, data)` | Detail | ✅ | |
| `/capas/{id}/close` | POST | `capasApi.close(id, data)` | Detail | ✅ | |

**Field note:** Backend `CAPAResponse` uses `severity` (not `priority`). FE uses `mapCapaDto` which reads `c.severity ?? c.priority` for backward compatibility — ✅ correct.

---

### 16. Equipment Service

**File:** `docs/APIs/qms/equipment-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/qms.ts` → `equipmentApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/equipment` | GET | `equipmentApi.list()` | `/qms/equipment` | ✅ | |
| `/equipment` | POST | `equipmentApi.create()` | Create dialog | ✅ | |
| `/equipment/{id}` | GET | `equipmentApi.get(id)` | `/qms/equipment/[id]` | ✅ | |
| `/equipment/{id}` | PATCH | ❌ None | ❌ None | ❌ | Backend has PATCH; FE missing `equipmentApi.update()` |
| `/equipment/{id}` | DELETE | ❌ None | ❌ None | ❌ | Backend has DELETE; FE missing `equipmentApi.delete()` |
| `/equipment/{id}/calibrations` | POST | `equipmentApi.recordCalibration(id, data)` | Detail | ✅ | |
| `/equipment/{id}/calibrations` | GET | ❌ None | ❌ None | ❌ | No calibration history list in FE |
| `/equipment/{id}/decommission` | PATCH | `equipmentApi.decommission(id, data)` | Detail | ✅ | |

---

### 17. Training Service

**File:** `docs/APIs/qms/training-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/qms.ts` → `trainingApi`

| Endpoint | Method | FE Function | UI | Status |
|----------|--------|-------------|-----|--------|
| `/training/courses` | GET | `trainingApi.listCourses()` | `/qms/training` | ✅ |
| `/training/courses` | POST | `trainingApi.createCourse()` | Create dialog | ✅ |
| `/training/courses/{id}` | GET | `trainingApi.getCourse(id)` | Course detail | ✅ |
| `/training/assignments` | GET | `trainingApi.listAssignments()` | My training | ✅ |
| `/training/assignments` | POST | `trainingApi.createAssignment()` | Assign dialog | ✅ |
| `/training/assignments/{id}` | GET | `trainingApi.getAssignment(id)` | Assignment detail | ✅ |
| `/training/assignments/{id}/complete` | POST | `trainingApi.completeAssignment(id, data)` | My training | ✅ |

**All bindings correct.** E-signature flow for certified courses sends `signature` field — aligned with backend.

---

## EM (Environmental Monitoring) SERVICES

**Important note:** The EM frontend client (`em.ts`) was written with wrong API path assumptions throughout. The gateway proxies EM service requests, but the actual service endpoints use `/api/v1/plates`, `/api/v1/images`, etc. — not nested paths like `/plates/plates` or `/images/plates/{id}/images`.

---

### 18. Plate Service

**File:** `docs/APIs/em/plate-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/em.ts` → `platesApi`

| Endpoint | Method | FE Function | Expected FE Path | Actual FE Path | Status |
|----------|--------|-------------|-----------------|----------------|--------|
| `/plates` | GET | `platesApi.list()` | `/plates` | `/plates/plates` ❌ | ❌ |
| `/plates` | POST | `platesApi.register()` | `/plates` | `/plates/plates` ❌ | ❌ |
| `/plates/{id}` | GET | `platesApi.get(id)` | `/plates/{id}` | `/plates/plates/{id}` ❌ | ❌ |
| `/plates/{id}/status` | POST | `platesApi.transition(id, data)` | `/plates/{id}/status` | `/plates/plates/{id}/transition` ❌ | ❌ |
| `/plates/{id}/history` | GET | ❌ None | `/plates/{id}/history` | — | ❌ |

**Request body mismatch for `register()`:**  
FE sends: `{ barcode, plate_type, media_type }` — backend `RegisterPlateRequest` expects: `{ barcode, sample_type, media_type, location_code?, lot_number?, notes?, incubation_temp_celsius?, incubation_hours?, metadata? }`.  
Field `plate_type` → backend calls it `sample_type` — **field name mismatch**.

**Response field mismatch — `Plate` interface in em.ts vs `PlateResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `plate_type` | `sample_type` | ❌ Wrong name |
| `location` | `location_code` | ❌ Wrong name |
| — | `operator_id` | ❌ Missing in FE type |
| — | `lot_number` | ❌ Missing in FE type |
| — | `incubation_temp_celsius` | ❌ Missing in FE type |

---

### 19. Image Service

**File:** `docs/APIs/em/image-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/em.ts` → `imagesApi`

| Endpoint | Method | FE Function | Expected FE Path | Actual FE Path | Status |
|----------|--------|-------------|-----------------|----------------|--------|
| `/images` | GET | ❌ None | `/images` | — | ❌ |
| `/images` | POST | `imagesApi.upload()` | `/images` (JSON body) | `/images/plates/{id}/images` (wrong path, multipart) | ❌ |
| `/images/{id}` | GET | ❌ None | `/images/{id}` | — | ❌ |
| `/images/{id}` | DELETE | ❌ None | `/images/{id}` | — | ❌ |
| `/images/{id}/set-primary` | POST | ❌ None | `/images/{id}/set-primary` | — | ❌ |

**Request body mismatch for `upload()`:**  
FE sends multipart FormData — backend `RegisterImageRequest` uses JSON body with fields: `{ plate_id, image_key, image_type, captured_at, file_size_bytes?, width_px?, height_px?, resolution_dpi?, magnification?, camera_settings?, is_primary? }`.

**Response field mismatch — `EMImage` interface vs `ImageResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `s3_key` | `image_key` | ❌ Wrong name |
| — | `uploaded_by` | ❌ Missing in FE type |
| — | `file_size_bytes` | ❌ Missing in FE type |
| — | `width_px`, `height_px`, `resolution_dpi`, `magnification` | ❌ Missing in FE type |
| — | `camera_settings` | ❌ Missing in FE type |

---

### 20. AI Service

**File:** `docs/APIs/em/ai-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/em.ts` → `aiRunsApi`

| Endpoint | Method | FE Function | Expected FE Path | Actual FE Path | Status |
|----------|--------|-------------|-----------------|----------------|--------|
| `/analysis/runs` | GET | ❌ None | `/analysis/runs` | — | ❌ |
| `/analysis/runs` | POST | `aiRunsApi.start()` | `/analysis/runs` | `/ai/runs` ❌ | ❌ |
| `/analysis/runs/{id}` | GET | ❌ None | `/analysis/runs/{id}` | — | ❌ |
| `/analysis/runs/{id}/start` | POST | ❌ None | `/analysis/runs/{id}/start` | — | ❌ |
| `/analysis/runs/{id}/complete` | POST | ❌ None | `/analysis/runs/{id}/complete` | — | ❌ |
| `/analysis/runs/{id}/fail` | POST | ❌ None | `/analysis/runs/{id}/fail` | — | ❌ |
| `/analysis/runs/{id}/result` | GET | ❌ None | `/analysis/runs/{id}/result` | — | ❌ |

**Request body mismatch for `start()`:**  
FE sends: `{ plate_id, image_id }` — backend `CreateAnalysisRunRequest` expects: `{ plate_id, image_id, job_id?, model_name?, model_version? }` — minimal fields match ✅ but path is wrong.

**Response field mismatch — `AIRun` interface vs `AnalysisRunResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `colony_count` | not in run response | ❌ — Colony count is in `AnalysisResultResponse`, not the run |
| `confidence` | not in run response | ❌ — `confidence_score` is in result, not run |
| `has_contamination` | not in run response | ❌ — in result only |
| `model_name` | `model_name` | ✅ |
| — | `model_version` | ❌ Missing in FE type |
| — | `triggered_by` | ❌ Missing in FE type |

---

### 21. Job Service

**File:** `docs/APIs/em/job-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/em.ts` → `jobsApi`

| Endpoint | Method | FE Function | Expected FE Path | Actual FE Path | Status |
|----------|--------|-------------|-----------------|----------------|--------|
| `/jobs` | GET | `jobsApi.list()` | `/jobs` | `/jobs/jobs` ❌ | ❌ |
| `/jobs` | POST | `jobsApi.enqueue()` | `/jobs` | `/jobs/jobs` ❌ | ❌ |
| `/jobs/{id}` | GET | `jobsApi.get(id)` | `/jobs/{id}` | `/jobs/jobs/{id}` ❌ | ❌ |
| `/jobs/claim` | POST | ❌ None | `/jobs/claim` | — | ❌ |
| `/jobs/{id}/complete` | POST | ❌ None | `/jobs/{id}/complete` | — | ❌ |
| `/jobs/{id}/fail` | POST | ❌ None | `/jobs/{id}/fail` | — | ❌ |
| `/jobs/{id}/cancel` | POST | ❌ None | `/jobs/{id}/cancel` | — | ❌ |

**Request body mismatch for `enqueue()`:**  
FE sends: `{ job_type, plate_barcode, priority }` — backend `EnqueueJobRequest` expects: `{ job_type, payload, priority, max_retries? }`.  
`plate_barcode` → should be inside `payload: { plate_barcode: "..." }`. Field is wrong.

**Response field mismatch — `Job` interface vs `JobResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `plate_barcode` | not a top-level field | ❌ — this is a payload field |
| `attempts` | `retry_count` | ❌ Wrong name |
| `max_attempts` | `max_retries` | ❌ Wrong name |
| — | `payload` | ❌ Missing in FE type |
| — | `created_by` | ❌ Missing in FE type |
| — | `next_retry_at` | ❌ Missing in FE type |

---

### 22. QA Review Service

**File:** `docs/APIs/em/qa-review-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/em.ts` → `qaReviewsApi`

| Endpoint | Method | FE Function | Expected FE Path | Actual FE Path | Status |
|----------|--------|-------------|-----------------|----------------|--------|
| `/reviews` | GET | ❌ None (only by-plate) | `/reviews` | — | ❌ |
| `/reviews` | POST | `qaReviewsApi.create()` | `/reviews` | `/qa-reviews/reviews` ❌ | ❌ |
| `/reviews/{id}` | GET | ❌ None | `/reviews/{id}` | — | ❌ |
| `/reviews/{id}/assign` | POST | ❌ None | `/reviews/{id}/assign` | — | ❌ |
| `/reviews/{id}/transition` | POST | `qaReviewsApi.approve()` / `reject()` | `/reviews/{id}/transition` | `/qa-reviews/reviews/{id}/approve` ❌ | ❌ |
| `/reviews/{id}/comments` | GET | ❌ None | `/reviews/{id}/comments` | — | ❌ |
| `/reviews/{id}/comments` | POST | ❌ None | `/reviews/{id}/comments` | — | ❌ |

**Wrong action pattern:** FE uses `/approve` and `/reject` as separate endpoints. Backend uses a single `/transition` endpoint with `{ new_status: "approved" | "rejected", decision, review_notes, override_colony_count, override_reason, ai_result_accepted }`.

**Response field mismatch — `QAReview` interface vs `ReviewResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `ai_run_id` | `analysis_run_id` | ❌ Wrong name |
| `comments` | `review_notes` | ❌ Wrong name |
| `reviewed_at` | `review_completed_at` | ❌ Wrong name |
| — | `review_started_at` | ❌ Missing |
| — | `assigned_at` | ❌ Missing |
| — | `override_reason` | ❌ Missing |
| — | `ai_result_accepted` | ❌ Missing |
| — | `due_at` | ❌ Missing |

---

## CCV SERVICES

---

### 23. CRM Service

**File:** `docs/APIs/ccv/crm-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/ccv.ts` → `customersApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/crm/customers` | GET | `customersApi.list()` | `/ccv/customers` | ✅ | Path via gateway `/crm/customers` ✅ |
| `/crm/customers` | POST | `customersApi.create()` | Create dialog | ✅ | |
| `/crm/customers/{id}` | GET | `customersApi.get(id)` | Customer detail | ✅ | |
| `/crm/customers/{id}` | PATCH | `customersApi.update(id, data)` | Edit dialog | ✅ | |
| `/crm/customers/{id}/status` | POST | ❌ None | ❌ None | ❌ | No status transition in UI |
| `/crm/customers/{id}/contacts` | GET | ❌ None | ❌ None | ❌ | Contacts list not in FE |
| `/crm/customers/{id}/contacts` | POST | ❌ None | ❌ None | ❌ | Add contact not in FE |
| `/crm/customers/{id}/interactions` | GET | ❌ None | ❌ None | ❌ | Interaction log not in FE |
| `/crm/customers/{id}/interactions` | POST | ❌ None | ❌ None | ❌ | Log interaction not in FE |

**Response field mismatch — `Customer` interface vs `CustomerResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `company_name` | `company_name` | ✅ |
| `contact_count` | `contact_count` | ✅ |
| — | `website` | ❌ Missing in FE type |
| — | `address`, `postal_code` | ❌ Missing in FE type |
| — | `tags` | ❌ Missing in FE type |
| — | `notes` | ❌ Missing in FE type |

---

### 24. Contract Service

**File:** `docs/APIs/ccv/contract-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/ccv.ts` → `contractsApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/contracts` | GET | `contractsApi.list()` | `/ccv/contracts` | ✅ | Uses `skip`/`limit` params — backend expects these ✅ |
| `/contracts` | POST | `contractsApi.create()` | Create dialog | ✅ | Auto-generates `contract_number` if not provided |
| `/contracts/{id}` | GET | `contractsApi.get(id)` | Contract detail | ✅ | |
| `/contracts/{id}/status` | POST | `contractsApi.transition(id, data)` | Detail | ✅ | Maps `action` → `new_status` ✅ |
| `/contracts/{id}/history` | GET | ❌ None | ❌ None | ❌ | No history timeline in FE |
| `/contracts/{id}/line-items` | GET | ❌ None | ❌ None | ❌ | No line items in FE |
| `/contracts/{id}/line-items` | POST | ❌ None | ❌ None | ❌ | |

**Note:** Backend returns raw array (not paginated envelope) for `GET /contracts`. FE handles this via `coerceListPage()` — ✅ correct.

**Response field mismatch — `Contract` interface vs `ContractResponse`:**
| FE field | Backend field | Match? |
|----------|--------------|--------|
| `customer_name` | not in backend response | ❌ — backend only has `customer_id` |
| — | `payment_terms` | ❌ Missing in FE type |
| — | `approved_at/by`, `signed_at/by` | ❌ Missing in FE type |
| — | `terminated_at`, `termination_reason` | ❌ Missing in FE type |

---

### 25. Work Order Service

**File:** `docs/APIs/ccv/workorder-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/ccv.ts` → `workOrdersApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/workorders` | GET | `workOrdersApi.list()` | `/ccv/work-orders` | ✅ | |
| `/workorders` | POST | `workOrdersApi.create()` | Create dialog | ⚠️ | Sends `scheduled_start` — needs to verify backend field name |
| `/workorders/{id}` | GET | `workOrdersApi.get(id)` | WO detail | ✅ | |
| `/workorders/{id}/assign` | POST | `workOrdersApi.assign(id, data)` | Detail | ✅ | |
| `/workorders/{id}/status` | POST | `workOrdersApi.transition(id, data)` | Detail | ✅ | |

**Response field mismatch — `WorkOrder` interface vs backend:**
| FE field | Notes |
|----------|-------|
| `customer_name` | Backend likely only returns `customer_id` — FE assumes name is present |

---

### 26. Technician Service

**File:** `docs/APIs/ccv/technician-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/ccv.ts` → `techniciansApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/technicians` | GET | `techniciansApi.list()` | `/ccv/technicians` | ✅ | |
| `/technicians` | POST | `techniciansApi.create()` | Create dialog | ⚠️ | Sends fake `user_id` (random UUID) — will not link to real platform user |
| `/technicians/{id}` | GET | `techniciansApi.get(id)` | Technician detail | ✅ | |
| `/technicians/{id}/availability` | POST | `techniciansApi.updateAvailability(id, data)` | Detail | ✅ | |

**Critical issue with `create()`:**
```ts
// em.ts — fake user_id:
user_id: typeof crypto !== "undefined" ? crypto.randomUUID() : "00000000-0000-4000-8000-000000000001"
```
This creates technicians with a random UUID as the platform user link, meaning no real user account is associated. Technicians cannot log in or have proper RBAC.

---

### 27. Billing Service

**File:** `docs/APIs/ccv/billing-service.json`  
**FE Client:** `frontend/apps/web/lib/api/services/ccv.ts` → `invoicesApi`

| Endpoint | Method | FE Function | UI | Status | Notes |
|----------|--------|-------------|-----|--------|-------|
| `/invoices` | GET | `invoicesApi.list()` | `/ccv/billing` | ✅ | |
| `/invoices` | POST | `invoicesApi.create()` | Create dialog | ✅ | |
| `/invoices/{id}` | GET | `invoicesApi.get(id)` | Invoice detail | ✅ | |
| `/invoices/{id}/payments` | POST | `invoicesApi.recordPayment(id, data)` | Detail | ✅ | Sends `reference_number` ✅ |
| `/invoices/{id}/status` | POST | `invoicesApi.transition(id, data)` | Detail | ✅ | |

**Response field mismatch — `Invoice` interface vs backend:**
| FE field | Notes |
|----------|-------|
| `customer_name` | Backend likely only returns `customer_id` |
| `amount_paid` | Needs verification against billing-service schema |
| `amount_due` | Needs verification |

---

## Fix Priority Queue

### Priority 1 — Fixes that make existing features work

| # | File | Fix |
|---|------|-----|
| P1-A | `platform.ts:292` | Change `"/audit/entries"` → `"/audit/logs"` and rename `details` → `metadata` in `AuditEntry` interface |
| P1-B | `settings/page.tsx` | Add `useEffect` to load `tenantsApi.getSettings()` on mount; wire Save button to `tenantsApi.updateSettings()` |
| P1-C | `settings/users/page.tsx` | Wire MoreHorizontal menu to edit dialog (uses `usersApi.update()`) and deactivate confirmation (uses `usersApi.deactivate()`) |

### Priority 2 — Core missing pages

| # | Page to Create | APIs to Call |
|---|----------------|-------------|
| P2-A | `/profile` — My Account | `usersApi.get(session.user.id)` + `usersApi.update()` |
| P2-B | `/settings/audit-logs` — Audit Log Viewer | `auditApi.list()` after P1-A fix |
| P2-C | MFA settings section in `/profile` | `POST /auth/mfa/setup`, `POST /auth/mfa/verify`, `POST /auth/mfa/disable` |

### Priority 3 — EM service path corrections

All 5 EM service clients in `em.ts` need path and field corrections:

| Client | Old Path Pattern | Correct Path Pattern |
|--------|-----------------|---------------------|
| `platesApi` | `/plates/plates/*` | `/plates/*` |
| `imagesApi` | `/images/plates/{id}/images` | `/images` (with body fields) |
| `aiRunsApi` | `/ai/runs` | `/analysis/runs` |
| `jobsApi` | `/jobs/jobs/*` | `/jobs/*` |
| `qaReviewsApi` | `/qa-reviews/reviews/{id}/approve|reject` | `/reviews/{id}/transition` |

Also fix `RegisterPlateRequest` field: `plate_type` → `sample_type`.  
Also fix `QAReview` interface field names: `ai_run_id` → `analysis_run_id`, `comments` → `review_notes`, `reviewed_at` → `review_completed_at`.

### Priority 4 — Missing client functions

| Service | Missing FE Functions |
|---------|---------------------|
| CAPA | `capasApi.delete(id)` |
| Equipment | `equipmentApi.update(id, data)`, `equipmentApi.delete(id)`, `equipmentApi.getCalibrationHistory(id)` |
| CRM | `customersApi.transitionStatus(id, data)`, `customersApi.listContacts(id)`, `customersApi.addContact(id, data)`, `customersApi.listInteractions(id)`, `customersApi.logInteraction(id, data)` |
| Contract | `contractsApi.getHistory(id)`, `contractsApi.listLineItems(id)`, `contractsApi.addLineItem(id, data)` |
| Auth | `authApi.logoutAll()`, `authApi.setupMFA()`, `authApi.verifyMFA()`, `authApi.disableMFA()` |
| Config | `configApi.getFeatures()`, `configApi.getFeatureFlag(key)`, `configApi.getEnums()` |
| File | `fileApi.upload(formData)`, `fileApi.list()` |
| Reporting | `reportingApi.generate(params)`, `reportingApi.getJobStatus(id)` |

### Priority 5 — Analytics charts deharcode

| File | Section | Fix |
|------|---------|-----|
| `app/(qms)/qms/analytics/page.tsx` | Document Status Distribution chart | Replace hardcoded array with data from `analyticsApi.getDashboard("qms_overview")` |
| `app/(qms)/qms/analytics/page.tsx` | CAPA Aging Summary chart | Same — use real API data |

---

## Services with Zero Frontend Binding (all endpoints missing)

These backend services have a frontend client file but NO UI pages that use them, or have no FE client at all:

| Service | Status | Impact |
|---------|--------|--------|
| Config Service | No FE client | Enum dropdowns are hardcoded |
| File Service | No FE client | No file upload/attachment UI |
| Reporting Service | No FE client | No export/report generation UI |
| Audit Service | Client exists, wrong path | Audit log viewer page missing |
| Schedule Service | Service has no endpoints yet | — |
| Workflow Engine | Service is empty | — |
