# QMS permission matrix (code-derived)

This matrix maps **JWT permission strings** (see `backend/shared/rainer_auth_lib/rainer_auth_lib/permissions.py`) to **frontend role sets** in `frontend/apps/web/lib/hooks/usePermission.ts`. Extra JWT `permissions[]` can grant additional rights beyond the role baseline (`has_permission` in auth lib).

## Backend `Permission` enum (QMS subset)

| Permission | Typical use |
|-------------|-------------|
| `document:read` | List/get documents, versions, distribution read, due-for-review. |
| `document:write` | Create/update draft, submit for review, distribution write. |
| `document:approve` | Approve, reject, make obsolete. |
| `document:delete` | Delete draft documents. |
| `quality_event:read` | List/get/summary quality events. |
| `quality_event:write` | Create/update/close/delete quality events. |
| `capa:read` | List/get CAPA, list actions. |
| `capa:write` | Create/update CAPA, add/complete actions (where UI allows). |
| `capa:approve` | Close CAPA, verify effectiveness (quality manager flows). |
| `training:read` | Courses, my assignments, overdue list. |
| `training:write` | Complete assignment (learner completion). |
| `training:assign` | Assign training to users / bulk flows. |
| `equipment:read` | List/get equipment, due-for-calibration. |
| `equipment:write` | Create/update/calibrate/decommission. |
| `analytics:read` | KPIs, dashboards (via gateway). |

## Frontend roles (`ROLE_PERMISSIONS`)

| Role | QMS baseline |
|------|----------------|
| `super_admin` | All permissions (auth lib grants full enum). |
| `tenant_admin` | All QMS read/write/approve/delete + training assign. |
| `tenant_user` | Read-only QMS (`document:read`, `quality_event:read`, `capa:read`, `training:read`, `equipment:read`, `analytics:read`, …). |
| `company_admin` | Same pattern as tenant_admin for QMS in the hook table. |
| `company_user` | Same as tenant_user for QMS reads. |

> **Note:** `company_admin` / `company_user` are not enumerated in `UserRole` in the Python auth lib; those users rely on **`permissions` claims** in the JWT matching the strings above.

## UI gates (Phases 4–8)

- Documents: `document:read` (widgets/lists), `document:write` (distribution add), `document:approve` (reject/approve/obsolete on detail).
- Quality events: `quality_event:read` / `quality_event:write` for destructive or mutating controls.
- CAPA detail: `capa:read` baseline; `capa:write` for actions; `capa:approve` for close / verify effectiveness.
- Equipment: `equipment:read` / `equipment:write` for calibrate & decommission.
- Training: `training:read` for my assignments; `training:write` for completion; `training:assign` for assign flows.

## Backend route guards

QMS FastAPI routes use `dependencies=[Depends(require_permission(Permission.<name>))]`:

- **document-service** `documents.py` — document read/write/approve/delete per route.
- **capa-service** `capas.py` — CAPA read/write/approve on list/get/actions vs close/verify.
- **quality-event-service** `quality_events.py` — quality event read/write.
- **equipment-service** `equipment.py` — equipment read/write on all routes.
- **training-service** `training.py` — training read, write (courses + complete), assign on `POST .../assign`.
