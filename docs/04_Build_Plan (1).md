# RainerQMS — Phased Build Plan with UI Specifications

> **Document Purpose:** A single, actionable build plan that takes the current RainerQMS codebase (5 modules built, 9 missing, frontend basic) to a polished, MasterControl-quality product. Each phase contains: scope, backend tasks, frontend tasks with detailed UI specs, field bindings, acceptance criteria, and dependencies.
>
> **How to use this document:**
> 1. Work through phases in order — each phase unlocks the next
> 2. Each module section is self-contained: backend → frontend → fields → UI layout → acceptance
> 3. UI specs target MasterControl visual quality (Documents Explorer, InfoCard view, Job Code Matrix, FBS tabs, etc.)
> 4. All API field bindings explicitly listed — no hidden data
>
> **Special note on Supplier Quality (M8):** Deprioritized to final phase pending clarification with manager on scope and timeline. Marked throughout as **[DEFERRED]**.
>
> **Built on:** `RainerQMS_Complete_Reference.md` (May 2026 codebase state)

---

## Table of Contents

1. [Build Phase Roadmap](#1-build-phase-roadmap)
2. [Design System & UI Foundation](#2-design-system--ui-foundation)
3. [UI Reference Image Mapping](#3-ui-reference-image-mapping)
4. [Document Editor Integration (editor.manne.work)](#4-document-editor-integration-editormannework)
5. [Phase 0 — Fix & Stabilize Existing Modules](#5-phase-0--fix--stabilize-existing-modules)
6. [Phase 1 — Platform Foundations](#6-phase-1--platform-foundations)
7. [Phase 2 — Document Control Completion](#7-phase-2--document-control-completion)
8. [Phase 3 — Quality Event & CAPA Polish](#8-phase-3--quality-event--capa-polish)
9. [Phase 4 — Training Excellence (Job Codes + Matrix)](#9-phase-4--training-excellence)
10. [Phase 5 — Equipment Completion](#10-phase-5--equipment-completion)
11. [Phase 6 — Audit Management (New Module)](#11-phase-6--audit-management)
12. [Phase 7 — Environmental Monitoring (New Module)](#12-phase-7--environmental-monitoring)
13. [Phase 8 — Risk Management (New Module)](#13-phase-8--risk-management)
14. [Phase 9 — Proficiency Testing (New Module)](#14-phase-9--proficiency-testing)
15. [Phase 10 — Customer Complaints (New Module)](#15-phase-10--customer-complaints)
16. [Phase 11 — Management Review (New Module)](#16-phase-11--management-review)
17. [Phase 12 — Reporting & Analytics Completion](#17-phase-12--reporting--analytics-completion)
18. [Phase 13 — Lab-Specific Features](#18-phase-13--lab-specific-features)
19. [Phase 14 — Supplier Quality (DEFERRED)](#19-phase-14--supplier-quality-deferred)
20. [Cross-Cutting Workstreams](#20-cross-cutting-workstreams)
21. [Acceptance & Sign-Off Criteria](#21-acceptance--sign-off-criteria)

---

## 1. Build Phase Roadmap

### 1.1 Phase summary

| Phase | Name | Duration | Type | Why this order |
|-------|------|----------|------|----------------|
| **0** | Fix & Stabilize | 1 week | Backend + Frontend | Don't build on a broken base — fix the 4 known defects first |
| **1** | Platform Foundations | 3 weeks | Backend (platform services) | Kafka, audit trail, notifications, file storage — needed by every later phase |
| **2** | Document Control Completion | 2 weeks | Backend + Frontend | Already 80% done; add file upload, MasterControl-style InfoCard, missing fields |
| **3** | Quality Event & CAPA Polish | 2 weeks | Frontend-heavy | Already built backend; needs FBS tabbed forms, root cause UI, missing fields |
| **4** | Training Excellence | 3 weeks | Backend + Frontend | Add Job Codes, Job Code Status Matrix, 5-step training task UX |
| **5** | Equipment Completion | 2 weeks | Backend + Frontend | Add OOT auto-QE, calibration cert PDF, usage logbook, missing detail fields |
| **6** | Audit Management | 4 weeks | Full new module | High-priority new module; depends on CAPA |
| **7** | Environmental Monitoring | 3 weeks | Full new module | IoT integration; depends on Quality Event |
| **8** | Risk Management | 3 weeks | Full new module | Standalone; includes Impartiality Risk Register |
| **9** | Proficiency Testing | 3 weeks | Full new module | Depends on CAPA for unsatisfactory→CAPA flow |
| **10** | Customer Complaints | 3 weeks | Full new module | Depends on CAPA for escalation |
| **11** | Management Review | 2 weeks | Full new module | Aggregates from all prior modules — must come late |
| **12** | Reporting & Analytics | 3 weeks | Backend + Frontend | Replaces stub with real analytics service |
| **13** | Lab-Specific Features | 4 weeks | Distributed | Method Validation, Uncertainty, Control Charts, etc. — competitive moat |
| **14** | Supplier Quality (**DEFERRED**) | 3 weeks | Full new module | Awaiting clarification from manager |

**Total estimated duration:** ~41 weeks (~10 months) at one team. Parallel work possible from Phase 6 onward.

### 1.2 Dependency graph

```
Phase 0 (Fix)
  ↓
Phase 1 (Platform Foundations: Kafka, Audit, Notification, File)
  ↓
  ├── Phase 2 (Document Control Completion)
  │      ↓
  │      └── Phase 4 (Training — needs Document Approved events)
  │
  ├── Phase 3 (Quality Event & CAPA Polish)
  │      ↓
  │      ├── Phase 6 (Audit — Finding→CAPA)
  │      ├── Phase 7 (EM — Excursion→QE)
  │      ├── Phase 9 (PT — Unsatisfactory→CAPA)
  │      └── Phase 10 (Complaints — Escalation→CAPA)
  │
  ├── Phase 5 (Equipment Completion — OOT→QE)
  │
  └── Phase 8 (Risk Management — standalone)

All above → Phase 11 (Management Review)
All above → Phase 12 (Reporting & Analytics)
All above → Phase 13 (Lab-Specific Features)

Phase 14 (Supplier — DEFERRED)
```

### 1.3 What's in scope per phase

Each phase covers four artefacts:

1. **Backend tasks** — services, endpoints, data model, events, tests
2. **Frontend tasks** — pages, components, dialogs, MasterControl-quality UI
3. **Field bindings** — every API field bound to a UI element (no hidden data)
4. **Acceptance criteria** — what "done" looks like

---

## 2. Design System & UI Foundation

Before any UI work, lock down the design system. The reference target is **MasterControl's Quality Excellence Suite** — clean dashboards with tiled widgets, hierarchical Explorer views, single-record InfoCards with right-side tab navigation, drag-and-drop calendars, and compliance matrices.

### 2.1 Visual language reference (from MasterControl screenshots)

| Element | MasterControl pattern to match |
|---------|-------------------------------|
| **Module header** | Module name + breadcrumb (e.g. "MasterControl Documents > View Document InfoCard") |
| **Left navigation** | Always-visible 64-px rail with module icons; expands to 256px showing labels |
| **Dashboard tiles** | 8–12 colored tiles: MY TASKS, MY RECENT, MY TRAINING FOLDER, EXPLORER, ANALYTICS, TRACKING, START TASK, HELP |
| **List view** | Sortable columns, right-side multi-filter sidebar, status badges with semantic colors, pagination |
| **InfoCard (detail) view** | Two-column: left = grouped form sections (Version Info, Main File, Date Info), right = vertical tab nav (Information / Training / Controlled Copies / Attachments & Links / Custom Fields / History / Status / Versions) |
| **Workflow visualization** | Horizontal step progress bar at top of detail page; current step highlighted |
| **FBS (Forms-Based System) tabs** | Tabbed form: About / Complaint Information / Event Reporting / Product Recovery / Investigation / Action Items / Communications Log / Resolution |
| **Calendar** | Month/Week toggle, color-coded events grouped by Status/Owner/Type, drag-and-drop |
| **Matrix view** | Rows = employees, Columns = courses/items, Cell = status icon + tooltip |
| **Pie charts** | Standardized colors per category (e.g. severity: red/orange/yellow/blue) |

### 2.2 Color palette additions (extend current shadcn)

| Token | Purpose | Example use |
|-------|---------|-------------|
| `--status-draft` | gray-500 | Draft documents |
| `--status-review` | amber-500 | Under Review |
| `--status-approved` | emerald-500 | Approved/Effective |
| `--status-obsolete` | red-500 | Obsolete |
| `--status-superseded` | slate-400 | Superseded |
| `--severity-critical` | red-600 | Critical events |
| `--severity-major` | orange-500 | Major NC |
| `--severity-minor` | yellow-500 | Minor NC |
| `--severity-observation` | slate-400 | Observation |
| `--training-complete` | emerald-600 | Job Code Matrix ✅ |
| `--training-in-progress` | blue-500 | Job Code Matrix ⏳ |
| `--training-overdue` | red-500 | Job Code Matrix ⚠️ |
| `--training-waiting` | amber-400 | Waiting on Prerequisite |
| `--training-pending` | slate-300 | Pending Launch |

### 2.3 Shared components to build first

Build these reusable shadcn-based components in `frontend/apps/web/components/qms-shared/` before any module work:

| Component | Purpose | Used by |
|-----------|---------|---------|
| `<ModuleHeader />` | Module title + breadcrumb + action buttons | All module pages |
| `<DashboardTiles />` | Configurable grid of tiles (icon + label + count + click action) | Module dashboards |
| `<FilterSidebar />` | Right-side collapsible multi-filter panel with checkbox groups | List views |
| `<InfoCard />` | Two-column layout with left-side form sections + right-side vertical tabs | All detail pages |
| `<WorkflowStepBar />` | Horizontal step progress bar with active/complete/pending states | Detail pages with workflow |
| `<FBSForm />` | Tabbed form container with form-level state and tab-by-tab validation | Quality Event, CAPA, Complaint detail pages |
| `<StatusBadge variant=… />` | Colored badge using status color tokens | Everywhere |
| `<SeverityBadge variant=… />` | Colored badge for severity | Quality Event, CAPA, Audit Finding |
| `<DragDropCalendar />` | Month/Week calendar with FullCalendar.js, drag-and-drop, grouping | Audit, Equipment Calibration |
| `<MatrixGrid />` | Sticky-header rows × columns grid with status icon cells | Job Code Status Matrix |
| `<SignatureDialog />` | Re-auth + signature meaning declaration modal for 21 CFR Part 11 | All approval flows |
| `<DateInfoGrid />` | 2×3 grid: Created / Released / Effective / Expires / Moved to Phase / Next Review | Document InfoCard |
| `<FileUploadDropzone />` | Drag-and-drop file upload with progress, virus scan status | Documents, Audit evidence, CAPA evidence |
| `<EventTimeline />` | Vertical timeline of audit-trail events with user + timestamp + action | History tab on every InfoCard |

### 2.4 New dependencies to add

```json
{
  "@fullcalendar/react": "^6.x",
  "@fullcalendar/daygrid": "^6.x",
  "@fullcalendar/timegrid": "^6.x",
  "@fullcalendar/interaction": "^6.x",
  "react-dropzone": "^14.x",
  "react-pdf": "^9.x",  // For viewing uploaded PDF documents inline
  "temp-builder": "^1.x",  // Document editor iframe wrapper for editor.manne.work
  "recharts": "already installed — use for module analytics"
}
```

> **Important — Document Authoring:** RainerQMS does **not** use a built-in rich-text editor for SOPs, work instructions, methods, or policies. Document content authoring uses the **external editor at `https://editor.manne.work`**, integrated via the `temp-builder` React component which wraps the editor as an iframe. See [Section 4 — Document Editor Integration](#4-document-editor-integration-editormannework) for the complete integration guide. The TipTap dependency previously mentioned in earlier drafts is **removed** in favour of `temp-builder`.

---

## 3. UI Reference Image Mapping

The team committed every MasterControl screenshot and supporting reference UI image to the codebase. Every module, page, and component spec in this build plan must visually match a specific reference image. Implementers should open the referenced image alongside the spec while building.

### 3.1 Where the images live

**Reference location in repo:** `frontend/apps/web/public/ui-reference-images/` (also accessible to designers without running the dev server at `https://<host>/ui-reference-images/<filename>`).

> **Action item:** If your local checkout does not have this folder, copy the original screenshots from the two onboarding chats (the 19 MasterControl images + the `New Article` knowledge-base reference) into that path before starting any UI work. The folder is part of the source repo, not gitignored.

### 3.2 Per-page reference image mapping

For every page spec in Phases 0–13, this table tells the implementer which reference image to copy visually. File names follow the pattern `<module>-<page>-<index>.jpeg`. Filenames below are the conventional names — match whatever is in your local folder.

| Module / Page | Build Plan Section | Reference Image(s) |
|---------------|-------------------|--------------------|
| **Global — Dashboard with "My X" tiles** | §2.3, §3.2 | `documents-dashboard-01.jpeg` (My MasterControl with 12 tiles) |
| **Global — Left navigation rail** | §2.3 | `documents-dashboard-01.jpeg` (the persistent sidebar) |
| **Documents — Create Page (NEW)** | §7.2.0 | `knowledge-base-new-article.jpeg` (the New Article reference — left nav + breadcrumb + title + content editor + right-side Settings panel) |
| **Documents — Explorer / List** | §7.2.1 | `documents-dashboard-02.jpeg` (Documents workspace with tiles), `documents-explorer-list.jpeg` (Explorer breadcrumb), `documents-explorer-product-line.jpeg` (Product Line drilldown) |
| **Documents — InfoCard / Detail** | §7.2.2 | `documents-infocard-view.jpeg` (Version Info, Main File, Date Information, right-side tabs) |
| **Documents — Collaboration Workspace** | §7.2 (Distribution tab) | `documents-collaboration-workspace.jpeg`, `documents-add-comments-dialog.jpeg` |
| **Quality Event — List (Pending Tasks)** | §8.2.1 | `capa-pending-tasks-list.jpeg` (My Tasks > Pending Tasks > Complaints) |
| **Quality Event — Detail FBS tabbed form** | §8.2.2 | `capa-customer-complaint-fbs.jpeg` (8 tabs across the top), `capa-issue-review-fbs.jpeg`, `capa-form-links-popup.jpeg` |
| **CAPA — Hub diagram (for marketing/overview page)** | §8.3 | `capa-system-hub-diagram.jpeg` |
| **CAPA — Event Analyzer Agents (Phase 13 advanced)** | §18 (future) | `capa-event-analyzer-proposed-matches.jpeg`, `capa-event-analyzer-confirmed-matches.jpeg` |
| **CAPA — Analytics charts** | §8.3 detail page | `capa-analytics-pie-charts.jpeg` (CAPA by Department / Complaints by Product / NCMR Disposition) |
| **Audit — Dashboard** | §11.2.1 | `audit-dashboard-my-tasks.jpeg` |
| **Audit — Workspace 4 tabs** | §11.2.3 | `audit-workspace-information-tab.jpeg` (Information / Documentation / Observations / Checklist) |
| **Audit — Calendar drag-and-drop** | §11.2.2 | `audit-calendar-month-view.jpeg` (Month/Week toggle + color-coded events + Event Grouping panel) |
| **Audit — Auditor picker (two-column)** | §11.2.4 | `audit-details-supplier-picker.jpeg` (Available / Qualified Auditors picker pattern) |
| **Supplier — Dashboard (DEFERRED)** | §19 | `supplier-dashboard.jpeg` |
| **Supplier — List with filter sidebar** | §19 | `supplier-list-with-filter-sidebar.jpeg` |
| **Supplier — Advanced Search builder** | §19 | `supplier-advanced-search.jpeg` |
| **Supplier — Retrieve InfoCards** | §19 | `supplier-retrieve-infocards.jpeg` |
| **Supplier — View Supplier InfoCard** | §19 | `supplier-view-infocard.jpeg` |
| **Training — Dashboard tiles** | §9.2.1 | `training-dashboard-tiles.jpeg` (11 tiles) |
| **Training — 5-step Training Task** | §9.2.3 | `training-task-5-step.jpeg` (Introduction → Materials → Exam → Overview → Sign Off) |
| **Training — Job Code Status Matrix** | §9.2.2 | `training-job-code-status-matrix.jpeg` (per-employee × per-course heatmap with status icons) |

### 3.3 How to follow the references

For every page implementation:
1. Open the reference image side-by-side with this spec
2. Match the **layout** (column widths, sidebar positions, tab placement)
3. Match the **typography hierarchy** (header sizes, label styles)
4. Match the **color usage** (status badges, severity colors per the design system tokens in §2.2)
5. Where shadcn/ui primitives exist, prefer them over hand-rolled markup — but the visual outcome must match the reference
6. The reference is **MasterControl-quality** — that means clean spacing, breadcrumbs on every page, no orphan controls, consistent button placement (primary actions top-right)

### 3.4 Deviations from the reference

The build plan deliberately deviates from MasterControl in these places (do not match the reference here):

| Where | Why we deviate |
|-------|---------------|
| **Document content authoring** | RainerQMS uses external editor.manne.work iframe; MasterControl uses native rich text. See §4. |
| **CAPA risk model** | Spec uses 3-factor RPN (Severity × Occurrence × Detectability); MasterControl uses 2-factor F×I. See §8 detail page. |
| **Multi-tenancy** | RainerQMS is multi-tenant SaaS; MasterControl is single-tenant per deployment. |
| **Lab-specific modules** | RainerQMS adds Method Validation, PT, Calibration Certificates, etc. (Phase 13) — not in MasterControl. |

---

## 4. Document Editor Integration (editor.manne.work)

This section defines exactly how the RainerQMS document service integrates with the external Template Builder editor hosted at `https://editor.manne.work`. The integration uses the **iframe approach** via the `temp-builder` npm package (a React wrapper that hides the underlying `postMessage` protocol).

### 4.1 What is `editor.manne.work`?

A standalone web application built and operated separately from RainerQMS. It provides:
- A WYSIWYG document editor (`https://editor.manne.work/`)
- A read-only viewer (`https://editor.manne.work/?mode=viewer`)
- Documentation (`https://editor.manne.work/docs`)

RainerQMS uses this editor for **authoring** the body content of SOPs, work instructions, methods, policies, forms, and manuals. The editor produces two artefacts on save:
- **`content_ast`** — ProseMirror JSON, used to re-open the document for editing
- **`html_snapshot`** — HTML, used for display, export, and PDF generation

### 4.2 Two document authoring modes — both supported

Every RainerQMS document can be authored in **one of two ways**, chosen by the user on the Create Document page:

| Mode | When to use | What's stored |
|------|-------------|---------------|
| **Mode A — Upload existing file** | User has an existing `.docx`, `.pdf`, `.xlsx`, image, etc. | Uploaded binary stored via file-service → `Document.file_id`. No `content_ast`, no `html_snapshot`. |
| **Mode B — Author in embedded editor** | User wants to write a new SOP / WI inline using the structured editor | `Document.content_ast` (ProseMirror JSON) + `Document.html_snapshot` (rendered HTML). No `file_id` for the body. |

Both modes coexist for the same document type. A user creating an SOP can either upload an existing Word doc or write it inline — their choice. The Document InfoCard displays whichever mode was used.

### 4.3 Required schema additions to `Document` table

Add to `document-service/app/infra/db/models.py` and a new migration:

```python
class Document(Base):
    # ... existing fields ...
    authoring_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="upload")
    # values: "upload" | "embedded_editor"

    content_ast: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # ProseMirror JSON from editor.manne.work — for re-editing

    html_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Rendered HTML — for display, search, export

    editor_nonce: Mapped[str | None] = mapped_column(String(64), nullable=True)
    # Most recent save nonce from editor — used for staleness detection
```

Per-version snapshots (existing `DocumentVersion` table) should mirror these columns so each version retains its own AST + HTML:

```python
class DocumentVersion(Base):
    # ... existing fields ...
    authoring_mode: Mapped[str] = mapped_column(String(20), nullable=False, default="upload")
    content_ast: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    html_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_id: Mapped[str | None]  # already exists
```

### 4.4 Required backend endpoints

Add to `document-service/app/api/v1/routes/documents.py`:

| Method | Path | Purpose | Auth |
|--------|------|---------|------|
| `POST` | `/documents/{id}/content` | Save the AST + HTML coming from the editor. Body: `{ content_ast, html_snapshot, nonce }`. Updates `Document.content_ast`, `Document.html_snapshot`, `Document.editor_nonce`. Returns 200 with updated `Document`. | Requires `DOCUMENT_WRITE` and document in `draft` state. |
| `GET` | `/documents/{id}/content` | Returns `{ content_ast, html_snapshot, authoring_mode }` for re-opening the editor or rendering the viewer. | Requires `DOCUMENT_READ`. |
| `POST` | `/documents/{id}/content/snapshot` | On version creation, snapshots current AST/HTML into the new `DocumentVersion` row. Internal — called by `create_new_version` flow (Phase 0 D-2). | Internal. |

All three emit audit-trail events (Phase 1 audit service).

### 4.5 Required frontend integration — install and configure

Install the editor wrapper:

```bash
cd frontend/apps/web
npm install temp-builder
```

Set an environment variable so the iframe origin is overridable per environment:

```bash
# .env.local (dev)
NEXT_PUBLIC_UMO_EDITOR_URL=https://editor.manne.work

# .env.production
NEXT_PUBLIC_UMO_EDITOR_URL=https://editor.manne.work
```

The editor will be loaded via iframe to this origin. To support local testing, point to `http://localhost:5173` (or wherever the editor dev server is running).

### 4.6 New page — `/qms/documents/create`

This is a **new dedicated route** replacing the simple "+ New Document" dialog. Visual reference: `knowledge-base-new-article.jpeg`.

#### 4.6.1 Layout

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ [Logo]              Home › Documents › New Document                          │
├──────────┬──────────────────────────────────────────────────────────────────┤
│          │ ┌──────────────────────────────────────┐  ┌────────────────────┐ │
│ 📋 Docs  │ │ Document Content                      │  │ Settings           │ │
│ ⚠️ Events│ │ Author your SOP using the editor or  │  │                    │ │
│ 🔧 CAPA  │ │ upload an existing file               │  │ Document Number *  │ │
│ 🎓 Train │ │                                       │  │ [SOP-MICRO-0042 ]  │ │
│ 🛠️ Equip │ │ Title *                               │  │                    │ │
│ ... etc  │ │ [Labeling Procedure                ]  │  │ Type *             │ │
│          │ │                                       │  │ [SOP            ▼] │ │
│          │ │ Authoring Mode                        │  │                    │ │
│          │ │ ( • ) Author in editor               │  │ Department         │ │
│          │ │ (   ) Upload existing file            │  │ [Microbiology   ▼] │ │
│          │ │                                       │  │                    │ │
│          │ │ Excerpt / Summary                     │  │ Vault              │ │
│          │ │ [Brief summary of the document    ]  │  │ [QA-Released    ▼] │ │
│          │ │                                       │  │                    │ │
│          │ │ ┌─────────────────────────────────┐  │  │ Folder / Taxonomy  │ │
│          │ │ │  ┌──────────────────────────┐   │  │  │ [Docs by Dept...▼] │ │
│          │ │ │  │                          │   │  │  │                    │ │
│          │ │ │  │   editor.manne.work       │   │  │  │ Effective Date     │ │
│          │ │ │  │   IFRAME (TemplateEditor) │   │  │  │ [____________]     │ │
│          │ │ │  │                          │   │  │  │                    │ │
│          │ │ │  │   (when Mode A selected)  │   │  │  │ Review Frequency   │ │
│          │ │ │  │                          │   │  │  │ [12 months      ▼] │ │
│          │ │ │  └──────────────────────────┘   │  │  │                    │ │
│          │ │ └─────────────────────────────────┘  │  │ ISO Clauses        │ │
│          │ │                                       │  │ [8.3, 8.4       ]  │ │
│          │ │ — OR (when Mode B selected) —        │  │                    │ │
│          │ │                                       │  │ Tags               │ │
│          │ │ ┌─────────────────────────────────┐  │  │ [labeling] [QA] +  │ │
│          │ │ │     📤 Drop file here or click  │  │  │                    │ │
│          │ │ │        Max 100 MB                │  │  │ Regulatory         │ │
│          │ │ │     PDF, DOCX, XLSX, PNG, JPG   │  │  │ ☑ FDA 21 CFR Pt 11│ │
│          │ │ └─────────────────────────────────┘  │  │ ☐ ISO 17025        │ │
│          │ │                                       │  │                    │ │
│          │ │                                       │  │ Owner              │ │
│          │ │                                       │  │ [Rajesh Patel  ▼]  │ │
│          │ │                                       │  │                    │ │
│          │ │                                       │  │ Approver(s)        │ │
│          │ │                                       │  │ [Dr. Priya     ▼]  │ │
│          │ │                                       │  │                    │ │
│          │ │                                       │  │ [💾 Save as Draft] │ │
│          │ │                                       │  │ [📤 Submit Review] │ │
│          │ │                                       │  │ [← Cancel         ]│ │
│          │ └──────────────────────────────────────┘  └────────────────────┘ │
└──────────┴──────────────────────────────────────────────────────────────────┘
```

**Layout rules:**
- Three-column responsive layout: persistent left nav, main content area (~60%), Settings sidebar (~30%)
- Title and Authoring Mode radio appear above the iframe / dropzone
- The editor iframe is rendered when Mode A is selected; the dropzone is rendered when Mode B is selected — they swap based on the radio
- Settings sidebar is sticky on scroll
- Save as Draft saves all metadata + current editor state; Submit Review additionally transitions status to `under_review`

#### 4.6.2 Component code outline

Create `frontend/apps/web/app/(qms)/qms/documents/create/page.tsx`:

```tsx
'use client'

import { useEffect, useRef, useState } from 'react'
import { useRouter } from 'next/navigation'
import { TemplateEditor, type TemplateEditorRef, type SaveResponsePayload } from 'temp-builder'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { useCreateDocument, useSaveDocumentContent } from '@/lib/api/hooks/documents'
import { useAuth } from '@/lib/stores/auth.store'
import { z } from 'zod'

const createDocumentSchema = z.object({
  doc_number: z.string().min(1),
  title: z.string().min(1),
  doc_type: z.enum(['sop', 'wi', 'method', 'policy', 'form', 'manual']),
  department: z.string().optional(),
  vault: z.enum(['qa_released', 'qa_draft', 'external']).default('qa_draft'),
  folder_id: z.string().optional(),
  effective_date: z.string().optional(),
  review_frequency_months: z.number().default(12),
  iso_clause_mapping: z.string().optional(),
  tags: z.array(z.string()).default([]),
  regulatory_frameworks: z.array(z.string()).default([]),
  owner_id: z.string(),
  approver_id: z.string().optional(),
  description: z.string().optional(),
  authoring_mode: z.enum(['embedded_editor', 'upload']),
})

export default function CreateDocumentPage() {
  const router = useRouter()
  const auth = useAuth()
  const editorRef = useRef<TemplateEditorRef>(null)
  const [authoringMode, setAuthoringMode] = useState<'embedded_editor' | 'upload'>('embedded_editor')
  const [pendingContent, setPendingContent] = useState<SaveResponsePayload | null>(null)
  const [uploadedFile, setUploadedFile] = useState<File | null>(null)

  const createDocument = useCreateDocument()
  const saveContent = useSaveDocumentContent()

  const form = useForm({
    resolver: zodResolver(createDocumentSchema),
    defaultValues: { authoring_mode: 'embedded_editor' as const, tags: [], regulatory_frameworks: [] },
  })

  // Step 1: when editor signals a save, hold the AST/HTML in state
  const handleEditorSave = (data: SaveResponsePayload) => {
    if (data.success) setPendingContent(data)
  }

  // Step 2: on "Save as Draft" — first create the document, then attach content
  const handleSaveAsDraft = form.handleSubmit(async (values) => {
    const doc = await createDocument.mutateAsync(values)

    if (values.authoring_mode === 'embedded_editor') {
      // Ask editor for latest content (in case user hasn't clicked the editor's own Save yet)
      const latest = pendingContent ?? await new Promise<SaveResponsePayload>((resolve) => {
        editorRef.current?.saveRequest()
        // The onSave callback will fire and we capture it via state — for simplicity wait one tick
        setTimeout(() => resolve(pendingContent!), 500)
      })
      await saveContent.mutateAsync({
        documentId: doc.id,
        content_ast: latest.content_ast,
        html_snapshot: latest.html_snapshot,
        nonce: latest.nonce,
      })
    } else if (values.authoring_mode === 'upload' && uploadedFile) {
      // Upload file via file-service; backend wires file_id to document
      const fileResponse = await uploadFile(uploadedFile)
      await attachFileToDocument(doc.id, fileResponse.file_id)
    }

    router.push(`/qms/documents/${doc.id}`)
  })

  return (
    <div className="grid grid-cols-[1fr_360px] gap-6 p-6">
      <div className="space-y-4">
        <h1 className="text-xl font-semibold">Document Content</h1>
        <p className="text-sm text-muted-foreground">
          Author your SOP using the editor or upload an existing file
        </p>

        <Input label="Title *" {...form.register('title')} />

        <RadioGroup value={authoringMode} onValueChange={(v) => {
          setAuthoringMode(v as typeof authoringMode)
          form.setValue('authoring_mode', v as typeof authoringMode)
        }}>
          <Radio value="embedded_editor">Author in editor</Radio>
          <Radio value="upload">Upload existing file</Radio>
        </RadioGroup>

        <Textarea label="Excerpt / Summary" {...form.register('description')} />

        {authoringMode === 'embedded_editor' ? (
          <TemplateEditor
            ref={editorRef}
            authToken={auth.access_token}
            tenantId={auth.tenant_id}
            onSave={handleEditorSave}
            onReady={() => console.log('Editor ready')}
            height="700px"
          />
        ) : (
          <FileUploadDropzone
            onFileSelect={setUploadedFile}
            maxSize={100 * 1024 * 1024}
            accept={['.pdf', '.docx', '.xlsx', '.png', '.jpg', '.jpeg']}
          />
        )}
      </div>

      <aside className="space-y-4 sticky top-6 self-start">
        <h2 className="text-lg font-semibold">Settings</h2>
        <SelectField label="Document Number *" name="doc_number" form={form} />
        <SelectField label="Type *" name="doc_type" form={form} options={DOC_TYPES} />
        <SelectField label="Department" name="department" form={form} options={DEPARTMENTS} />
        <SelectField label="Vault" name="vault" form={form} options={VAULTS} />
        <SelectField label="Folder / Taxonomy" name="folder_id" form={form} options={FOLDERS} />
        <DatePicker label="Effective Date" name="effective_date" form={form} />
        <SelectField label="Review Frequency" name="review_frequency_months" form={form} options={REVIEW_FREQUENCIES} />
        <Input label="ISO Clauses" {...form.register('iso_clause_mapping')} />
        <TagInput label="Tags" name="tags" form={form} />
        <MultiCheckboxGroup label="Regulatory" name="regulatory_frameworks" form={form} options={REG_FRAMEWORKS} />
        <UserPicker label="Owner" name="owner_id" form={form} />
        <UserPicker label="Approver(s)" name="approver_id" form={form} />

        <div className="space-y-2 pt-4 border-t">
          <Button onClick={handleSaveAsDraft} className="w-full">💾 Save as Draft</Button>
          <Button variant="outline" onClick={() => {/* Submit Review flow */}} className="w-full">📤 Submit Review</Button>
          <Button variant="ghost" onClick={() => router.back()} className="w-full">← Cancel</Button>
        </div>
      </aside>
    </div>
  )
}
```

> The above is a structural reference — actual implementation should split UI fragments into `<DocumentMetadataSidebar />`, `<DocumentAuthoringPane />`, etc., and reuse existing shadcn primitives.

#### 4.6.3 Editing an existing document

When opening an already-created document in `draft` state for editing, fetch the prior `content_ast` and pass it to the editor via `initialContentAst`:

```tsx
// app/(qms)/qms/documents/[id]/edit/page.tsx
const { data: doc } = useDocument(id)
const { data: content } = useDocumentContent(id) // fetches from new GET /documents/{id}/content

return (
  <TemplateEditor
    ref={editorRef}
    authToken={auth.access_token}
    tenantId={auth.tenant_id}
    templateId={doc.id}
    initialContentAst={content?.content_ast}
    onSave={handleEditorSave}
    height="700px"
  />
)
```

The editor opens with the saved content fully restored. The user makes changes, clicks the editor's Save button, the wrapper's `onSave` fires, and we POST to `/documents/{id}/content`.

#### 4.6.4 Viewing an approved document

For the read-only InfoCard display of an Effective document authored in embedded mode, render the `html_snapshot` directly OR embed the viewer mode of the editor:

```tsx
// Option 1 — render the saved HTML directly (faster, no iframe overhead)
<div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: doc.html_snapshot }} />

// Option 2 — use TemplateViewer for fidelity (handles print pagination, conditional blocks at render time)
import { TemplateViewer } from 'temp-builder'

<TemplateViewer
  html={doc.html_snapshot}
  title={doc.title}
  meta={[
    { label: 'Document #', content: doc.doc_number },
    { label: 'Version', content: doc.current_version },
    { label: 'Effective', content: doc.effective_date },
  ]}
  height="700px"
/>
```

Prefer **Option 2 (TemplateViewer)** when the document uses conditional blocks (`data-show-when`), tables with row visibility, or `{{path}}` variable interpolation — the viewer's render pipeline handles all three correctly. Prefer **Option 1** for simple static documents to avoid an additional iframe load.

For uploaded `.pdf` documents, use `react-pdf`. For uploaded `.docx`, render in `react-pdf` after server-side conversion (Phase 13) or surface a Download button only.

#### 4.6.5 Per-version snapshots

When a user creates a new version of an approved document (Phase 0 D-2 flow):

1. The `create_new_version` service method snapshots the current `Document.content_ast` and `Document.html_snapshot` into the new `DocumentVersion` row via `POST /documents/{id}/content/snapshot`
2. The new version's status becomes `draft`
3. The Edit page opens the editor pre-loaded with the snapshotted `content_ast`
4. User edits, saves, content of the **new version** updates while the **previous version** retains its frozen snapshot

The Versions tab on the InfoCard lets the user open any prior version in the read-only viewer.

### 4.7 Authentication handoff to the editor

The `temp-builder` component accepts an `authToken` prop and a `tenantId` prop, which it forwards to the editor iframe via `postMessage` on initialization. The editor uses these for:
- Asset uploads (the editor's own asset endpoint receives the auth token)
- Tenant scoping of uploaded images, files, and field catalogs

Pass these from the Zustand auth store:

```tsx
const auth = useAuth()
<TemplateEditor authToken={auth.access_token} tenantId={auth.tenant_id} ... />
```

If the editor needs to call back to RainerQMS (for example, to fetch a field catalog of available `{{path}}` placeholders), expose a public endpoint in the document service (`GET /documents/field-catalog`) that the editor calls with the auth token.

### 4.8 Field catalog (for `{{path}}` placeholders and conditional blocks)

The editor supports placeholder variables like `{{patient.name}}` and conditional blocks like "show this section if `patient.isVip` is truthy." Pass the list of allowed field paths via the `fieldCatalog` prop:

```tsx
<TemplateEditor
  fieldCatalog={[
    { code: 'sample.id', label: 'Sample ID', kind: 'text' },
    { code: 'sample.received_date', label: 'Received Date', kind: 'date' },
    { code: 'analyst.name', label: 'Analyst Name', kind: 'text' },
    // ...
  ]}
  ...
/>
```

For Phase 2, supply a static field catalog covering common lab variables. For Phase 13 (Lab-Specific Features), generate the catalog dynamically per document type (e.g. a Calibration Certificate document gets equipment + standards + uncertainty fields).

### 4.9 Conditional block render contract

The editor serializes conditional blocks as:

```html
<div class="conditional-block"
     data-show-when="patient.isVip"
     data-condition-mode="truthy"
     data-conditional-kind="section"
     data-conditional-label="VIP-only paragraph"
     data-conditional-version="1">
  ...
</div>
```

When rendering with `TemplateViewer`, the viewer evaluates `data-show-when` against the supplied `data` prop and either includes or omits the block. When rendering via `dangerouslySetInnerHTML`, the `.conditional-block` divs are visible as-is — therefore prefer `TemplateViewer` for any document containing conditional blocks.

### 4.10 Save and update flow — sequence diagram

```
User → /qms/documents/create page
    Selects Mode A (Author in editor)
    Fills metadata in Settings sidebar
    Writes content in iframe (editor.manne.work)
    Clicks "Save as Draft" in RainerQMS

Frontend  → POST /api/v1/documents (metadata only, no content)
Backend   ← 201 Created { id, doc_number, status: 'draft', ... }

Frontend  → editorRef.current.saveRequest()  // ask editor to emit latest content
Editor    → onSave callback fires with { content_ast, html_snapshot, nonce }
Frontend  → POST /api/v1/documents/{id}/content { content_ast, html_snapshot, nonce }
Backend   ← 200 OK { content saved, audit-trail event emitted }

Frontend  → router.push(`/qms/documents/${doc.id}`)
```

For Mode B (upload):

```
User → fills metadata, drops a .docx file
    Clicks "Save as Draft"

Frontend  → POST /api/v1/files (multipart) → { file_id }
Frontend  → POST /api/v1/documents (metadata + file_id, authoring_mode='upload')
Backend   ← 201 Created
```

### 4.11 Imperative API reference (for advanced cases)

The `TemplateEditor` exposes a ref-based imperative API. RainerQMS uses these methods:

| Method | When RainerQMS uses it |
|--------|------------------------|
| `loadTemplate({ content_ast })` | When opening a saved document for editing (initial load) |
| `saveRequest()` | When the user clicks RainerQMS's "Save as Draft" before the editor's own save button has been pressed |
| `getContent()` | When generating a preview without committing a save |
| `insertPlaceholder(code, label, kind)` | When a user drags a field from the field catalog sidebar onto the editor canvas (Phase 13 feature) |
| `insertConditionalBlock(...)` | Same as above for conditional sections |
| `setReadonly(true)` | When opening an Effective document in viewer mode but the user later clicks "Edit" — flip to editable |

### 4.12 Acceptance criteria for editor integration

- [ ] `temp-builder` installed and configured with environment-aware `NEXT_PUBLIC_UMO_EDITOR_URL`
- [ ] Backend `Document` schema gains `authoring_mode`, `content_ast`, `html_snapshot`, `editor_nonce` columns
- [ ] Backend `DocumentVersion` schema gains matching columns for per-version snapshots
- [ ] New endpoints `POST /documents/{id}/content`, `GET /documents/{id}/content`, `POST /documents/{id}/content/snapshot` work
- [ ] `/qms/documents/create` page renders with three-column layout, breadcrumb, Authoring Mode radio
- [ ] Mode A: user authors in iframe → clicks Save as Draft → content persists → reopening Edit page restores content
- [ ] Mode B: user drops a file → clicks Save as Draft → file uploaded → document created with `file_id`
- [ ] Editing a draft document re-opens the iframe with prior content loaded
- [ ] Viewing an approved embedded-mode document renders the HTML correctly (via `<TemplateViewer>` if conditional blocks present, else via direct HTML render)
- [ ] Creating a new version snapshots the current content into the prior version, leaves the new version editable
- [ ] All content save/update operations emit audit-trail events
- [ ] No content authoring inside RainerQMS itself — TipTap and other built-in editor dependencies removed
- [ ] CSP / iframe-src directive allows `editor.manne.work` in the Next.js config

### 4.13 Build plan impact

The editor integration affects the following phases — each phase's section has been (or will be) updated accordingly:

| Phase | Impact |
|-------|--------|
| **Phase 0 (§5)** | No impact — still fix the 4 defects first; D-2 additionally snapshots `content_ast`+`html_snapshot` into prior version on `create_new_version` |
| **Phase 1 (§6)** | File service (§6.3) is still needed for Mode B uploads; audit trail service (§6.2) captures all editor save operations |
| **Phase 2 (§7)** | **Major** — the `/qms/documents/create` page replaces the simple "+ New Document" dialog; new endpoints added; schema migration required. See §7.2.0. |
| **Phase 4 (§9)** | The Training Materials step (5-step task) can use `<TemplateViewer>` to display the linked SOP content inline |
| **Phase 6 (§11)** | Audit Report tab can use the editor to compose audit reports |
| **Phase 11 (§16)** | Management Review meeting minutes can be authored in the editor |
| **Phase 13 (§18)** | Calibration Certificates can be authored via the editor with dynamic field catalog |

---

## 5. Phase 0 — Fix & Stabilize Existing Modules

**Duration:** 1 week
**Goal:** Fix the 4 known defects before building anything new. A broken foundation poisons every later phase.

### 5.1 Defect D-1: ORM column drift (`last_rejection_reason`)

**Where:** `document-service/app/infra/db/models.py`
**Symptom:** Column exists in migration 002, missing from SQLAlchemy `Document` model. Reject endpoint writes succeed at SQL level but ORM reads return nothing.

**Tasks:**
- [ ] Add `last_rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)` to `Document` model
- [ ] Verify no other migration-vs-ORM drift exists (script: dump migrations, dump ORM columns, diff)
- [ ] Add unit test: create doc → submit → reject with reason → reload → assert reason persisted

### 5.2 Defect D-2: Dead `create_new_version` transition

**Where:** `document-service/app/domain/services.py` (transition defined), no handler exists
**Symptom:** Transition lists `approved → draft` via `create_new_version`, but no method or endpoint implements it. Cannot create v2.0 of an existing document.

**Tasks:**
- [ ] Implement `create_new_version(document_id, new_file_id, change_summary)` service method that:
  - Validates document is in `approved` status
  - Computes next version number (e.g. 1.0 → 2.0 if major, 1.0 → 1.1 if minor — add `change_type` enum)
  - Creates new `DocumentVersion` row
  - **Snapshots the prior version's `content_ast` and `html_snapshot` into that prior `DocumentVersion` row** (so the previous version's content is frozen)
  - Updates parent `Document.current_version`
  - Sets parent `Document.status = draft` (new edit cycle)
  - Marks previous version as `superseded` (see D-4)
  - Emits `Document.VersionCreated` event
- [ ] Add API endpoint `POST /documents/{id}/versions`
- [ ] Add unit + E2E tests
- [ ] Add frontend dialog (Phase 2)

### 5.3 Defect D-3: Dead acknowledgment code

**Where:** `document_acknowledgments` table + `DocumentAcknowledgment` model exist; no API, no service, no repository.
**Symptom:** Distribution list members cannot acknowledge they've read a new document — spec requires this for ISO 17025 compliance.

**Tasks:**
- [ ] Add repository: `AcknowledgmentRepository.create()`, `.list_for_document()`, `.list_for_user()`, `.get_compliance_stats()`
- [ ] Add service: `acknowledge_document(document_id, user_id, signature)` — creates row with SHA-256 hash
- [ ] Add API endpoints:
  - `POST /documents/{id}/acknowledge` — current user acknowledges
  - `GET /documents/{id}/acknowledgments` — list (Quality Manager view)
  - `GET /me/acknowledgments/pending` — user's pending acknowledgments
- [ ] Add frontend (Phase 2)

### 5.4 Defect D-4: Missing `Superseded` & `Effective` states

**Where:** State machine in `document-service`
**Symptom:** Document goes `approved → obsolete` directly. Industry/spec requires `approved → effective → superseded → obsolete`.

**Tasks:**
- [ ] Add states to enum: `APPROVED`, `EFFECTIVE`, `SUPERSEDED`, `OBSOLETE`
- [ ] Add transitions:
  - `approved → effective` (automatic on effective_date OR manual "Release" action)
  - `effective → superseded` (automatic when new version becomes effective)
  - `effective → obsolete` (manual retirement)
  - `superseded → obsolete` (manual archival)
- [ ] Add scheduled job (Phase 1 scheduler) to auto-transition `approved → effective` on effective_date
- [ ] Update frontend status badges and dropdown filters (Phase 2)

### 5.5 Quality gates for existing modules

While we're here, also:
- [ ] Add missing unit tests for `document-service` (reject, update, delete, list, due-for-review, distribution, get-versions) — get unit test coverage from 8 to 15+
- [ ] Add unit tests for `quality-event-service` (currently 1 test, 109 lines) — target 8+ tests
- [ ] Add unit tests for `capa-service` (currently 1 test, 110 lines) — target 10+ tests
- [ ] Add unit tests for `training-service` (currently 1 test, 138 lines) — target 8+ tests
- [ ] Add unit tests for `equipment-service` (currently 1 test, 178 lines) — target 10+ tests

### 5.6 Acceptance criteria

- [ ] All 4 defects fixed and verified by automated tests
- [ ] Unit test count per service ≥ target above
- [ ] `npm run test` passes
- [ ] `pytest` passes for all 5 built services
- [ ] CI pipeline green

---

## 6. Phase 1 — Platform Foundations

**Duration:** 3 weeks
**Goal:** Stand up the 4 platform services that every module depends on. Without these, the "integrated QMS" value proposition cannot work.

### 6.1 Service 1: Notification Service

**Current state:** Stub only.
**Build:**

**Backend tasks:**
- [ ] Choose mail provider (SendGrid / AWS SES / Resend) and add config
- [ ] Implement endpoints:
  - `POST /notifications` — send a notification (channels: email, in-app, webhook)
  - `GET /notifications/me` — list current user's in-app notifications
  - `POST /notifications/{id}/mark-read` — mark in-app notification read
  - `GET /notifications/me/unread-count` — for header bell badge
- [ ] Implement Kafka consumer that listens to events from other services and dispatches notifications based on user preferences
- [ ] Add templates per event type (Document Approved, CAPA Assigned, Training Due, Calibration Due, etc.)
- [ ] Add user preferences endpoint: which events → which channel

**Frontend tasks:**
- [ ] Bell icon in header (already exists) — wire to live API
- [ ] In-app notification dropdown panel with mark-read, mark-all-read
- [ ] Notification preferences page under `/settings/notifications` (event type × channel matrix)
- [ ] Socket.io-client real-time push of new in-app notifications

**Acceptance:**
- [ ] Approve a document → distribution list members receive email within 60 seconds
- [ ] User sees unread count badge update without page refresh

### 6.2 Service 2: Audit Trail Service

**Current state:** Stub only.
**Build:**

**Backend tasks:**
- [ ] Append-only Postgres table `audit_trail_records` with fields:
  - `id`, `tenant_id`, `actor_user_id`, `actor_email` (immutable snapshot), `actor_role`, `event_type`, `entity_type`, `entity_id`, `action` (create/update/approve/sign/delete), `before_snapshot` (JSONB), `after_snapshot` (JSONB), `signature_hash`, `client_ip`, `user_agent`, `timestamp`
- [ ] Endpoints:
  - `POST /audit-trail` — emit event (called by Kafka consumer; also direct from services)
  - `GET /audit-trail` — query (filterable by entity, actor, date range) — admin/QM only
  - `GET /audit-trail/entity/{type}/{id}` — full history for one record
  - `GET /audit-trail/export` — CSV/PDF export (for regulatory submissions)
- [ ] Add Kafka consumer that ingests events from all domain services and persists them
- [ ] Verify append-only: no UPDATE or DELETE permissions on the table (DB-level enforcement)

**Frontend tasks:**
- [ ] `History` tab on every InfoCard (Document, QE, CAPA, etc.) using `<EventTimeline />` component — shows actor, timestamp, action, before/after diff for fields that changed
- [ ] Global Audit Log page at `/admin/audit-log` (Quality Manager + super admin only) with filters and export buttons

**Acceptance:**
- [ ] Every create/update/approve/reject/delete operation across all services emits an audit trail event
- [ ] History tab on a document shows every action taken on it, with diffs

### 6.3 Service 3: File Service

**Current state:** Stub only. `file_id` fields in many models point to nothing.
**Build:**

**Backend tasks:**
- [ ] S3-compatible storage (AWS S3 or MinIO for dev)
- [ ] Endpoints:
  - `POST /files` — multipart upload, returns `file_id` + signed download URL
  - `GET /files/{id}` — fetch metadata (filename, size, mime_type, virus_scan_status, uploaded_by, uploaded_at)
  - `GET /files/{id}/download` — generates time-limited signed download URL
  - `GET /files/{id}/preview` — generates time-limited signed preview URL (for PDFs/images)
  - `DELETE /files/{id}` — soft delete (preserves audit trail)
- [ ] Virus scan integration (ClamAV) — files marked `pending` → `clean` or `infected`
- [ ] Tenant-scoped storage paths: `s3://bucket/{tenant_id}/{file_id}/{filename}`
- [ ] Max file size config (default 100 MB)

**Frontend tasks:**
- [ ] `<FileUploadDropzone />` shared component with progress bar, virus scan status indicator
- [ ] `<FilePreview />` component using `react-pdf` for PDFs, native `<img>` for images, download button for others
- [ ] Wire into Document Control (Phase 2), Audit (Phase 6), CAPA evidence, equipment calibration certificates

**Acceptance:**
- [ ] Upload a 10 MB PDF to a document, see virus scan complete, preview inline, download succeeds
- [ ] Tenant isolation verified: tenant A cannot fetch tenant B's files even with the right `file_id`

### 6.4 Service 4: Kafka Event Bus (wire-up)

**Current state:** `rainer_events` producer library exists but is imported nowhere.

**Backend tasks:**
- [ ] Add Kafka topic schema per event type (consider Avro / JSON Schema)
- [ ] Wire `rainer_events` producer into every domain service:
  - Document Service: `Document.Created`, `.SubmittedForReview`, `.Approved`, `.Rejected`, `.Effective`, `.Superseded`, `.Obsolete`, `.VersionCreated`, `.Acknowledged`
  - Quality Event Service: `QualityEvent.Created`, `.AssignedToInvestigator`, `.RootCauseRecorded`, `.EscalatedToCAPA`, `.Closed`
  - CAPA Service: `CAPA.Created`, `.InvestigationStarted`, `.ActionAssigned`, `.ActionCompleted`, `.EffectivenessVerified`, `.Closed`
  - Training Service: `Training.Assigned`, `.Started`, `.Completed`, `.Overdue`
  - Equipment Service: `Equipment.Created`, `.CalibrationDue`, `.CalibrationPassed`, `.CalibrationFailed` (OOT), `.Decommissioned`
- [ ] Wire Kafka consumers per service for cross-module flows (see [Section 20.1](#201-cross-module-event-flows))
- [ ] Add dead-letter queue + retry policy

**Acceptance:**
- [ ] Approve a document → see `Document.Approved` event published to Kafka
- [ ] Training service consumer receives event → auto-creates assignments for distribution list members
- [ ] Inspect Kafka with a CLI tool to verify topics receiving messages

### 6.5 Service 5: Scheduler Service (new — fills a gap)

**Current state:** Doesn't exist. Spec calls for reminders at 30/14/7/1 days for periodic review, calibration due, training due, CAPA effectiveness checks.

**Backend tasks:**
- [ ] Build new `scheduler-service` based on APScheduler or Celery beat
- [ ] Endpoints:
  - `POST /schedules` — register a schedule (entity_type, entity_id, trigger_dates[], event_to_emit)
  - `GET /schedules/{entity_type}/{entity_id}` — list schedules for an entity
  - `DELETE /schedules/{id}` — cancel a schedule
- [ ] Cron worker that fires events at scheduled times via Kafka
- [ ] Used by:
  - Document periodic review reminders
  - Equipment calibration reminders
  - Training assignment due-date reminders
  - CAPA action overdue escalation (7/14/30 days)
  - CAPA effectiveness check at 30/60/90 days

**Acceptance:**
- [ ] Create a document with `review_date = today + 30 days` → 1 day before, an in-app notification fires

### 6.6 Service 6: Auth Service hardening (existing stub)

**Backend tasks:**
- [ ] Move from stub to real Keycloak (or finalize the custom auth-service)
- [ ] Implement endpoints if not already:
  - `POST /auth/login` (returns JWT + refresh token)
  - `POST /auth/refresh`
  - `POST /auth/logout` (revoke refresh)
  - `POST /auth/mfa/setup`, `POST /auth/mfa/verify`
  - `POST /auth/re-auth` — re-enter password for 21 CFR Part 11 signing (returns short-lived token)
- [ ] Add `signature_meaning` parameter for re-auth: "Approve", "Reject", "Acknowledge", etc.
- [ ] Wire RBAC enforcement at API gateway level

**Frontend tasks:**
- [ ] `<SignatureDialog />` component used wherever a 21 CFR Part 11 signature is captured:
  - Document Approve / Reject
  - CAPA Close
  - Document Acknowledgment
  - Training Sign-Off
  - Audit Report Sign-Off
- [ ] Modal contains: password re-entry, signature meaning declaration (preset by caller), "I confirm" checkbox

**Acceptance:**
- [ ] Approving a document opens the SignatureDialog modal before the API call
- [ ] Backend rejects approval if re-auth token absent or signature_meaning is missing
- [ ] Audit trail records the signature meaning alongside the hash

---

## 7. Phase 2 — Document Control Completion

**Duration:** 2 weeks
**Goal:** Take Document Control from "basic CRUD" to MasterControl-quality with InfoCard view, file upload, all spec fields visible, periodic review reminders, version creation flow.

### 7.1 Backend tasks

- [ ] **Editor integration schema additions** (per [Section 4.3](#43-required-schema-additions-to-document-table)):
  - Add `authoring_mode` (string, enum: `upload` | `embedded_editor`, default `upload`)
  - Add `content_ast` (JSONB, nullable) — ProseMirror JSON from editor
  - Add `html_snapshot` (text, nullable) — rendered HTML from editor
  - Add `editor_nonce` (string(64), nullable) — most recent editor save nonce
  - Mirror the same columns on `DocumentVersion` for per-version snapshots
- [ ] **Editor integration endpoints** (per [Section 4.4](#44-required-backend-endpoints)):
  - `POST /documents/{id}/content` — save AST + HTML from editor
  - `GET /documents/{id}/content` — fetch AST + HTML for re-editing or viewing
  - `POST /documents/{id}/content/snapshot` — internal endpoint called by `create_new_version` flow
- [ ] Add missing fields to `Document` ORM model + migration:
  - `change_summary` (already in DB?)
  - `retention_period` (months)
  - `iso_clause_mapping` (string, comma-separated clauses)
  - `vault` (enum: `qa_released` | `qa_draft` | `course_release` | `external`)
  - `taxonomy_id` (FK to new `taxonomies` table)
  - `folder_id` (FK to new `folders` table)
  - `lifecycle_name` (e.g. "Quality Lifecycle" — for future configurable lifecycles)
  - `expires_date`
  - `moved_to_phase`
- [ ] New entity: `Taxonomy` (id, tenant_id, name, parent_id for hierarchy)
- [ ] New entity: `Folder` (id, tenant_id, taxonomy_id, name, parent_folder_id)
- [ ] New entity: `ControlledCopy` (id, tenant_id, document_id, copy_holder_user_id, distribution_date, copy_format: digital/paper, status: active/recalled)
- [ ] Endpoints:
  - `GET /taxonomies` — tree
  - `POST /taxonomies` — create
  - `POST /folders` — create folder in taxonomy
  - `GET /documents?taxonomy_id=&folder_id=&vault=&search=` — extended filters
  - `POST /documents/{id}/controlled-copies` — issue controlled copy
  - `GET /documents/{id}/controlled-copies` — list
  - `POST /controlled-copies/{id}/recall` — recall a copy
- [ ] Wire file upload for Mode B (uses Phase 1 file service):
  - `POST /documents/{id}/file` — attach a file (becomes the document content for upload-mode docs)
  - `GET /documents/{id}/file/download`
  - `GET /documents/{id}/file/preview`
- [ ] Wire scheduler (Phase 1) for periodic review reminders at 30/14/7 days
- [ ] Wire Kafka events for all transitions (now emits real events)

### 7.2 Frontend tasks

#### 7.2.0 Create Document page — NEW dedicated route

> **Full spec:** See [Section 4.6 — New page `/qms/documents/create`](#46-new-page--qmsdocumentscreate) for the complete page layout, component code outline, and integration with `editor.manne.work`.

**Summary of what changes:**
- The current modal-based "+ New Document" dialog is **removed** from the list page
- The "+ New Document" button on the Explorer page **navigates to `/qms/documents/create`** instead
- The Create page supports **two authoring modes** (Mode A: embedded editor iframe; Mode B: file upload), selected by a radio button
- The Create page has the three-column layout (left nav / center authoring pane / right Settings sidebar) matching the `knowledge-base-new-article.jpeg` reference
- After saving, the user is redirected to the Document InfoCard view (`/qms/documents/{id}`)

**Reference image:** `knowledge-base-new-article.jpeg` (Settings sidebar pattern), plus `documents-infocard-view.jpeg` for the post-save destination.

**Cross-references:**
- Section 4 — full editor integration guide
- Section 7.1 above — backend schema additions (`authoring_mode`, `content_ast`, `html_snapshot`)
- Section 6.3 (Phase 1) — File Service required for Mode B

#### 7.2.1 Documents Explorer page — REPLACE current basic list

**Target UI:** Match MasterControl Explorer.

**Layout:**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Documents > Explorer                            [Search...] [New Document]    │
├──────────────────────────────────────────────────────────────────────────────┤
│ [🗂️ List] [⊞ Grid]  [Sort ▼] [Filter ▼]  Home / Documents by Department    │
├─────────────────┬────────────────────────────────────────────────────────────┤
│ Favorites    🗑️ │ NAME                          TYPE          FAV   MORE     │
│ 📁 Contracts    │ 📁 Microbiology               Taxonomy       ☆    ⚙️       │
│ 📄 POL-0004     │ 📁 Chemistry                  Taxonomy       ☆    ⚙️       │
│ 📄 POL-0005     │ 📁 Calibration Lab            Taxonomy       ☆    ⚙️       │
│                 │ 📁 Quality Procedures         Folder         ☆    ⚙️       │
│ Taxonomies      │ 📄 SOP-MICRO-0042             Document       ⭐    ⚙️       │
│ ▸ By Department │ 📄 SOP-MICRO-0041             Document       ☆    ⚙️       │
│ ▸ By Product    │                                                              │
│ ▸ By Client     │ ─── Filter Sidebar ──────────────────                       │
│ ▸ By Process    │ Status:                                                     │
│                 │  ☐ Draft  ☑ Under Review  ☑ Effective                       │
│ Vaults          │  ☐ Superseded  ☐ Obsolete                                  │
│ ▸ QA-Released   │ Type:                                                       │
│ ▸ QA-Draft      │  ☑ SOP  ☑ WI  ☐ Method  ☐ Policy                          │
│ ▸ External      │ Vault: ☑ QA-Released  ☐ QA-Draft                           │
│                 │ Owner: [select user]                                        │
│                 │ Review due: [date range]                                    │
└─────────────────┴────────────────────────────────────────────────────────────┘
```

**Components:**
- `<DocumentsExplorer />` — main page
- `<TaxonomyTree />` — left-side tree
- `<DocumentsList />` (List view) or `<DocumentsGrid />` (Grid view) — toggleable
- `<FilterSidebar />` — right-side filters
- `<Breadcrumb />` — top-of-list
- Sort dropdown: Name / Type / Status / Effective Date / Review Due

#### 7.2.2 Document InfoCard view — REPLACE current basic detail

**Target UI:** Match MasterControl InfoCard exactly.

**Layout:**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Documents > View Document InfoCard                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ SOP-MICRO-0042                                          Status: Effective     │
│ Labeling Procedure for Finished Goods                   [Initiate Revision]   │
│                                                          [Acknowledge]        │
├─────────────────────────────────────────┬────────────────────────────────────┤
│ Version Information                      │ ▎ Information (current)            │
│   Document Number:  SOP-MICRO-0042       │   Training                         │
│   Version:          2.0                  │   Controlled Copies                │
│   Revision:         Rev 04               │   Distribution List                │
│   Title:            Labeling Procedure   │   Attachments & Links              │
│   Notes:            SOP for label attach │   Custom Fields                    │
│                     procedure            │   History                          │
│   Lifecycle:        Quality Lifecycle    │   Status                           │
│   Vault:            QA-Released          │   Versions                         │
│   Document Type:    SOP                  │                                    │
│   Subtype:          Quality              │                                    │
│   ISO Clauses:      8.3, 8.4             │                                    │
│   Tags:             [labeling] [QA]      │                                    │
│   Regulatory:       FDA 21 CFR Part 11   │                                    │
│                                          │                                    │
│ Main File                                │                                    │
│   📄 Labeling.docx  27.48 KB             │                                    │
│   [Download] [View] [Replace]            │                                    │
│   ☑ Include signature manifest on        │                                    │
│     gateway export                       │                                    │
│                                          │                                    │
│ Date Information                         │                                    │
│   Created:        07 Nov 2025            │                                    │
│   Released:       26 Mar 2026            │                                    │
│   Effective:      26 Mar 2026            │                                    │
│   Expires:        —                      │                                    │
│   Moved to Phase: 26 Mar 2026            │                                    │
│   Next Review:    26 Mar 2027            │                                    │
│                                          │                                    │
│ Owner & Approvers                        │                                    │
│   Owner:          Rajesh Patel           │                                    │
│   Approver(s):    Dr. Priya Sharma       │                                    │
│   Retention:      7 years                │                                    │
└──────────────────────────────────────────┴────────────────────────────────────┘
```

**Right-side tabs (each is a separate component):**

| Tab | Content |
|-----|---------|
| **Information** | The left column above (default) |
| **Training** | List of courses linked to this document; assignments compliance % |
| **Controlled Copies** | Table: Copy Holder, Distribution Date, Format, Status, [Recall] |
| **Distribution List** | Existing UI; show acknowledgment status per member (Acknowledged ✅ / Pending ⏳ / Overdue ⚠️) |
| **Attachments & Links** | Other files + linked records (CAPAs, audits) |
| **Custom Fields** | Extensible key-value pairs (Phase 13) |
| **History** | `<EventTimeline />` from audit-trail-service |
| **Status** | Current state machine position visualized |
| **Versions** | Existing UI; add "Create New Version" button (Phase 0 D-2 backend) |

#### 7.2.3 New dialogs

| Dialog | Trigger | Fields | API |
|--------|---------|--------|-----|
| **Create New Document** (extend existing) | "New Document" button | Add: vault, taxonomy_id, folder_id, iso_clause_mapping, retention_period, tags, file upload | `POST /documents` + `POST /documents/{id}/file` |
| **Create New Version** | "Initiate Revision" button on InfoCard | change_type (major/minor), change_summary, new file upload | `POST /documents/{id}/versions` |
| **Acknowledge Document** | "Acknowledge" button (visible if user is on distribution list and hasn't acknowledged) | Signature meaning auto-set to "I have read and understood"; uses `<SignatureDialog />` | `POST /documents/{id}/acknowledge` |
| **Issue Controlled Copy** | "Issue Copy" button on Controlled Copies tab (QM only) | copy_holder (user picker), format (digital/paper) | `POST /documents/{id}/controlled-copies` |
| **Approve Document** (extend existing) | Already exists; add signature meaning declaration via `<SignatureDialog />` | All fields stay | `POST /documents/{id}/approve` |

### 7.3 Field bindings — Document detail page

| API Field | UI Element | Where shown |
|-----------|-----------|-------------|
| `id` | URL only | — |
| `doc_number` | Header subtitle + Version Info section | Top |
| `title` | Header | Top |
| `doc_type` | Version Info section ✅ now bound | **Currently NOT bound — fix** |
| `status` | Status badge (top right) | Top |
| `current_version` | Version Info section | Left |
| `description` | Version Info > Notes | Left |
| `department` | Owner & Approvers section ✅ now bound | **Currently NOT bound — fix** |
| `owner_id` | Owner & Approvers section (display owner name) | Left |
| `approver_id` | Owner & Approvers section | Left |
| `effective_date` | Date Information | Left |
| `review_date` | Date Information > Next Review | Left |
| `expiry_date` | Date Information > Expires ✅ now bound | **Currently NOT bound — fix** |
| `file_id` | Main File section ✅ now bound | **Currently NOT bound — fix** |
| `tags` | Version Info > Tags chips ✅ now bound | **Currently NOT bound — fix** |
| `regulatory_frameworks` | Version Info > Regulatory chips ✅ now bound | **Currently NOT bound — fix** |
| `is_controlled` | Status badge "Controlled" indicator ✅ now bound | **Currently NOT bound — fix** |
| `last_rejection_reason` | Amber alert banner if not null | Top (existing) |
| `created_at` | Date Information > Created | Left |
| `updated_at` | History tab | — |
| `vault` | Version Info > Vault | Left (NEW field) |
| `taxonomy_id` | Breadcrumb | Top (NEW field) |
| `iso_clause_mapping` | Version Info > ISO Clauses | Left (NEW field) |
| `retention_period` | Owner & Approvers > Retention | Left (NEW field) |
| `lifecycle_name` | Version Info > Lifecycle | Left (NEW field) |
| `moved_to_phase` | Date Information > Moved to Phase | Left (NEW field) |
| `authoring_mode` | Main File section label ("Authored in editor" / "Uploaded file") | Left (NEW field — editor integration) |
| `content_ast` | (Not displayed directly — used to re-open editor on Edit) | — (NEW field — editor integration) |
| `html_snapshot` | Rendered inline in Information tab body OR via `<TemplateViewer>` | Body (NEW field — editor integration) |

### 7.4 Acceptance criteria

- [ ] `/qms/documents/create` page exists and matches the `knowledge-base-new-article.jpeg` reference layout (left nav + breadcrumb + center authoring pane + right Settings sidebar)
- [ ] Authoring Mode radio (Author in editor / Upload file) toggles between iframe and dropzone
- [ ] Mode A: editor.manne.work loads inside iframe via `temp-builder`'s `TemplateEditor` component
- [ ] Mode A: clicking "Save as Draft" creates the document AND persists `content_ast` + `html_snapshot` via `POST /documents/{id}/content`
- [ ] Mode B: file dropzone accepts up to 100 MB (PDF/DOCX/XLSX/PNG/JPG) and uploads via file-service before creating the document
- [ ] Documents Explorer page renders with taxonomy tree + breadcrumb + filter sidebar
- [ ] Switching to grid view works
- [ ] Document InfoCard matches MasterControl reference visually
- [ ] InfoCard renders content from `html_snapshot` (Mode A docs) or from uploaded file preview (Mode B docs) based on `authoring_mode`
- [ ] Editing a draft document re-opens the editor with prior `content_ast` loaded
- [ ] All 25 API fields are bound to UI elements (no hidden data)
- [ ] File upload works end-to-end (upload → virus scan → preview → download)
- [ ] Create new version flow works (status: approved → draft, version: 1.0 → 2.0); previous version's `content_ast` and `html_snapshot` are snapshotted into the prior `DocumentVersion` row
- [ ] Acknowledgment workflow works with `<SignatureDialog />`
- [ ] Controlled Copies tab functional
- [ ] History tab shows audit trail events
- [ ] Periodic review reminder fires 30 days before `review_date`
- [ ] All transitions emit Kafka events

---

## 8. Phase 3 — Quality Event & CAPA Polish

**Duration:** 2 weeks
**Goal:** Take QE & CAPA from "basic forms" to MasterControl FBS-style tabbed forms with full field coverage, root cause UI, escalation flows.

### 8.1 Backend tasks (small — mostly frontend polish)

- [ ] Quality Event service: add missing endpoints:
  - `POST /quality-events/{id}/root-cause` — record RCA using one of 5 tools (5-Why / Fishbone / Fault Tree / Pareto / Manual)
  - `POST /quality-events/{id}/immediate-action` — record immediate action separately from description
- [ ] CAPA service: ensure all listed fields are returned in detail GET
- [ ] Wire Kafka event `QualityEvent.EscalatedToCAPA` (currently just sets `capa_id` field)

### 8.2 Frontend tasks — Quality Event

#### 8.2.1 List page improvements

- [ ] Add `<FilterSidebar />` with: Severity, Event Type, Department, Date Range, Status
- [ ] Add column sort indicators
- [ ] Add "Report Event" prominent button matching MasterControl Pending Tasks layout
- [ ] My Priority and My Tag columns (user-personal tagging) — defer to Phase 3.5 if scope tight

#### 8.2.2 Detail page — FBS-style tabbed form

**Target UI:** Match MasterControl Customer Complaint FBS pattern. Tabs across the top:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ MasterControl Process > Quality Event: QE-2026-0037                          │
├──────────────────────────────────────────────────────────────────────────────┤
│ Form #: QE-2026-0037  |  Current Step: Investigation  |  Step Due: 22 May    │
├──────────────────────────────────────────────────────────────────────────────┤
│ [About] [Event Information ✏️] [Investigation] [Root Cause] [Action Items]   │
│ [Communications Log] [Resolution]                                            │
├──────────────────────────────────────────────────────────────────────────────┤
│ (Active tab content here — see field bindings below)                         │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Tab 1: About**
- Form Number (auto), Current Step (auto), Step Due Date, Status, Created By, Created At, Last Updated

**Tab 2: Event Information**
- Title*, Description*, Event Type* (deviation/non-conformance/nc-work/oos/oot), Severity* (critical/major/minor/observation), Priority, Department*, Location, Detected At*, Detected By, Linked Equipment (picker), Linked Document (picker), Linked Personnel (user picker), Tags, Attachments (`<FileUploadDropzone />`)

**Tab 3: Investigation**
- Investigator (user picker), Investigation Start Date, Investigation Notes (rich text), Assigned To
- Now binds: `assigned_to`, `due_date`

**Tab 4: Root Cause** (NEW)
- RCA Tool used: dropdown (5-Why / Fishbone / Fault Tree / Pareto / Manual)
- If 5-Why: 5 text input rows (Why 1: ... → Why 5: ...)
- If Fishbone: 6 input areas (Machine / Method / Material / Man / Measurement / Environment)
- If Fault Tree / Pareto: embedded interactive editor (Phase 13)
- Root Cause Summary (textarea)
- Evidence (file upload)
- Now binds: `root_cause`, `immediate_action`

**Tab 5: Action Items**
- List of corrective/preventive actions; each row: Description, Owner, Due Date, Status
- "Add Action" button → if escalating to CAPA, links to CAPA Action records
- Now binds: `capa_required`, `capa_id` (auto-link button)

**Tab 6: Communications Log**
- Append-only log of notifications sent, client contacts, internal emails
- Used heavily for client notification flag

**Tab 7: Resolution**
- Resolution Summary, Closure Date, Verified By, Lessons Learned
- "Close Event" button → opens `<SignatureDialog />` with meaning "I confirm event resolution"

#### 8.2.3 Currently unbound Quality Event fields — now bound

| Field | Where to bind |
|-------|--------------|
| `root_cause` | Root Cause tab |
| `immediate_action` | Event Information tab → new field |
| `priority` | Event Information tab |
| `capa_required` | Action Items tab |
| `due_date` | About tab → Step Due Date |
| `tags` | Event Information tab |
| `attachments` | Event Information tab |

### 8.3 Frontend tasks — CAPA

#### 8.3.1 List page

- [ ] Add `<FilterSidebar />`: Type, Severity, Status, Department, Owner, Source Type, Date Range
- [ ] Add columns for Source Type and Source Ref (so user sees if it came from QE, Audit, Complaint, PT)

#### 8.3.2 Detail page — FBS-style with 6-step lifecycle bar

**Layout:**

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ CAPA-2026-0018: Improved pH meter calibration schedule                       │
├──────────────────────────────────────────────────────────────────────────────┤
│ ●─────●─────●─────○─────○─────○                                              │
│ Open  Inv.  RCA   Impl. Eff.  Closed                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ [About] [Source] [Risk Assessment] [Investigation] [Action Plan]             │
│ [Implementation] [Effectiveness] [Closure]                                   │
├──────────────────────────────────────────────────────────────────────────────┤
│ (Active tab content here)                                                    │
└──────────────────────────────────────────────────────────────────────────────┘
```

**Tab 1: About**
- CAPA Number, Title, Type (corrective/preventive/both), Status, Owner, Department, Created By, Created At, Target Close Date, Actual Close Date

**Tab 2: Source**
- Source Type (quality_event / audit_finding / complaint / pt_result / management_review / standalone)
- Source ID + clickable link to source record
- "View Source Event" button

**Tab 3: Risk Assessment**
- Risk Severity (1-5 slider), Risk Occurrence (1-5), Risk Detectability (1-5)
- Auto-calculated RPN display: Severity × Occurrence × Detectability = N
- Risk Statement / Rationale (textarea)

**Tab 4: Investigation**
- Investigation Notes, Root Cause, Root Cause Method (RCA tool used), Evidence files

**Tab 5: Action Plan**
- List of CAPA Actions: existing UI; add columns for Expected Outcome and Impact Assessment
- "Approve Plan" button (QM only) → `<SignatureDialog />`

**Tab 6: Implementation**
- Per-action: Owner sign-off, Completion Date, Evidence file upload
- Document/training auto-triggers (read-only display of any linked changes)

**Tab 7: Effectiveness**
- 3 scheduled checks: 30/60/90 days
- Per check: Date, Performed By, Result (Effective / Not Effective), Notes
- "Verify Effectiveness" button at each scheduled check

**Tab 8: Closure**
- Closure Summary, Final Approval (QM signature), Closed Date
- "Close CAPA" button → `<SignatureDialog />` with meaning "I close this CAPA as effective"

#### 8.3.3 Currently unbound CAPA fields — now bound

| Field | Where to bind |
|-------|--------------|
| `source_type` / `source_id` | Source tab |
| `target_close_date` | About tab |
| `actual_close_date` | About tab |
| `effectiveness_check_date` | Effectiveness tab |
| `department` | About tab |
| `tags`, `attachments` | About tab |

### 8.4 Acceptance criteria

- [ ] Quality Event detail page renders 7-tab FBS layout
- [ ] CAPA detail page renders 8-tab FBS layout with 6-step lifecycle bar
- [ ] All previously-unbound fields now visible and editable
- [ ] Root Cause tab supports at least 5-Why and Fishbone tools
- [ ] Escalate QE → CAPA flow creates linked CAPA with source pre-filled
- [ ] All operations emit Kafka events

---

## 9. Phase 4 — Training Excellence (Job Codes + Matrix)

**Duration:** 3 weeks
**Goal:** Make Training the strongest module visually — Job Codes, the Job Code Status Matrix (the single biggest compliance UX gap), and the 5-step training task UX.

### 9.1 Backend tasks

#### 9.1.1 New entities

- [ ] `JobCode` (id, tenant_id, code, name, description, department, is_active, created_at, updated_at)
- [ ] `JobCodeCourse` (id, job_code_id, course_id, is_mandatory, prerequisite_course_id)
- [ ] `JobCodeAssignment` (id, job_code_id, user_id, assigned_at, assigned_by, status)
- [ ] `Trainer` (id, tenant_id, user_id, qualifications[], is_active) — distinct from User
- [ ] `Exam` (id, tenant_id, course_id, title, passing_score)
- [ ] `ExamQuestion` (id, exam_id, question_text, question_type, options[], correct_answer)
- [ ] `ExamAttempt` (id, exam_id, user_id, started_at, completed_at, score, passed)

#### 9.1.2 Endpoints

- [ ] `GET/POST /job-codes`
- [ ] `GET /job-codes/{id}/courses` — list courses for job code
- [ ] `POST /job-codes/{id}/courses` — link course to job code
- [ ] `POST /job-codes/{id}/users` — assign user to job code (auto-creates training assignments for all courses)
- [ ] `GET /job-codes/{id}/status-matrix` — returns matrix data (users × courses × status)
- [ ] `GET /trainers`, `POST /trainers`
- [ ] `GET /exams/{id}`, `POST /exams`, `POST /exams/{id}/questions`
- [ ] `POST /exams/{id}/attempts/start`, `POST /exams/{id}/attempts/{attemptId}/submit`

#### 9.1.3 Kafka consumer

- [ ] Listen for `Document.Effective` events → look up linked Course by `document_id` → for every user assigned to a JobCode that includes this Course → create training assignment
- [ ] Listen for `User.RoleChanged` events → re-evaluate job code assignments

### 9.2 Frontend tasks

#### 9.2.1 Training Dashboard

**Target UI:** Match MasterControl Training dashboard tiles.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Training                                       [Search...] [Import]      │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐          │
│ │ Training   │ │ Job Code   │ │ Recent     │ │ Import       │          │
│ │ Folders    │ │ Status     │ │ Courses    │ │              │          │
│ │            │ │            │ │            │ │   ⤴️         │          │
│ │ [Open]     │ │ [Open]     │ │  • SOP-... │ │ [Import]    │          │
│ │            │ │            │ │  • SOP-... │ │              │          │
│ └────────────┘ └────────────┘ └────────────┘ └──────────────┘          │
│ ┌────────────┐ ┌────────────┐ ┌──────────────────────────┐             │
│ │ Courses    │ │ Job Codes  │ │ Settings                  │             │
│ │ • New      │ │ • New      │ │   ⚙️                     │             │
│ │ • Search   │ │ • Search   │ │ [Open]                   │             │
│ │ • View     │ │ • View     │ │                          │             │
│ └────────────┘ └────────────┘ └──────────────────────────┘             │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐            │
│ │ Reports    │ │ Exams      │ │ Trainees   │ │ Classes    │            │
│ │   📊       │ │ • New      │ │ • Search   │ │   📚      │            │
│ │ [Open]     │ │ • Search   │ │ • View     │ │ [Open]    │            │
│ │            │ │ • View     │ │            │ │            │            │
│ └────────────┘ └────────────┘ └────────────┘ └────────────┘            │
│ ┌────────────┐                                                          │
│ │ Trainers   │                                                          │
│ │   👤       │                                                          │
│ │ • New      │                                                          │
│ │ • Search   │                                                          │
│ │ • View     │                                                          │
│ └────────────┘                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 9.2.2 Job Code Status Matrix — THE KEY UI

**Target UI:** Match MasterControl Job Code Status exactly.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Training > Job Code Status                                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Job Code: Microbiology Analyst                                  [Export to Excel]│
│                                                                                  │
│ Legend: ✅ Complete  ⏳ In Progress  ⚠️ Overdue  🔒 Waiting on Prereq  ⏸️ Pending│
│                                                                                  │
│ ┌────────────────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬──────┐│
│ │ Employee       │GMP  │Lbl  │Ster │Media│IL   │Lbl  │MD   │Open │Pack │ %    ││
│ │                │     │     │     │     │Smp  │Fin  │Tpl  │Prod │     │      ││
│ ├────────────────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼─────┼──────┤│
│ │ Carpenter, Rob │ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Christensen S. │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Gattardi, Ruben│ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Hamilton, Ang. │ ✅  │ ⏳  │ ✅  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Harper, Jeff   │ ✅  │ ⚠️  │ ✅  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Hefer, Dan     │ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Holland, Ken   │ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Lewis, Kai     │ ✅  │ ✅  │ ✅  │ ⚠️  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 45%  ││
│ │ Liston, Sean   │ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Little, Doug   │ ✅  │ ⏸️  │ ⏸️  │ ⏸️  │ ⏸️  │ ⏸️  │ ⏸️  │ ⏸️  │ ⏸️  │  9%  ││
│ │ Smith, Matt    │ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ │ Toms, David    │ ⚠️  │ ⚠️  │ ⚠️  │ ⚠️  │ ⚠️  │ ⚠️  │ ⚠️  │ ⚠️  │ ⚠️  │  0%  ││
│ │ Wolk, Dallas   │ ✅  │ ✅  │ ✅  │ ⏳  │ ⏳  │ ✅  │ ✅  │ ✅  │ ✅  │ 55%  ││
│ └────────────────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴──────┘│
│ Average Percentage Completed: 46%                                                │
│ 0 of 13 have completed training                                                  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Component:** `<JobCodeMatrix />`
- Uses `<MatrixGrid />` shared component
- Sticky left column (employee names) and sticky top row (course names with vertical text)
- Each cell shows status icon + tooltip on hover with full course title + due date + completion date
- Cell click → opens that user's assignment detail
- Filter dropdown at top: select Job Code (changes which matrix is shown)
- Export to Excel button → CSV download
- Color-code the percentage column: green > 90, amber 70-90, red < 70

#### 9.2.3 5-Step Training Task UX

**Target UI:** Match MasterControl Training Task workflow.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Training > Training Task: SOP-MICRO-0042                                 │
├─────────────────────────────────────────────────────────────────────────┤
│  📖 ────────► 📚 ────────► ✏️ ────────► 👁️ ────────► ✅                │
│ Introduction  Materials    Exam       Overview    Sign Off              │
│  (active)                                                                │
├─────────────────────────────────────────────────────────────────────────┤
│ Step 1: Introduction                                                     │
│                                                                          │
│   Source of Training: New document added to course                       │
│   Training For Course: Labeling Finished Goods                           │
│   Description: Labeling                                                  │
│   Initial Training Instructions:                                         │
│     1. Read attached document                                            │
│     2. Take exam                                                         │
│     3. Sign-off on task                                                  │
│   Location: Workstation                                                  │
│   Trainer: Dan Hefer (DAN)                                               │
│   Competency: None                                                       │
│                                                                          │
│                                                  [Next: Materials →]    │
└─────────────────────────────────────────────────────────────────────────┘
```

**Component:** `<TrainingTaskWizard />` — multi-step form using shadcn-stepper or custom
- Step bar at top with icons (color: active=blue, complete=green, pending=slate)
- Step 1 (Introduction): course context, trainer info, instructions
- Step 2 (Materials): embedded `<FilePreview />` showing the linked document; "I have read" checkbox; time-on-page tracker
- Step 3 (Exam): if course requires_certification, render `<ExamRunner />` with questions; auto-grade on submit
- Step 4 (Overview): summary of progress, opportunity to go back
- Step 5 (Sign Off): `<SignatureDialog />` with meaning "I have read, understood, and will follow this SOP"

#### 9.2.4 New routes

| Route | Page |
|-------|------|
| `/qms/training/job-codes` | Job Codes list (CRUD) |
| `/qms/training/job-codes/[id]` | Job Code detail (linked courses, assigned users) |
| `/qms/training/job-codes/[id]/status` | Job Code Status Matrix |
| `/qms/training/courses/[id]` | Course detail (currently missing) |
| `/qms/training/trainers` | Trainers list |
| `/qms/training/exams` | Exams list |
| `/qms/training/exams/[id]` | Exam editor (question bank) |
| `/qms/training/my-training/[id]` | Training task wizard (5-step) |

### 9.3 Field bindings — Training

| API field | UI element | Where |
|-----------|-----------|-------|
| `course.document_id` | Course detail > Linked Document link ✅ | NEW binding |
| `course.recurrence_days` | Course detail > Recurrence ✅ | NEW binding |
| `assignment.course_title` | My Training list > Course column ✅ | NEW binding |
| Job Code | Matrix selector | NEW |
| Job Code → Courses | Matrix columns | NEW |
| Job Code → Users | Matrix rows | NEW |

### 9.4 Acceptance criteria

- [ ] Training dashboard with 11 tiles
- [ ] Job Code CRUD works
- [ ] Job Code Status Matrix renders with sticky headers, status icons, percentage column
- [ ] Export to Excel works
- [ ] 5-step Training Task wizard works end-to-end
- [ ] Exam administration works (start → questions → submit → auto-grade)
- [ ] Auto-assignment on document approval works (verified via Kafka event)

---

## 10. Phase 5 — Equipment Completion

**Duration:** 2 weeks
**Goal:** Add the missing pieces — OOT auto-QE creation, calibration certificate generation, usage logbook, full field display.

### 10.1 Backend tasks

- [ ] Add OOT auto-event flow: on calibration with `passed=false`, auto-emit Kafka event `Equipment.CalibrationFailed` → Quality Event consumer auto-creates `QualityEvent(event_type=oot, severity=major, equipment_id=…)`
- [ ] New entity: `EquipmentUsageLog` (id, equipment_id, user_id, timestamp, action: in-use/idle/maintenance, notes)
- [ ] Endpoints:
  - `POST /equipment/{id}/usage-log` — log a usage event
  - `GET /equipment/{id}/usage-log?from=&to=` — paginated usage history
  - `POST /equipment/{id}/calibration-certificate` — generate PDF certificate
  - `GET /equipment/{id}/calibration-certificate/{certId}/download` — fetch
- [ ] Standards traceability: new `ReferenceStandard` entity (id, name, manufacturer, lot, calibrated_against, certificate_file_id, expiry)
- [ ] Block calibration if any used reference standard is expired

### 10.2 Frontend tasks

#### 10.2.1 List page

- [ ] Add `<FilterSidebar />` with: Status, Department, Equipment Type, Calibration Status (Up-to-date / Due / Overdue), Location
- [ ] Add columns for Manufacturer + Last Calibration

#### 10.2.2 Detail page — REPLACE with InfoCard layout

Use the `<InfoCard />` shared component. Sections:

**Left column:**
- **Equipment Information** — Asset Tag, Name, Description, Type, Manufacturer, Model, Serial Number
- **Location & Assignment** — Location, Department, Assigned To, Tags
- **Calibration Schedule** — Requires Calibration ✓, Frequency (days), Last Cal Date, Next Cal Date, Status
- **Preventive Maintenance** — Requires PM ✓, Frequency (days), Last PM Date, Next PM Date
- **Procurement** — Purchase Date, Warranty Expiry, Cost (optional)

**Right-side tabs:**

| Tab | Content |
|-----|---------|
| **Information** | The left column (default) |
| **Calibration History** | List of `CalibrationRecord[]`: Date, Technician, Pass/Fail, Standards Used, As-Found/As-Left, Uncertainty, [Download Certificate] |
| **Usage Logbook** | Append-only log of usage events; filterable by date and user |
| **PM History** | Past preventive maintenance records (Phase 13 if time-tight) |
| **Attachments** | Manuals, certificates, etc. |
| **History** | Audit trail |

#### 10.2.3 New dialogs

| Dialog | Trigger | Fields | Notes |
|--------|---------|--------|-------|
| **Add Equipment** | "+ New Equipment" button on list page (button exists, no dialog now — fix) | Full equipment form | Wire to `POST /equipment` |
| **Record Calibration** (extend) | "Record calibration" button | Add: Reference Standards picker (multi-select), Environmental Conditions, As-Found Readings table, As-Left Readings table, Measurement Uncertainty | Block if any standard expired |
| **Log Usage** | "Log Usage" button | Action (in-use/idle/maintenance), Notes | New |
| **Generate Certificate** | "Generate Certificate" button (Calibration History tab, per record) | Customer name, custom notes | PDF download |

### 10.3 Field bindings — Equipment detail page

| Field | Currently bound? | Where to bind now |
|-------|------------------|-------------------|
| `manufacturer` | List only | **Equipment Information** section |
| `model` | NOT bound | **Equipment Information** section |
| `serial_number` | NOT bound | **Equipment Information** section |
| `requires_pm` | NOT bound | **Preventive Maintenance** section |
| `pm_frequency_days` | NOT bound | **Preventive Maintenance** section |
| `last_pm_date`, `next_pm_date` | NOT bound | **Preventive Maintenance** section |
| `purchase_date`, `warranty_expiry` | NOT bound | **Procurement** section |
| Calibration history | NOT bound | **Calibration History** tab |

### 10.4 Acceptance criteria

- [ ] Add Equipment dialog wired and functional
- [ ] All 7 previously-unbound equipment fields now display
- [ ] Calibration History tab shows past calibrations
- [ ] Failed calibration triggers Quality Event auto-creation (verified)
- [ ] Generate Certificate produces downloadable PDF
- [ ] Usage logbook functional
- [ ] Reference Standard expiry check blocks calibration

---

## 11. Phase 6 — Audit Management

**Duration:** 4 weeks
**Goal:** Build the Audit Management module from scratch — the most complex new module. Drag-and-drop calendar, 4-tab Audit Workspace, finding-to-CAPA auto flow.

### 11.1 Backend tasks

#### 11.1.1 Entities

- [ ] `Audit` (id, tenant_id, audit_number, audit_type, scope, criteria, lead_auditor_id, audit_team[], auditee_id, scheduled_start, scheduled_end, performed_start, performed_end, score, status, checklist_id, summary, scope_text, report_file_id, created_at, updated_at)
- [ ] `AuditChecklist` (id, tenant_id, name, criteria, items[])
- [ ] `AuditChecklistItem` (id, checklist_id, iso_clause, question, expected_evidence, order)
- [ ] `AuditFinding` (id, tenant_id, audit_id, finding_number, classification (major_nc/minor_nc/observation/ofi), description, evidence_file_ids[], iso_clause, capa_id, auditee_response, response_due_date, created_at)
- [ ] `AuditorQualification` (id, tenant_id, user_id, audit_types[], iso_standards[], qualified_until)
- [ ] `AuditPlan` (id, tenant_id, year, audits[], approved_by, approved_at) — annual plan

#### 11.1.2 Endpoints

- [ ] CRUD: `GET/POST/PATCH /audits`
- [ ] `GET /audits/calendar?from=&to=` — calendar data
- [ ] `POST /audits/{id}/start` — performed_start
- [ ] `POST /audits/{id}/finalize-report` — generates PDF report
- [ ] `POST /audits/{id}/findings` — create finding (auto-creates CAPA if major/minor NC)
- [ ] `POST /findings/{id}/auditee-response`
- [ ] `GET /checklists` — list / `POST /checklists` — create
- [ ] `GET /auditor-qualifications/{userId}`
- [ ] `POST /audit-plans` — submit annual plan for approval

#### 11.1.3 Kafka consumers

- [ ] Listen for `Audit.FindingCreated` (major/minor NC) → auto-emit `CAPA.Create` → CAPA service consumes and creates CAPA with source_type=audit_finding

### 11.2 Frontend tasks

#### 11.2.1 Audit Dashboard

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Audit                                              [Search...] [+ New]   │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐          │
│ │ My Tasks   │ │ Calendar   │ │ Annual Plan│ │ Audit Folders│          │
│ │ (13)       │ │   📅       │ │ 2026       │ │              │          │
│ │ [Open]     │ │ [Open]     │ │ [Open]     │ │ [Open]      │          │
│ └────────────┘ └────────────┘ └────────────┘ └──────────────┘          │
│ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌──────────────┐          │
│ │ Auditors   │ │ Checklists │ │ Findings   │ │ Reports      │          │
│ │   👤      │ │            │ │ Open: 12   │ │              │          │
│ │ [Open]     │ │ [Open]     │ │ [Open]     │ │ [Open]      │          │
│ └────────────┘ └────────────┘ └────────────┘ └──────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 11.2.2 Audit Calendar — drag-and-drop

**Component:** `<DragDropCalendar />` using `@fullcalendar/react`

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ Audit Calendar              [Today] [< >]   March 2026          [Month] [Week] │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Group by: [Status ▼]    Filter: [All Auditors ▼] [All Types ▼]                  │
├──────────┬──────────┬──────────┬──────────┬──────────┬──────────┬──────────────┤
│ Sun      │ Mon      │ Tue      │ Wed      │ Thu      │ Fri      │ Sat          │
│   1      │   2      │   3      │   4      │   5      │   6      │   7          │
│          │          │          │          │          │ 🟦 AUD-11│              │
│   8      │   9      │  10      │  11      │  12      │  13      │  14          │
│          │          │          │          │          │🟪 Micro  │🟪 Micro       │
│          │          │          │          │          │          │              │
│  15      │  16      │  17      │  18      │  19      │  20      │  21          │
│          │🟦 Design │          │          │          │          │              │
│  22      │  23      │  24      │  25      │  26      │  27      │  28          │
│          │          │          │          │          │          │              │
│  29      │  30      │  31      │          │          │          │              │
│          │🟧 Person │          │          │          │          │              │
└──────────┴──────────┴──────────┴──────────┴──────────┴──────────┴──────────────┘
Legend: 🟦 Internal  🟪 External  🟧 Supplier
```

Features:
- Drag event to reschedule → `PATCH /audits/{id}` with new dates
- Click event → opens Audit Workspace
- Group by dropdown: Status / Auditor / Audit Type
- Color by group selection
- Month/Week toggle

#### 11.2.3 Audit Workspace — 4 tabs (matching MasterControl)

```
┌─────────────────────────────────────────────────────────────────────────┐
│ MasterControl Audit > Audit Workspace                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ AUD-2026-0011 - For Cause Audit                                          │
│                                                                          │
│ [Information] [Documentation] [Observations] [Checklist]                 │
└─────────────────────────────────────────────────────────────────────────┘
```

**Tab 1: Information**
- Audit Entity Type (dropdown: Supplier / Internal Section / Process / Product / Other)
- Audit Entity (cascading dropdown — if type=Supplier, list suppliers; else list internal sections)
- Audit Type (Internal / External / FDA / ISO / Supplier / Regulatory)
- Scheduled Start/End (datetime)
- Performed Start/End (datetime, filled at audit time)
- Score (auto-calculated from checklist completion)
- Lead Auditor (user picker filtered to qualified auditors)
- Auditors (multi-select picker with Available/Selected two-column layout)
- Summary (rich text)
- Scope (rich text)

**Tab 2: Documentation**
- Linked documents reviewed during audit (multi-link)
- Evidence files uploaded
- Audit Plan attachment

**Tab 3: Observations** (the findings list)
- Table: Finding #, Classification (badge), Description, ISO Clause, Linked CAPA
- "+ Add Finding" button → dialog with: Classification (radio), Description (textarea), Evidence (file upload), ISO Clause (autocomplete)
- For Major NC / Minor NC: auto-creates draft CAPA with finding pre-linked, shows confirmation banner

**Tab 4: Checklist**
- Render the linked `AuditChecklist`'s items
- Per item: question, expected evidence, response (Compliant / Non-Compliant / N/A), notes, evidence file upload
- Auto-update audit score as items are completed

#### 11.2.4 Auditor picker (two-column)

**Target UI:** Match MasterControl pattern.

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Add/Remove Auditors                                                      │
├─────────────────────────────────────────────────────────────────────────┤
│ Available (Qualified)            Qualified Auditors (Selected)          │
│ ┌─────────────────────────┐    ┌─────────────────────────┐             │
│ │ • Cesar Geronimo (CESAR)│    │ • Julie Cook (JULIE)    │             │
│ │ • David Dills (DAVID)   │  → │                          │             │
│ │ • George Foster (GEORGE)│  ← │                          │             │
│ │                          │    │                          │             │
│ └─────────────────────────┘    └─────────────────────────┘             │
│                                                                          │
│                                              [Cancel] [Save]            │
└─────────────────────────────────────────────────────────────────────────┘
```

#### 11.2.5 Audit Findings detail page

**Layout:**

- Header: Finding #, Classification badge, Linked Audit, Linked CAPA
- Sections: Description, Evidence Files, ISO Clause, Auditee Response (editable by auditee role), Response Due Date

#### 11.2.6 Routes

| Route | Page |
|-------|------|
| `/qms/audit` | Audit dashboard |
| `/qms/audit/calendar` | Drag-and-drop calendar |
| `/qms/audit/list` | Audit list (table) |
| `/qms/audit/[id]` | Audit Workspace (4 tabs) |
| `/qms/audit/[id]/findings/[findingId]` | Finding detail |
| `/qms/audit/checklists` | Checklist library |
| `/qms/audit/checklists/[id]` | Checklist editor |
| `/qms/audit/annual-plan` | Annual audit plan |
| `/qms/audit/auditor-qualifications` | Auditor qualification register |

### 11.3 Acceptance criteria

- [ ] Drag-and-drop calendar reschedules audits
- [ ] 4-tab Audit Workspace fully functional
- [ ] Two-column auditor picker works
- [ ] Major/Minor NC findings auto-create draft CAPA (verified via Kafka)
- [ ] Auditor qualification check enforced on Lead Auditor picker
- [ ] Audit Report PDF generation works
- [ ] Annual audit plan approval flow with e-signature

---

## 12. Phase 7 — Environmental Monitoring

**Duration:** 3 weeks
**Goal:** Build EM module with manual + IoT readings, alert/action limits, auto-QE on excursion.

### 12.1 Backend tasks

#### 12.1.1 Entities

- [ ] `MonitoringPoint` (id, tenant_id, point_id, location, parameter, alert_limit, action_limit, frequency_type, frequency_value, status, last_reading_value, last_reading_at, last_reading_status)
- [ ] `MonitoringReading` (id, tenant_id, point_id, value, recorded_at, recorded_by_user_id OR source_system, status: within_limits/alert/excursion, notes)

#### 12.1.2 Endpoints

- [ ] CRUD `GET/POST/PATCH /monitoring-points`
- [ ] `POST /monitoring-points/{id}/readings` — submit reading (manual or IoT)
- [ ] `GET /monitoring-points/{id}/readings?from=&to=` — time series
- [ ] `GET /monitoring-points/{id}/excursions` — list excursions
- [ ] MQTT bridge: subscribe to `tenant/{id}/sensors/{point_id}` → ingest to MonitoringReading

#### 12.1.3 Kafka consumers

- [ ] On excursion: emit `EnvironmentalMonitoring.Excursion` → Quality Event service consumes and creates QE

### 12.2 Frontend tasks

#### 12.2.1 EM Dashboard

- Tiles: Monitoring Points (count by status), Today's Readings, Active Excursions, Sensor Health
- Heatmap visualization: lab floor plan with sensor pins colored by status

#### 12.2.2 Monitoring Point detail page

- Header: Point ID, Location, Parameter, current status badge
- Tabs:
  - **Information**: limits, frequency, calibration
  - **Live Chart**: time-series chart of recent readings with alert/action limit lines using `recharts`
  - **Excursions**: list of past excursions with linked Quality Events
  - **History**: audit trail

#### 12.2.3 Manual reading entry

- Dialog: value + recorded_at + notes
- Auto-validates against limits, shows warning if alert/action exceeded

#### 12.2.4 Routes

| Route | Page |
|-------|------|
| `/qms/em` | EM Dashboard |
| `/qms/em/points` | Monitoring Points list |
| `/qms/em/points/[id]` | Monitoring Point detail |
| `/qms/em/excursions` | Excursions list |

### 12.3 Acceptance criteria

- [ ] IoT sensor reading via MQTT ingestion works
- [ ] Manual reading entry works
- [ ] Excursion detection triggers Quality Event auto-creation
- [ ] Live chart shows alert/action limit lines
- [ ] Heatmap floor plan view works (Phase 7.5 if time-tight)

---

## 13. Phase 8 — Risk Management

**Duration:** 3 weeks
**Goal:** Build Risk Management with FMEA, Impartiality Risk Register (ISO 17025 4.1 lab-specific differentiator).

### 13.1 Backend tasks

- [ ] `Risk` entity (id, tenant_id, risk_id, category (operational/impartiality/financial/regulatory/safety), description, severity, likelihood, risk_score (calculated), mitigation_plan, owner_id, status, review_date)
- [ ] `Opportunity` entity (similar structure for upside risks)
- [ ] `FMEA` entity for engineering-grade FMEA records
- [ ] Endpoints: CRUD for each; risk matrix endpoint for dashboard

### 13.2 Frontend tasks

#### 13.2.1 Risk Register page

- List with filter sidebar (Category, Status, Owner, Risk Score range)
- 5×5 Risk Matrix visualization (Severity × Likelihood) with risk count per cell
- Heatmap colors

#### 13.2.2 Impartiality Risk Register (special view)

- Specialized list filtered to category=impartiality
- Shows: Description, Affected Personnel, Mitigation Controls (rotation, blind testing, independent review), Review Frequency
- Auditor-friendly export

#### 13.2.3 Risk detail page

- InfoCard layout with sections for Risk Information, Assessment, Mitigation, Monitoring
- History tab

#### 13.2.4 Routes

| Route | Page |
|-------|------|
| `/qms/risk` | Risk dashboard with matrix |
| `/qms/risk/register` | Risk register list |
| `/qms/risk/[id]` | Risk detail |
| `/qms/risk/impartiality` | Impartiality risk register |
| `/qms/risk/opportunities` | Opportunities list |

### 13.3 Acceptance criteria

- [ ] 5×5 risk matrix renders with click-through
- [ ] Impartiality Risk Register view exists
- [ ] Quarterly review reminder fires
- [ ] Risk-based prioritization feeds Audit module (audits scheduled more frequently for high-risk areas)

---

## 14. Phase 9 — Proficiency Testing

**Duration:** 3 weeks
**Goal:** Build PT module — lab-specific differentiator. Track PT rounds, z-score/En calculation, auto-CAPA on unsatisfactory.

### 14.1 Backend tasks

- [ ] `PTProgram` entity (provider, scheme_name, frequency, parameters)
- [ ] `PTRound` entity (program_id, round_id, sample_received_date, result_due_date, reported_result, reference_value, z_score, en_number, status, capa_id)
- [ ] z-score and En number calculation logic
- [ ] Endpoints: CRUD + `POST /pt-rounds/{id}/submit-result`, `POST /pt-rounds/{id}/record-score`

### 14.2 Frontend tasks

- [ ] PT Programs list and detail (subscribed schemes per section)
- [ ] PT Round entry: blind sample receipt → result entry → reference reveal → score
- [ ] z-score trend chart per scheme over time
- [ ] Auto-CAPA on |z| > 3 with banner notification

#### 14.2.1 Routes

| Route | Page |
|-------|------|
| `/qms/pt` | PT dashboard |
| `/qms/pt/programs` | PT Programs list |
| `/qms/pt/programs/[id]` | Program detail (rounds history) |
| `/qms/pt/rounds/[id]` | PT Round entry |
| `/qms/pt/trends` | Cross-scheme trend analysis |

### 14.3 Acceptance criteria

- [ ] PT Round entry blind workflow works (analyst sees no reference until system reveals)
- [ ] z-score auto-calculated correctly (formula verified)
- [ ] Unsatisfactory result auto-creates CAPA
- [ ] z-score trend chart over time renders

---

## 15. Phase 10 — Customer Complaints

**Duration:** 3 weeks
**Goal:** Build Complaint module for ISO 17025 7.9 compliance.

### 15.1 Backend tasks

- [ ] `Complaint` entity (complaint_number, customer_id or name, received_via, severity, category, description, investigator_id, root_cause, response_text, response_sent_at, capa_id, status)
- [ ] Endpoints: CRUD + `POST /complaints/{id}/respond`, `POST /complaints/{id}/escalate-to-capa`
- [ ] Email intake bridge: monitored mailbox → parse → create complaint draft

### 15.2 Frontend tasks

#### 15.2.1 Complaint detail page — FBS-style 7-tab form

Tabs:
- **About**: Number, Status, Customer, Severity, Category, Date Received, Date Resolved
- **Complaint Information**: Description, Received Via, Linked Order/Sample
- **Customer Information**: Customer details (Name, Phone, Email, Account, Account Manager)
- **Investigation**: Investigator, Findings, Root Cause
- **Response**: Draft Response, Sent Date, Acknowledgment Received
- **Action Items**: Linked actions (escalates to CAPA if systemic)
- **Communications Log**: Append-only

#### 15.2.2 Routes

| Route | Page |
|-------|------|
| `/qms/complaints` | Complaints list |
| `/qms/complaints/[id]` | Complaint detail |
| `/qms/complaints/dashboard` | Complaint trends + analytics |

### 15.3 Acceptance criteria

- [ ] 7-tab FBS detail page
- [ ] Email intake bridge works (creates draft complaint from monitored mailbox)
- [ ] Escalation to CAPA works
- [ ] Auto-acknowledgment email sent to customer on intake

---

## 16. Phase 11 — Management Review

**Duration:** 2 weeks
**Goal:** Build Management Review module — auto-compiles 12 ISO 17025 Clause 8.9.2 inputs from all prior modules.

### 16.1 Backend tasks

- [ ] `ManagementReview` entity (id, tenant_id, review_date, chaired_by_id, attendees[], inputs_snapshot (JSONB), decisions[], action_items[], minutes_file_id, status)
- [ ] `ReviewActionItem` entity (id, review_id, description, owner_id, due_date, status)
- [ ] Endpoint: `POST /management-reviews/{id}/compile-inputs` — calls each module's summary endpoint, snapshots all 12 inputs
- [ ] Endpoint: `POST /management-reviews/{id}/generate-package` — produces PDF/Excel package

### 16.2 Frontend tasks

#### 16.2.1 Management Review detail page

- 12 collapsible accordion sections matching ISO 17025 8.9.2 inputs:
  1. Status of actions from previous review
  2. Policy/objectives suitability
  3. Audit results
  4. CAPA status
  5. External assessments
  6. Quality indicators/KPIs
  7. Supplier performance
  8. Customer feedback
  9. Risk register status
  10. Training status
  11. Resource adequacy
  12. PT performance
- Each section auto-populates from respective module
- Decisions section: free-text + decision records
- Action Items section: assign + track

#### 16.2.2 Routes

| Route | Page |
|-------|------|
| `/qms/management-review` | List of past reviews + schedule next |
| `/qms/management-review/[id]` | Review detail (12 inputs, decisions, action items) |
| `/qms/management-review/[id]/preview-package` | Auto-generated PDF/Excel preview |

### 16.3 Acceptance criteria

- [ ] All 12 inputs auto-compile from respective services
- [ ] Generated review package PDF passes auditor visual inspection
- [ ] Action items tracked to closure

---

## 17. Phase 12 — Reporting & Analytics Completion

**Duration:** 3 weeks
**Goal:** Replace the analytics service stub with real implementation. Add dashboards matching MasterControl pie chart pattern.

### 17.1 Backend tasks

- [ ] Build out `reporting-service` and `analytics-service` from stubs
- [ ] Materialized views in Postgres for fast dashboard queries
- [ ] Endpoints:
  - `GET /analytics/dashboards/{name}` — pre-computed dashboard data
  - `GET /analytics/kpis` — KPI summary
  - `GET /analytics/time-series?metric=&from=&to=&group_by=`
  - `POST /reports/export?type=pdf|excel&template=`

### 17.2 Frontend tasks

#### 17.2.1 Replace stub analytics page

Required dashboards (matching MasterControl pie charts):

| Dashboard | Chart Type | Data |
|-----------|-----------|------|
| **Quality Scorecard** | Cards + bars | Open CAPAs, Overdue Training, Cal Overdue, etc. |
| **CAPA by Department** | Pie | Count of open CAPAs grouped by department |
| **Complaints by Product** | Pie | Count of complaints grouped by product/sample |
| **NCMR Disposition** | Pie | Scrap / Rework-Repair / Return to Supplier / Accept - Not Defective |
| **Training Compliance** | Stacked bar by department | % complete / in progress / overdue |
| **Audit Findings Trend** | Time-series line | Findings over time, segmented by classification |
| **PT Performance** | Time-series line | z-score per scheme over time |
| **Equipment Calibration Status** | Pie | In Service / Due / Overdue / OOS |

#### 17.2.2 Routes

| Route | Page |
|-------|------|
| `/qms/analytics` | Main analytics dashboard (8 widgets) |
| `/qms/analytics/[dashboard]` | Individual dashboard detail |
| `/qms/analytics/reports` | Export center (generate custom reports) |

### 17.3 Acceptance criteria

- [ ] All 8 dashboards render with real data
- [ ] Export to PDF/Excel works
- [ ] Time-series charts have date range selector
- [ ] Drill-down from chart to underlying record list

---

## 18. Phase 13 — Lab-Specific Features

**Duration:** 4 weeks
**Goal:** Build the lab-specific moat — Method Validation, Measurement Uncertainty, Control Charts, etc.

### 18.1 Method Validation

- [ ] New `MethodValidation` entity, multi-step workflow
- [ ] Parameters: accuracy, precision, LOD, LOQ, linearity, range, robustness
- [ ] Statistical calculations per parameter
- [ ] Validation report PDF generation
- [ ] Routes: `/qms/lab/method-validation`

### 18.2 Measurement Uncertainty

- [ ] GUM (Guide to Expression of Uncertainty in Measurement) methodology
- [ ] Uncertainty budget builder: identify sources, quantify, combine
- [ ] Linked to Calibration records and Method Validation
- [ ] Routes: `/qms/lab/uncertainty`

### 18.3 Control Charts

- [ ] Shewhart, CUSUM, EWMA, Westgard rules
- [ ] Real-time control chart per analytical method
- [ ] Auto-flagging of rule violations
- [ ] Linked to Quality Event auto-creation
- [ ] Routes: `/qms/lab/control-charts`

### 18.4 Microbiology Workflows

- [ ] Media Prep QC: batch records, sterility check, performance check
- [ ] Culture Collection: reference strain inventory with passage number
- [ ] Aseptic Technique Assessment: periodic competency check (links to Training)
- [ ] Routes: `/qms/lab/microbiology/...`

### 18.5 Chemistry Workflows

- [ ] CRM Tracking: certified reference material inventory + expiry
- [ ] HPLC/GC/ICP system suitability tests
- [ ] Routes: `/qms/lab/chemistry/...`

### 18.6 Calibration Certificates

- [ ] Customer-facing certificate generation for client instruments
- [ ] Template editor for certificate layouts
- [ ] Routes: `/qms/lab/calibration-certificates`

### 18.7 Acceptance criteria

- [ ] At least 3 of 6 lab-specific features fully functional
- [ ] Each is linked to relevant primary module (QE, Equipment, Training)

---

## 19. Phase 14 — Supplier Quality (DEFERRED)

**Status:** **DEFERRED** — awaiting clarification from manager on scope and timeline.

**Tentative scope (when unblocked):**
- 7-status supplier model (Approved / Not Approved / Conditionally Approved / Under Qualification / Inactive / Certified / Disapproved)
- Supplier qualification workflow
- Material/Part linking with auto-disable on status drop
- Secure Guest Connect for external supplier collaboration
- CoA verification per lot
- Risk-driven audit frequency (integrates with Audit module)
- Supplier scorecard

**Pending questions for manager:**
- Is Phase 4 Supplier Portal (full external login) needed, or is lightweight Guest Connect sufficient?
- Which suppliers are in scope first (Critical only, or all)?
- Existing supplier data migration: source system?
- Integration with procurement / ERP system?

**Estimated duration:** 3 weeks once unblocked.

---

## 20. Cross-Cutting Workstreams

These workstreams run in parallel across phases.

### 20.1 Cross-Module Event Flows

Once Phase 1 (Kafka) is done, wire these 9 flows in sequence as each receiving module is built:

| # | Source Event | Target Module | Action |
|---|-------------|---------------|--------|
| 1 | `Document.Effective` | Training | Auto-assign training to distribution list users |
| 2 | `Document.Approved` | Notification | Email owner + approvers + distribution |
| 3 | `QualityEvent.Created` (Critical) | CAPA | Auto-create CAPA |
| 4 | `Audit.FindingCreated` (Major/Minor NC) | CAPA | Auto-create draft CAPA |
| 5 | `Equipment.CalibrationFailed` | Quality Event | Auto-create OOT event |
| 6 | `EnvironmentalMonitoring.Excursion` | Quality Event | Auto-create deviation |
| 7 | `PT.RoundUnsatisfactory` | CAPA | Auto-initiate CAPA |
| 8 | `CAPA.ActionOverdue` | Notification | Escalate at 7/14/30 days |
| 9 | `Training.AssignmentOverdue` | Notification | Alert employee + supervisor |

### 20.2 RBAC Enforcement

| Phase | Action |
|-------|--------|
| Phase 1 | API gateway-level RBAC enforcement, role→permission map verified |
| All phases | Every new endpoint must declare required permission |
| Phase 12 | Audit RBAC enforcement via penetration testing |

### 20.3 Tenant Isolation

| Phase | Action |
|-------|--------|
| All phases | Every new entity has `tenant_id` filtered query |
| Phase 1 | File service stores per-tenant paths |
| Phase 12 | Cross-tenant data leak test in CI |

### 20.4 21 CFR Part 11 Compliance

| Phase | Requirement | Action |
|-------|-------------|--------|
| Phase 1 | §11.50 Signature manifestations | `<SignatureDialog />` captures meaning |
| Phase 1 | §11.10(e) Audit trail | Audit Trail service captures all ops |
| Phase 1 | §11.100(b), §11.200(a)(1) Re-authentication | Re-auth endpoint + frontend modal |
| Phase 1 | §11.10(g) Authority checks | RBAC enforced |
| All phases | §11.10(c) Records retention | `retention_period` on entities + scheduled archival |

### 20.5 Testing Strategy

| Test type | Coverage target | Phase |
|-----------|----------------|-------|
| Unit tests | 80% line coverage per service | Continuous |
| Integration tests | Every cross-service flow | After Phase 1 |
| E2E tests | Every primary user journey | Per phase |
| Visual regression | All major pages | Phase 2+ |
| Load tests | 1000 concurrent users | Phase 12 |
| Compliance tests | 21 CFR Part 11 checklist | Phase 12 |

### 20.6 Documentation

| Phase | Doc updates |
|-------|-------------|
| Per phase | Update API docs (OpenAPI) |
| Per phase | Update user-facing help center articles |
| Phase 12 | Generate IQ/OQ/PQ validation package for regulated customers |

---

## 21. Acceptance & Sign-Off Criteria

### 21.1 Per-phase sign-off checklist

For each phase, before marking complete:

- [ ] All backend endpoints in the phase return 2xx for happy paths
- [ ] All frontend pages in the phase render without errors
- [ ] All API fields are bound to UI (no hidden data)
- [ ] All UI elements match the MasterControl reference visually (designer review)
- [ ] Kafka events fire as expected (verified by consuming on test topic)
- [ ] Audit trail captures all operations (verified by querying audit-trail service)
- [ ] Tenant isolation verified (cross-tenant test passes)
- [ ] RBAC enforced (unauthorized access returns 403)
- [ ] Unit tests pass (≥80% coverage)
- [ ] E2E tests pass for happy paths
- [ ] Documentation updated

### 21.2 Final product sign-off (after Phase 13)

- [ ] All 14 modules functional (M8 Supplier may be deferred per manager decision)
- [ ] 21 CFR Part 11 compliance audit passes
- [ ] ISO 17025 clause-by-clause coverage verified
- [ ] Real lab pilot deployment runs for 30 days without showstopper defects
- [ ] Validation package (IQ/OQ/PQ) produced for regulated customers
- [ ] Pricing tiers ($50/$100/$150-200 per user/month) live
- [ ] Multi-tenant deployment to production verified

---

*End of RainerQMS Phased Build Plan with UI Specifications.*

*This document is meant to be a living plan — update phase scope, dates, and acceptance criteria as the team learns and as the manager clarifies Supplier (M8) priority.*
