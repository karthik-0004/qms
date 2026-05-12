# RainerQMS — Comprehensive Master Documentation

> **Document Purpose:** This is the single authoritative reference for the RainerQMS Quality Management System, synthesized from all available documentation files. It is intended to give a new team member complete understanding of the product without reading source documents individually.
>
> **Source:** Synthesized from `RainerQMS-Documentation-main` (README + 5 documentation sections, 22 markdown files)
> **Last Source Date:** February 25, 2026

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [All Services / Modules](#2-all-services--modules)
3. [User Roles & Permissions](#3-user-roles--permissions)
4. [Workflows](#4-workflows)
5. [Key Entities & Fields](#5-key-entities--fields)
6. [Integrations & Dependencies](#6-integrations--dependencies)
7. [Technical Architecture](#7-technical-architecture)
8. [Compliance & Regulatory Framework](#8-compliance--regulatory-framework)
9. [Pricing Tiers](#9-pricing-tiers)
10. [Development Roadmap](#10-development-roadmap)
11. [Gaps & Missing Information](#11-gaps--missing-information)

---

## 1. System Overview

### 1.1 What is RainerQMS?

**RainerQMS** is a **cloud-native, multi-tenant, microservice-based Quality Management System (QMS)** purpose-built for **Microbiology and Chemistry Laboratories**. It is not a retrofitted generic QMS — every module and workflow is designed around the specific needs of testing and calibration laboratories.

### 1.2 The Problem It Solves

| Problem | Detail |
|---|---|
| **Paper & Spreadsheet Dependency** | Over 60% of small-to-mid-size labs still rely on paper or Excel for quality management, causing data integrity issues, lost records, and audit failures |
| **Generic QMS Tools Are Lab-Unfriendly** | Major QMS platforms (MasterControl, Veeva Vault, ETQ, TrackWise) are built for pharma/meddev manufacturing, not testing labs. They lack native support for method validation, proficiency testing, environmental monitoring, sample chain-of-custody, and instrument calibration |
| **Prohibitive Pricing** | Enterprise QMS tools cost $300–$600+/user/month, making them inaccessible to labs with 10–100 staff |
| **Disconnected Systems** | Labs typically run a LIMS, a separate document system, spreadsheets for training, and paper for audits/CAPA — creating data silos and compliance gaps |
| **Intensifying Regulatory Pressure** | ISO 17025:2017 and ISO 15189:2022 require risk-based thinking, impartiality management, and documented competence. FDA 21 CFR Part 11 compliance for e-signatures and audit trails is now a baseline expectation |

### 1.3 Who Are the Intended Users?

RainerQMS serves **five primary personas** across laboratory organizations:

| Persona | Role | Primary Needs |
|---|---|---|
| **Dr. Priya Sharma** | Laboratory Director / Quality Manager | Maintain accreditation, reduce audit prep time, real-time quality visibility |
| **Rajesh Patel** | Senior Microbiologist / Section Head | Team SOP compliance, environmental monitoring, PT tracking, media QC |
| **Sarah Chen** | QA Officer / Internal Auditor | End-to-end CAPA, change control, supplier management, management review data |
| **David Okonkwo** | Lab Technician / Analyst | Access current SOPs, complete training, log instrument use, report deviations |
| **Lisa Moreau** | IT Administrator | Multi-site deployment, SSO, LIMS integration, system validation, security |

**Target laboratory types:**
- Primary: Environmental testing, food & beverage, pharmaceutical QC, chemical, calibration, cannabis/hemp, forensic, agriculture labs
- Secondary: Clinical microbiology, clinical chemistry, pathology, blood bank, public health labs
- Tertiary: CROs, laboratory networks/chains, government lab systems, university research labs

### 1.4 End-to-End System Summary

RainerQMS delivers a unified platform where:

1. **Documents** are created, reviewed, electronically signed, version-controlled, and distributed — automatically triggering training assignments upon approval
2. **Quality Events** (deviations, OOS, non-conformances) are reported, classified by severity, investigated with built-in root cause tools, and escalated to CAPA when needed
3. **CAPAs** are managed through a full lifecycle — root cause investigation, action planning, implementation tracking, and effectiveness verification
4. **Audits** are planned on a risk-based schedule, executed digitally, and findings are automatically linked to CAPAs
5. **Training** is auto-assigned based on document approvals or role changes, delivered in-app, tracked with assessments, and recorded against employee competency profiles
6. **Equipment** is tracked through its full lifecycle with automated calibration scheduling, out-of-tolerance handling, and usage logging
7. **Environmental Conditions**, **Supplier Quality**, **Risk**, **Proficiency Testing**, **Customer Complaints**, and **Management Reviews** are all managed within the same platform
8. **AI-powered analytics** surface trends, suggest root causes, generate training assessments, and provide predictive compliance insights across all modules

---

## 2. All Services / Modules

RainerQMS is composed of **14 core business modules** plus a set of **platform/infrastructure services**, each implemented as an independent microservice.

### 2.1 Core Business Modules

| # | Module Name | Microservice | Purpose | QMS Workflow Phase |
|---|---|---|---|---|
| 1 | **Document Control & Management** | `document-service` | Full lifecycle management of SOPs, work instructions, test methods, policies, forms, manuals. Version control, change control, electronic approvals, distribution, periodic review | Quality System Foundation |
| 2 | **Quality Event Management** | `quality-event-service` | Capture, classify, investigate, and resolve deviations, non-conformances, OOS/OOT results, and non-conforming work | Quality Event Detection & Response |
| 3 | **CAPA Management** | `capa-service` | Full Corrective Action / Preventive Action lifecycle: identification → root cause → action planning → implementation → effectiveness verification | Corrective & Preventive Action |
| 4 | **Audit Management** | `audit-service` | Plan, execute, and track internal audits, external assessments, management reviews, with finding-to-CAPA traceability | Quality Assurance & Oversight |
| 5 | **Training & Competency Management** | `training-service` | Employee training programs, competency assessments, qualification records, auto-assignment from document changes | Personnel Quality |
| 6 | **Equipment & Calibration Management** | `equipment-service` | Full instrument lifecycle from procurement to decommission: calibration scheduling, maintenance, qualification, usage logging, out-of-tolerance handling | Resource Management |
| 7 | **Environmental Monitoring** | `envmon-service` | Monitor temperature, humidity, particulate counts, differential pressure; excursion alerts; trend analysis; IoT sensor integration | Facility & Environmental Control |
| 8 | **Supplier & Reagent Quality Management** | `supplier-service` | Qualify, monitor, and manage suppliers of reagents, reference materials, consumables, and external services | Supply Chain Quality |
| 9 | **Risk Management** | `risk-service` | Identify, assess, mitigate, and monitor risks across laboratory operations; FMEA; impartiality risk; opportunity management | Risk-Based Quality |
| 10 | **Proficiency Testing & ILC** | `proficiency-testing-service` | Manage PT program participation, results (z-scores, En numbers), unsatisfactory result handling → CAPA, trend analysis | Method Performance Assurance |
| 11 | **Customer Complaint & Feedback Management** | `complaint-service` | Receive, investigate, and resolve customer complaints and feedback; CAPA linkage; trend analysis; client portal | Customer Quality |
| 12 | **Management Review** | `management-review-service` | Automate preparation, execution, and follow-up of management reviews; auto-compile required ISO 17025 inputs | Leadership & Governance |
| 13 | **Reporting & Analytics** | `analytics-service` | Real-time dashboards, configurable reports, AI-powered analytics, KPI tracking, compliance scorecards | Quality Intelligence |
| 14 | **Lab-Specific Features** | *(distributed across services)* | Microbiology: media prep QC, culture collection, aseptic monitoring. Chemistry: method validation, measurement uncertainty, CRM tracking, control charts. Calibration: certificate generation, guard banding, traceability tree | Laboratory Technical Operations |

### 2.2 Platform / Infrastructure Services

| Service | Microservice | Responsibility |
|---|---|---|
| **API Gateway** | `api-gateway` (Kong/AWS API GW) | Request routing, rate limiting, authentication, tenant resolution |
| **Authentication** | `auth-service` (Keycloak) | Authentication, authorization, SSO, JWT token management |
| **Tenant Management** | `tenant-service` | Tenant provisioning, configuration, lifecycle management |
| **Notification Engine** | `notification-service` | Email, SMS, in-app, and webhook notifications |
| **Workflow Engine** | `workflow-engine` (Temporal) | No-code workflow execution, approval routing, long-running processes |
| **File Service** | `file-service` | File upload, storage (S3), retrieval, virus scanning |
| **Search Service** | `search-service` (OpenSearch) | Full-text search across all modules |
| **AI/ML Service** | `ai-service` (Python FastAPI) | Trend detection, root cause suggestion, exam generation, document summarization |

---

## 3. User Roles & Permissions

### 3.1 Built-In Roles (MVP — 5 roles)

| Role | Permissions | Restrictions |
|---|---|---|
| **System Admin / Tenant Admin** | Full system access: tenant configuration, user management, system settings, integrations, branding, workflow definitions, role assignments, audit log access | Cannot access data outside their tenant; no cross-tenant operations |
| **Quality Manager** | Full access to all quality modules (documents, CAPAs, audits, events, training, equipment, supplier, risk, PT, complaints, management review); full approval authority across all modules; CAPA creation and closure; audit program management | Cannot modify system settings or manage tenants |
| **Lab Director** | Read access to all quality data and dashboards; approval authority for policies and management review documents; management review participation | Cannot create/edit operational quality records (CAPAs, events, training assignments); limited write access |
| **Section Head** | Full create/edit access to records within their assigned section/department; read access to related sections; approve documents within their scope; assign training to their team; audit execution within their area | Cannot access other sections' restricted data; cannot close CAPAs outside their scope without Quality Manager involvement |
| **Analyst / Technician** | Create and submit quality event reports, training completions, instrument logbook entries, environmental monitoring data; access current SOPs and assigned training; personal task dashboard | Cannot approve documents; cannot close CAPAs; limited to their own training records and assigned tasks; read-only for records they did not create |
| **Viewer (Read-Only)** | View-only access to specified modules (e.g., dashboards for management, document access for clients) | No create, edit, or approve actions; no access to restricted modules |
| **Auditor** | Audit execution: create and execute audit checklists, record findings, collect evidence, generate audit reports; read access to all audited areas and linked historical records | Cannot modify records outside of audit-specific actions; cannot close CAPAs |
| **API User** | Programmatic access to defined API scopes for integrations | Access limited to defined API key scope; no UI access |

> **Note:** The MVP includes 5 built-in roles (Admin, Quality Manager, Section Head, Analyst, Viewer). Custom roles are deferred to Phase 2. Advanced RBAC with field-level permissions and data-scope restrictions is deferred to Phase 3.

### 3.2 Phase 2+ Extended RBAC Features (Deferred)

- Custom role creation
- Field-level permissions
- Data-scope restrictions (limit users to specific equipment, document categories, etc.)
- Auditor qualification tracking and independence enforcement

---

## 4. Workflows

### 4.1 Document Lifecycle Workflow

**Trigger:** New SOP required, existing SOP revision needed, periodic review due, or CAPA action requiring document change.

| Step | Action | Responsible Role | System Events |
|---|---|---|---|
| 1 | **Initiate** — Author creates new document or initiates revision; completes change request form (reason, impact assessment); document assigned draft version number | Author | Document record created; change request linked |
| 2 | **Draft & Edit** — Author creates/edits content using rich text editor with collaborative editing and tracked changes | Author | Version auto-incremented as Draft |
| 3 | **Review** — Author submits for review; reviewer(s) receive notification; reviewers provide comments, approve, or request changes. If changes requested → return to Step 2 | Reviewer(s) | Email notification sent; review deadline tracked |
| 4 | **Approval** — Approver(s) receive notification; review final version; apply electronic signature (21 CFR Part 11 compliant). If rejected → return to Step 2 with comments | Approver(s) | E-signature captured; approval recorded in audit trail |
| 5 | **Effective** — Document becomes current effective version; previous version auto-marked as Superseded; Master Document List updated; distribution notifications sent; AI generates change summary | System | `Document Approved` event published to event bus |
| 6 | **Training Trigger** — `training-service` receives event; training assignments auto-created for affected personnel; personnel notified; complete reading + assessment; completion recorded with e-signature | Affected Personnel | Training records created; completion tracked |
| 7 | **Periodic Review** — System schedules review based on config (e.g., annual); reminder sent to document owner 30/14/7 days before due; owner confirms current or initiates revision | Document Owner | Review completion recorded; next review date set |

**End State:** Document is live, effective, and in use; all affected personnel are trained; full audit trail captured.

**Conditional Branches:**
- Reviewer requests changes → back to Draft
- Approver rejects → back to Draft with comments
- Periodic review confirms no changes needed → review date reset, no new revision created

---

### 4.2 CAPA Workflow

**Trigger:** Quality event escalation, audit finding (Major/Minor NC), customer complaint, management review action, PT unsatisfactory result, or standalone initiation.

| Step | Action | Responsible Role | System Events |
|---|---|---|---|
| 1 | **Identification** — CAPA initiated (manually or auto-escalated); source event linked; classified as Corrective, Preventive, or Both; CAPA owner assigned; risk assessment (severity, occurrence, detectability) completed | Initiator / System | CAPA record created; source event linked; owner notified |
| 2 | **Investigation** — CAPA owner assembles team; data collected; root cause analysis using built-in tools (5-Why, Fishbone, Fault Tree, Pareto); AI suggests probable causes from historical data; root cause documented with evidence; reviewed and approved by Quality Manager | CAPA Owner, Investigator, Quality Manager | Investigation status tracked; RCA tools populated |
| 3 | **Action Planning** — Define corrective actions (address root cause) and preventive actions (prevent recurrence); each action assigned owner, due date, description, expected outcome; impact assessment on documents/training/processes; action plan approved by Quality Manager | CAPA Owner, Action Owners, Quality Manager | Action records created; due dates set |
| 4 | **Implementation** — Action owners execute assigned actions; evidence attached; document changes initiated via change control; retraining triggered for affected personnel; each action signed off; implementation verified by CAPA Owner | Action Owners, CAPA Owner | Evidence linked; document change workflow triggered; training auto-assigned |
| 5 | **Effectiveness Verification** — Scheduled at 30/60/90 days post-implementation; effectiveness reviewer evaluates: Has the issue recurred? Have metrics improved? Are actions sustained? If effective → proceed to Step 6. If not → return to Step 2 or 3 | Effectiveness Reviewer | Scheduled task created; pass/fail recorded |
| 6 | **Closure** — CAPA closed with final summary; Quality Manager final approval with e-signature; CAPA metrics updated; recurrence monitoring activated for defined period | Quality Manager | CAPA status = Closed; recurrence monitoring started |

**End State:** Root cause identified and addressed; corrective/preventive actions implemented and verified effective; full traceability from source event to closure.

**Escalation Rules:** Overdue CAPAs trigger escalation emails at 7/14/30 days overdue.

---

### 4.3 Internal Audit Workflow

**Trigger:** Annual audit schedule, risk-based trigger, or management directive.

| Step | Action | Responsible Role | System Events |
|---|---|---|---|
| 1 | **Annual Planning** — Audit Program Manager creates annual audit schedule; risk-based frequency per area/process; auditor assignments ensuring independence; schedule approved by Quality Manager | Audit Program Manager, Quality Manager | Audit schedule records created |
| 2 | **Audit Preparation** — Lead Auditor creates audit plan (scope, criteria, schedule); selects or creates checklist (ISO 17025, custom); reviews previous findings and open CAPAs; notifies auditee; schedules opening meeting | Lead Auditor | Audit notification sent to auditee |
| 3 | **Audit Execution** — Opening meeting conducted; auditors execute checklist items; evidence collected (documents, observations, photos); findings classified (Major NC, Minor NC, Observation, OFI); closing meeting with preliminary findings | Lead Auditor, Auditor(s), Auditee | Findings recorded; evidence attached; findings auto-create CAPA draft |
| 4 | **Reporting** — Lead Auditor compiles audit report; report reviewed and finalized; distributed to auditee and management | Lead Auditor | Audit report generated |
| 5 | **Auditee Response** — Auditee reviews findings; provides response and action plan; CAPAs auto-created for NC findings | Auditee | CAPAs created with audit finding as source |
| 6 | **Follow-Up** — CAPA implementation tracked through CAPA workflow; verification of corrective action effectiveness; follow-up audit scheduled if needed; audit closed when all findings resolved | Lead Auditor, Quality Manager | Audit status = Closed when all findings resolved |
| 7 | **Program Review** — Audit program effectiveness reviewed annually; results fed into management review; next year's program adjusted | Audit Program Manager | Data fed to management-review-service |

**End State:** Audit complete; all findings linked to CAPAs; audit results available for management review.

---

### 4.4 Equipment Calibration Workflow

**Trigger:** Scheduled calibration due date, post-maintenance verification, or user-initiated request.

| Step | Action | Responsible Role | System Events |
|---|---|---|---|
| 1 | **Scheduling** — System generates calibration due date based on interval; reminder notifications sent at 30/14/7/1 day before due; task assigned to technician; equipment status → "Calibration Due" | System, Calibration Coordinator | Notifications sent to calibration technician |
| 2 | **Preparation** — Calibration SOP accessed; reference standards verified (current calibration and traceability); environmental conditions verified; equipment taken out of service if required | Calibration Technician | Pre-cal checklist completed |
| 3 | **Execution** — As-found readings recorded; adjustments made if necessary; as-left readings recorded; pass/fail determination against acceptance criteria; measurement uncertainty calculated; calibration certificate generated | Calibration Technician | Calibration record created with all readings |
| 4 | **Review & Approval** — Results reviewed by qualified person. If PASS → equipment returned to service; next calibration date set. If FAIL → out-of-tolerance handling (Step 5) | Quality Manager / Qualified Reviewer | Equipment status updated |
| 5 | **Out-of-Tolerance Handling** (conditional) — Equipment placed "Out of Service"; quality event auto-created; impact assessment performed (which results may be affected?); clients notified if necessary; decision: repair, re-calibrate, or decommission; CAPA initiated if systemic issue | Quality Manager, Section Head | Quality event created; CAPA may be initiated |
| 6 | **Record Completion** — All calibration data stored with equipment record; certificate linked; equipment status label updated; next calibration date scheduled | System | Equipment record updated; next cal scheduled |

**End State:** Equipment calibrated and returned to service (or placed OOS); full calibration history maintained.

---

### 4.5 Non-Conforming Work Workflow (ISO 17025 Clause 7.10)

**Trigger:** Identification that testing or calibration work does not conform to procedures or agreed requirements.

| Step | Action | Responsible Role |
|---|---|---|
| 1 | **Identification** — NC work identified (by analyst, reviewer, QC check, or system); work immediately halted if quality of results is in question; NC record created | Analyst / Reviewer |
| 2 | **Evaluation** — Significance evaluated; determine if NC work is acceptable or must be rejected; risk assessment of impact on already-reported results; decision documented | Quality Manager, Section Head |
| 3 | **Client Notification** — If reported results may be affected → client notification required; work recalled if necessary; all communication documented | Quality Manager |
| 4 | **Corrective Action** — Immediate correction applied; root cause investigated; if recurrence risk → escalate to CAPA; responsible personnel identified; retraining initiated if competency issue | CAPA Owner, Section Head |
| 5 | **Authorization to Resume** — Corrective actions verified; Quality Manager authorizes resumption of work with electronic signature | Quality Manager |
| 6 | **Closure** — NC record completed; linked to CAPAs, training records, document changes; data fed into trend analysis | Quality Manager |

**End State:** Non-conforming work resolved, client notified (if applicable), work authorized to resume.

---

### 4.6 Supplier Qualification Workflow

**Trigger:** New supplier identified (reagent, reference material, service, or equipment).

| Step | Action | Responsible Role |
|---|---|---|
| 1 | **Supplier Identification** — New supplier identified; criticality classified (Critical, Major, Minor) | Quality Manager |
| 2 | **Initial Evaluation** — Supplier questionnaire sent and collected; capabilities assessed; quality system documentation reviewed; for Critical suppliers: on-site audit scheduled; evaluation scored | Quality Manager |
| 3 | **Approval Decision** — Approved → added to Approved Supplier List (ASL); Conditionally Approved → with conditions/timeline; Rejected → documented and notified | Quality Manager |
| 4 | **Ongoing Monitoring** — Performance metrics tracked (delivery, quality, NCRs); CoAs verified per lot received; incoming inspection logged; scorecard updated quarterly | QA Officer |
| 5 | **Re-Qualification** — Periodic re-evaluation (annually for Critical, biannually for Major); re-assessed on cumulative performance; status updated with decision rationale | Quality Manager |

---

### 4.7 Customer Complaint Workflow

**Trigger:** Complaint received via email, phone, web form, or client portal.

| Step | Action | Responsible Role |
|---|---|---|
| 1 | **Receipt** — Complaint received; auto-acknowledgment sent; logged with customer details, description, category; severity classified (Critical, Major, Minor) | System / QA Officer |
| 2 | **Investigation** — Complaint assigned to investigator; root cause analysis; related records (results, samples, deviations) reviewed; investigation findings documented | Investigator |
| 3 | **Response** — Response prepared; corrective actions described; reviewed by Quality Manager; sent to customer; customer satisfaction tracked | Quality Manager |
| 4 | **Corrective Action** — If systemic issue → CAPA initiated; corrective actions implemented; effectiveness verified; complaint linked to all related quality records | CAPA Owner |
| 5 | **Closure** — Complaint closed with summary; customer notified; data fed into trend analysis and management review | Quality Manager |

---

### 4.8 Management Review Workflow

**Trigger:** Scheduled review (typically annual or semi-annual).

| Step | Action | Responsible Role |
|---|---|---|
| 1 | **Scheduling** — Review scheduled; invitations sent to Lab Director, Quality Manager, Section Heads; data package preparation initiated 30 days before | Quality Manager |
| 2 | **Data Compilation (Automated)** — System auto-compiles all required ISO 17025 Clause 8.9.2 inputs: previous review actions status, policy suitability, audit results, CAPA status, external body assessments, quality indicators, supplier performance, customer feedback, risk status, training status, resource adequacy, PT performance | System (`management-review-service`) |
| 3 | **Review Meeting** — Agenda followed; each input discussed and documented; decisions recorded; action items created with owners and due dates; minutes captured | Lab Director, Quality Manager, Section Heads |
| 4 | **Follow-Up** — Management review report generated; action items tracked to completion; report distributed; next review date scheduled | Quality Manager |

---

### 4.9 Environmental Excursion Workflow

**Trigger:** Environmental monitoring reading exceeds defined alert or action limits (manual or automated sensor).

| Step | Action | Responsible Role |
|---|---|---|
| 1 | **Detection** — Excursion detected; real-time notification to responsible personnel; monitoring point flagged on dashboard | System |
| 2 | **Immediate Action** — Impact on samples, cultures, and ongoing tests assessed; affected items moved if necessary; immediate actions documented | Section Head / Analyst |
| 3 | **Investigation** — Quality event auto-created for action limit excursions; root cause investigated; duration and magnitude documented; impact on stored samples and in-process tests evaluated | Quality Manager |
| 4 | **Corrective Action** — Repair/fix environmental control if equipment-related; retesting of affected samples if necessary; CAPA initiated for recurring excursions; monitoring frequency increased if warranted | CAPA Owner |
| 5 | **Closure** — Event closed with summary and impact assessment; environmental conditions confirmed normal; data fed into environmental trend analysis | Quality Manager |

---

## 5. Key Entities & Fields

### 5.1 Core Entity Relationships

```
Tenant
├── Sites[]
│   └── Departments/Laboratories[]
├── Users[] (with Roles)
└── All quality data (documents, CAPAs, events, etc.)

Document ──────────────────────── version-of ──── PreviousDocument
  │                                                      │
  ├── ChangeRequest                               (Superseded)
  ├── Approvals[] ──── ESignature[]
  ├── DistributionList[]
  ├── TrainingAssignments[] ──── TrainingRecords[]
  └── linked to: CAPA, QualityEvent

QualityEvent ──── escalates-to ──── CAPA
  │                                    │
  ├── RootCauseAnalysis               ├── Actions[]
  ├── ImmediateActions                ├── EffectivenessCheck
  └── linked to: Equipment,           └── linked to: Document, AuditFinding,
      Document, Personnel                 QualityEvent, Complaint, PTResult

Equipment ──── CalibrationRecords[]
  │               └── Standards used
  ├── MaintenanceRecords[]
  ├── UsageLogbook[]
  └── auto-creates: QualityEvent (on OOT)

Audit ──── Findings[] ──── auto-creates ──── CAPA
  │            └── Evidence[]
  └── AuditReport

TrainingPlan ──── Courses[] ──── TrainingAssignments[] ──── TrainingRecords[]

Supplier ──── SupplierAudits[] ──── Findings[] ──── CAPA
  │
  └── ReagentLots[] ──── CoA[] ──── IncomingInspection[]
```

### 5.2 Document Entity

| Field | Purpose |
|---|---|
| `document_id` | Unique identifier |
| `document_number` | Sequential controlled document number |
| `title` | Document title |
| `type` | SOP, Work Instruction, Policy, Form, Method, Manual, External |
| `status` | Draft, Under Review, Approved, Superseded, Obsolete |
| `version` | Auto-incremented version number |
| `effective_date` | Date document became/becomes effective |
| `review_due_date` | Scheduled periodic review date |
| `owner` | Responsible user/role |
| `approvers[]` | List of required approvers |
| `distribution_list[]` | Users/roles who must receive and acknowledge |
| `content` | Rich text document body |
| `attachments[]` | Supporting files |
| `change_summary` | AI-generated or manual change description |
| `retention_period` | Configurable retention before archiving |
| `iso_clause_mapping` | Regulatory clause linkage |
| `audit_trail[]` | All create/update/approve/sign actions |

### 5.3 Quality Event Entity

| Field | Purpose |
|---|---|
| `event_id` | Unique identifier |
| `event_type` | Deviation, Non-Conformance, Non-Conforming Work, OOS, OOT |
| `severity` | Critical, Major, Minor |
| `description` | Detailed description of the event |
| `date_discovered` | When the event was identified |
| `area` | Laboratory section/department |
| `linked_equipment` | Associated instrument(s) |
| `linked_document` | Associated SOP/method |
| `linked_personnel` | Involved personnel |
| `immediate_action` | Actions taken immediately |
| `root_cause` | Identified root cause (from RCA) |
| `status` | Open, Under Investigation, CAPA Created, Closed |
| `capa_id` | Linked CAPA (if escalated) |
| `effectiveness_check_date` | Scheduled follow-up date |
| `client_notified` | Boolean (for NC work involving reported results) |

### 5.4 CAPA Entity

| Field | Purpose |
|---|---|
| `capa_id` | Unique identifier |
| `capa_type` | Corrective, Preventive, Both |
| `source_type` | Quality Event, Audit Finding, Complaint, PT Result, Management Review, Standalone |
| `source_id` | ID of originating record |
| `owner` | CAPA Owner user |
| `risk_severity / risk_occurrence / risk_detectability` | RPN scoring fields |
| `root_cause` | Documented root cause |
| `rca_tool_used` | 5-Why, Fishbone, Fault Tree, Pareto |
| `actions[]` | List of corrective/preventive action records |
| `status` | Identification, Investigation, Action Planning, Implementation, Effectiveness Check, Closed |
| `effectiveness_check_date` | Scheduled effectiveness review |
| `effectiveness_result` | Pass/Fail with evidence |
| `closed_date` | When CAPA was formally closed |
| `approvals[]` | QM sign-off with e-signature |

### 5.5 CAPA Action Entity

| Field | Purpose |
|---|---|
| `action_id` | Unique identifier |
| `capa_id` | Parent CAPA |
| `action_type` | Corrective, Preventive |
| `description` | What needs to be done |
| `owner` | Responsible person |
| `due_date` | Completion deadline |
| `expected_outcome` | Success criteria |
| `status` | Pending, In Progress, Complete, Overdue |
| `evidence[]` | Attached completion evidence |
| `completed_date` | Actual completion date |
| `signoff` | Electronic sign-off by action owner |

### 5.6 Audit Entity

| Field | Purpose |
|---|---|
| `audit_id` | Unique identifier |
| `audit_type` | Internal, External (Accreditation, Client, Regulatory) |
| `scope` | Areas/processes covered |
| `criteria` | ISO 17025, ISO 15189, GLP, GMP, Custom |
| `lead_auditor` | Assigned lead auditor |
| `auditors[]` | Audit team |
| `auditees[]` | Areas/personnel being audited |
| `scheduled_date` | Planned audit date |
| `checklist_id` | Selected or created checklist |
| `findings[]` | List of audit findings |
| `status` | Planned, In Progress, Reporting, Auditee Response, Follow-Up, Closed |
| `report` | Auto-generated audit report |

### 5.7 Audit Finding Entity

| Field | Purpose |
|---|---|
| `finding_id` | Unique identifier |
| `audit_id` | Parent audit |
| `classification` | Major NC, Minor NC, Observation, Opportunity for Improvement |
| `description` | Finding description |
| `evidence[]` | Photos, documents, interview notes |
| `iso_clause` | Relevant regulatory clause |
| `capa_id` | Auto-linked or manually linked CAPA |
| `auditee_response` | Auditee's written response |

### 5.8 Equipment Entity

| Field | Purpose |
|---|---|
| `equipment_id` | Unique system ID |
| `asset_tag` | Physical label/tag number |
| `name / model / manufacturer / serial` | Equipment identification |
| `location` | Physical location within facility |
| `status` | In Service, Calibration Due, Under Calibration, Under Maintenance, Out of Service, Decommissioned |
| `calibration_interval` | Time-based or usage-based interval |
| `next_calibration_due` | System-calculated next due date |
| `last_calibration_date` | Most recent calibration date |
| `calibration_records[]` | History of all calibrations |
| `maintenance_records[]` | History of maintenance |
| `usage_logbook[]` | Digital use log entries |
| `measurement_uncertainty` | Linked uncertainty budget |

### 5.9 Training Assignment Entity

| Field | Purpose |
|---|---|
| `assignment_id` | Unique identifier |
| `user_id` | Trainee |
| `course_id` | Training course (linked to document or standalone) |
| `trigger` | Document Approval, Manual, CAPA Action, Role Change, Periodic |
| `assigned_date` | When assignment was created |
| `due_date` | Completion deadline |
| `status` | Assigned, In Progress, Complete, Overdue |
| `completion_date` | When completed |
| `assessment_score` | Quiz/exam score |
| `passing_score` | Required threshold |
| `e_signature` | Electronic sign-off on completion |

### 5.10 Calibration Record Entity

| Field | Purpose |
|---|---|
| `calibration_id` | Unique identifier |
| `equipment_id` | Associated equipment |
| `calibration_date` | Date performed |
| `technician` | Who performed the calibration |
| `standards_used[]` | Reference standards used (with their own calibration status) |
| `as_found_readings[]` | Pre-calibration measurement data |
| `as_left_readings[]` | Post-calibration measurement data |
| `pass_fail` | Outcome against acceptance criteria |
| `measurement_uncertainty` | Calculated uncertainty for this calibration |
| `certificate` | Generated calibration certificate |
| `next_due_date` | Calculated from interval |

### 5.11 Audit Trail Record (Immutable)

Every write operation across all modules generates an audit trail entry:

| Field | Purpose |
|---|---|
| `id` | Unique UUID |
| `tenant_id` | Tenant context |
| `user_id / user_name` | Who performed the action |
| `action` | CREATE, UPDATE, DELETE, APPROVE, SIGN, LOGIN, EXPORT |
| `entity_type` | Document, CAPA, QualityEvent, TrainingRecord, etc. |
| `entity_id` | ID of affected record |
| `before_value` | JSON snapshot before change |
| `after_value` | JSON snapshot after change |
| `ip_address` | Client IP |
| `user_agent` | Browser/client info |
| `timestamp` | UTC server-generated timestamp |
| `signature_id` | Linked e-signature (if action required one) |

> Audit trail records are **append-only**. No UPDATE or DELETE operations are permitted. Stored in a separate write-optimized, tamper-evident table.

---

## 6. Integrations & Dependencies

### 6.1 LIMS Integrations

| LIMS Platform | Integration Type | Data Flow |
|---|---|---|
| **LabWare LIMS** | REST API + Database bridge | Bi-directional |
| **Thermo Fisher SampleManager** | REST API | Bi-directional |
| **STARLIMS** | REST API + Web services | Bi-directional |
| **LabVantage** | REST API | Bi-directional |
| **Agilent OpenLab** | File-based + API | Instrument data → RainerQMS |
| **QBench** | REST API | Bi-directional |
| **Scispot** | REST API | Bi-directional |

**Key LIMS Data Exchange Points:**

| Data Type | Direction | Description |
|---|---|---|
| Sample Registration | LIMS → QMS | New sample metadata triggers chain-of-custody in QMS |
| OOS/OOT Results | LIMS → QMS | Out-of-spec results auto-create quality events in QMS |
| Method References | QMS → LIMS | Approved test methods and SOPs referenced in LIMS workflows |
| Instrument Status | QMS → LIMS | Equipment calibration status shared with LIMS for method eligibility |
| Analyst Competency | QMS → LIMS | Training/competency status shared for analyst authorization |
| Deviation Records | QMS ↔ LIMS | Bi-directional sharing of deviation and investigation data |

### 6.2 ERP Integrations

| ERP Platform | Integration Type |
|---|---|
| SAP S/4HANA | REST API + IDoc/RFC |
| Oracle ERP Cloud | REST API |
| Microsoft Dynamics 365 | REST API / Dataverse |
| NetSuite | SuiteTalk REST API |

### 6.3 Identity Provider / SSO

| Provider | Protocol |
|---|---|
| Azure Active Directory | SAML 2.0, OAuth 2.0, OIDC |
| Okta | SAML 2.0, OAuth 2.0, OIDC |
| OneLogin | SAML 2.0 |
| Google Workspace | OAuth 2.0, OIDC |

> SSO integration is deferred to Phase 2 (Month 8). MVP supports email/password + MFA only.

### 6.4 Instrument & IoT Integrations

| Integration Type | Method |
|---|---|
| Analytical Balances | Serial/USB + middleware |
| pH Meters | Serial/USB + middleware |
| Chromatography (HPLC/GC) | CDS integration (Empower, OpenLab, Chromeleon) |
| Temperature/Humidity Sensors | IoT (MQTT/HTTP) |
| Data Loggers | File export + API |
| Autoclaves | Serial + middleware |
| Incubators | IoT sensors |

A lightweight **Edge Agent** can be installed on lab computers to collect instrument data, parse output files, validate, and transmit to RainerQMS cloud via secure API. Buffers data during connectivity interruptions.

### 6.5 Third-Party Application Integrations

| Application | Integration | Use Case |
|---|---|---|
| Microsoft 365 | OAuth + Graph API | Document collaboration, email, Teams notifications |
| Google Workspace | OAuth + API | Document collaboration, calendar, email |
| Slack | Webhook + Bot | Quality event notifications, CAPA reminders, approval requests |
| Microsoft Teams | Webhook + Bot | Same as Slack |
| Jira | REST API | Link quality events to engineering tickets |
| Salesforce | REST API | Customer complaint sync |
| DocuSign | REST API | External document signing workflows |
| Power BI | REST API + Connector | Advanced analytics |
| Tableau | REST API + Connector | Advanced analytics |

### 6.6 Generic Integration Protocols

| Protocol | Use Case |
|---|---|
| HL7 FHIR | Clinical laboratory data exchange |
| ASTM E1394 | Instrument-to-LIMS data communication |
| SiLA 2 | Smart integration of laboratory instruments |
| OPC UA | Industrial IoT device integration |
| MQTT | Lightweight IoT sensor data (environmental monitoring) |

### 6.7 API Platform

| Attribute | Detail |
|---|---|
| Architecture | RESTful with optional GraphQL endpoint |
| Authentication | OAuth 2.0 with API keys and JWT bearer tokens |
| Documentation | OpenAPI 3.0 (Swagger) with interactive API explorer |
| Rate Limiting | Configurable per tenant and per API key |
| Versioning | URI-based (e.g., `/api/v1/`, `/api/v2/`) |
| Webhooks | Outbound webhooks for real-time event notifications |
| SDKs | Python, JavaScript/TypeScript, C#, Java |
| Sandbox | Dedicated sandbox environment for integration development |

> Public REST API is deferred to Phase 2 (Month 9). GraphQL API is deferred to Phase 3 (Month 17).

---

## 7. Technical Architecture

### 7.1 Technology Stack Summary

| Layer | Technology |
|---|---|
| **Frontend** | React 18 + TypeScript, Vite, TanStack Query, Zustand, Shadcn/ui, Tailwind CSS, TipTap editor, Recharts + D3.js |
| **Backend** | Node.js + TypeScript, NestJS, Prisma ORM |
| **Auth** | Keycloak 24+ (OIDC, SAML 2.0, user federation) |
| **AI/ML** | Python 3.11+, FastAPI, scikit-learn, OpenAI/Anthropic API, pandas, statsmodels/Prophet |
| **Primary DB** | PostgreSQL 16 (schema-per-tenant isolation) |
| **Cache** | Redis 7 |
| **Search** | OpenSearch 2.x (AWS Managed) |
| **Event Bus** | Apache Kafka 3.x (AWS MSK) |
| **Analytics DB** | TimescaleDB or ClickHouse |
| **File Storage** | AWS S3 |
| **Workflow Engine** | Temporal |
| **Infrastructure** | AWS EKS (Kubernetes), CloudFront CDN, RDS, ElastiCache, MSK |
| **IaC** | Pulumi (TypeScript) |
| **CI/CD** | GitHub Actions + ArgoCD |

### 7.2 Multi-Tenancy Model

**Hybrid isolation approach:**

| Layer | Isolation |
|---|---|
| Application | Shared instances with tenant context injection |
| Database | **Schema-per-tenant** within shared PostgreSQL clusters |
| File Storage | Tenant-specific S3 buckets/prefixes with IAM policies |
| Cache | Namespace-per-tenant in shared Redis |
| Search | Tenant-specific index aliases |

**Tenant request flow:**
1. Client sends request with JWT token
2. API Gateway validates token, extracts `tenant_id`
3. Request forwarded with `X-Tenant-ID` header
4. Tenant middleware sets DB schema: `SET search_path TO tenant_{id}`
5. All queries automatically scoped to tenant schema
6. File operations use tenant-specific S3 prefix
7. Cache keys namespaced with `tenant_id`

### 7.3 Event-Driven Integration (Key Flows)

| Trigger Event | Source Service | Target Service | Action |
|---|---|---|---|
| Document Approved | `document-service` | `training-service` | Auto-assign training for affected personnel |
| Document Approved | `document-service` | `notification-service` | Notify owner and distribution list |
| Quality Event Created (Critical) | `quality-event-service` | `capa-service` | Auto-create CAPA |
| Audit Finding Created | `audit-service` | `capa-service` | Create CAPA from major/minor NC findings |
| Calibration Failed | `equipment-service` | `quality-event-service` | Create non-conformance |
| Environmental Excursion | `envmon-service` | `quality-event-service` | Create deviation |
| PT Result Unsatisfactory | `proficiency-testing-service` | `capa-service` | Initiate CAPA |
| CAPA Overdue | `capa-service` | `notification-service` | Escalate to management |
| Training Overdue | `training-service` | `notification-service` | Alert employee and supervisor |

### 7.4 Security Summary

| Control | Implementation |
|---|---|
| Encryption at rest | AES-256 via AWS KMS; per-tenant keys for Enterprise |
| Encryption in transit | TLS 1.3 everywhere |
| Authentication | Keycloak (password + MFA); SAML/OIDC for enterprise SSO |
| Authorization | RBAC at API gateway + service level; resource-level permissions |
| Audit trail | Append-only PostgreSQL; no UPDATE/DELETE on audit records |
| Electronic signatures | 21 CFR Part 11 compliant: user ID + password verification; signature meaning declaration; timestamp; cryptographic link to record |
| Network | AWS WAF, VPC private subnets, mutual TLS between services (Istio) |

### 7.5 Availability & Disaster Recovery

| Metric | Standard Tier | Enterprise Tier |
|---|---|---|
| Uptime SLA | 99.9% | 99.95% |
| RPO | 1 hour | 15 minutes |
| RTO | 4 hours | 1 hour |
| Backup Frequency | Daily full + hourly incremental | Same |
| Geo-Redundancy | Multi-AZ within region | Cross-region replication |

### 7.6 Performance Targets

| Metric | Target |
|---|---|
| Page load time | < 2 seconds |
| API response time (95th percentile) | < 500ms |
| Search response time | < 1 second |
| Concurrent users per tenant | 100+ (Full platform); 50 (MVP) |
| Report generation | < 10 seconds |

### 7.7 Scalability Limits

| Dimension | Limit |
|---|---|
| Concurrent tenants | 1,000+ |
| Users per tenant | Up to 1,000 |
| Documents per tenant | Up to 100,000 |
| Quality records per tenant | Up to 10 million |
| Storage per tenant | Up to 1TB (expandable) |

---

## 8. Compliance & Regulatory Framework

### 8.1 Standards Coverage

| Standard | Scope | Coverage |
|---|---|---|
| **ISO/IEC 17025:2017** | Testing & Calibration Laboratories | Full clause-by-clause mapping |
| **ISO 15189:2022** | Medical/Clinical Laboratories | Full clause-by-clause mapping |
| **ISO 9001:2015** | General Quality Management | Full support |
| **FDA 21 CFR Part 11** | Electronic Records & Signatures | Native compliance |
| **GLP** | Good Laboratory Practice | Workflow support |
| **GMP** | Good Manufacturing Practice | Workflow support |
| **CLIA** | Clinical Lab Improvement Amendments | Applicable controls |
| **EPA Methods** | Environmental Testing | Template-based support |
| **NABL** | Indian Laboratory Accreditation | Full support |
| **A2LA / ANAB / UKAS** | Accreditation Bodies | Assessment workflow support |
| **GDPR** | Data Protection (EU) | Built-in at launch |
| **HIPAA** | Health Data (US Clinical) | Planned for Year 2 |

### 8.2 ISO 17025:2017 Module Mapping (Key Clauses)

| ISO 17025 Clause | Requirement | RainerQMS Module |
|---|---|---|
| 4.1 | Impartiality | Risk Management (dedicated impartiality risk register) |
| 4.2 | Confidentiality | Platform Services (RBAC, encryption, audit trails) |
| 6.2 | Personnel | Training & Competency |
| 6.3 | Facilities & Environmental Conditions | Environmental Monitoring |
| 6.4 | Equipment | Equipment & Calibration |
| 6.5 | Metrological Traceability | Equipment & Calibration (traceability chain, CRM tracking) |
| 6.6 | Externally Provided Products & Services | Supplier Management |
| 7.7 | Ensuring Validity of Results | Proficiency Testing, Control Charts |
| 7.9 | Complaints | Customer Complaints |
| 7.10 | Nonconforming Work | Quality Events (dedicated NC work workflow) |
| 8.3 | Control of Management System Documents | Document Control |
| 8.4 | Control of Records | Document Control + Platform |
| 8.5 | Actions to Address Risks & Opportunities | Risk Management |
| 8.7 | Corrective Actions | CAPA Management |
| 8.8 | Internal Audits | Audit Management |
| 8.9 | Management Reviews | Management Review |

### 8.3 ALCOA+ Data Integrity Compliance

| Principle | System Enforcement |
|---|---|
| **Attributable** | Every record linked to creating user; timestamps; e-signatures |
| **Legible** | Structured electronic forms; no handwritten entries; PDF archival |
| **Contemporaneous** | Real-time data entry enforcement; timestamp validation; late entry flagging |
| **Original** | First-entry data preserved; no overwriting; all changes tracked |
| **Accurate** | Input validation; range checks; calculation verification; review workflows |
| **Complete** | Required field enforcement; workflow gates prevent partial records |
| **Consistent** | Controlled vocabularies; pick-lists; form templates |
| **Enduring** | Cloud storage; automated backups; configurable retention; disaster recovery |
| **Available** | Role-based access; search; reporting; API access |

### 8.4 FDA 21 CFR Part 11 Electronic Signatures

Every electronic signature in RainerQMS captures:
- Signer name
- Date and time (UTC, server-generated)
- Signature meaning (e.g., "Approved," "Reviewed," "Authored")
- Identity verification (user ID + password re-entry)
- Cryptographic link to the signed record (cannot be excised, copied, or transferred)

---

## 9. Pricing Tiers

### 9.1 Model

- **Per-user, per-month** pricing billed annually (default) or monthly
- Full Users (create/edit/approve) at standard rate; Read-Only Users at 50% discount
- 20% discount for annual prepayment

### 9.2 Tier Comparison

| | **Starter** | **Professional** | **Enterprise** |
|---|---|---|---|
| **Target** | Small labs (5–25 users) | Mid-size labs (10–100 users) | Large labs & networks (25–1000+) |
| **Full User Price** | $50/user/month (annual) | $100/user/month (annual) | $150–$200/user/month (custom) |
| **Min. Annual Commitment** | $3,000 | $12,000 | $45,000 |
| **Document Storage** | 10 GB | 100 GB | Unlimited |
| **Sites** | 1 | Up to 3 | Unlimited |
| **Custom Workflows** | 3 | Unlimited | Unlimited |
| **AI Features** | ❌ | ✅ Trend detection, summarization, exam gen | ✅ + Predictive CAPA, root cause suggestion |
| **SSO** | ❌ | ✅ | ✅ |
| **API Access** | ❌ | ✅ REST API | ✅ REST + GraphQL |
| **LIMS Integration** | ❌ | ✅ 1 connector | ✅ Multiple connectors |
| **ERP Integration** | ❌ | ❌ | ✅ |
| **Multi-Site Management** | ❌ | ❌ | ✅ Centralized admin |
| **Support** | Standard (email, KB) | Priority (email, chat, phone) | Dedicated CSM + SLA |
| **Validation Package** | ❌ | ❌ | ✅ IQ/OQ/PQ tools |

---

## 10. Development Roadmap

### 10.1 Phase Summary

| Phase | Timeline | Focus | Key Deliverables |
|---|---|---|---|
| **Phase 0: Foundation** | Months 1–2 | Infrastructure, auth, multi-tenancy, platform services | AWS/EKS infrastructure, Auth Service (Keycloak), Tenant Service, API Gateway, Notification Service, File Service, Audit Trail, E-Signature Module, RBAC, Frontend Shell |
| **Phase 1: MVP Core** | Months 3–6 | 6 core QMS modules for pilot customers | Document Control, Quality Events, CAPA, Training, Audit Management, Equipment & Calibration, Dashboards, ISO 17025 templates |
| **Phase 2: Extended Modules** | Months 7–12 | Remaining modules + integrations | Environmental Monitoring, Supplier, Risk, PT, Complaints, Management Review, Method Validation, Measurement Uncertainty, Control Charts, Microbiology/Chemistry features, SSO, Public REST API, LIMS connector |
| **Phase 3: Intelligence & Scale** | Months 13–18 | AI features + enterprise capabilities | AI Trend Detection, Document Summarization, Exam Generation, Root Cause Suggestion, Predictive Analytics, Multi-Site Management, IoT Integration, SOC 2 Type II certification |
| **Phase 4: Market Leadership** | Months 19–24 | Advanced features + global expansion | Offline Mode (PWA), Industry Editions, Marketplace, Academy, Advanced Workflow Engine, Supplier Portal, Client Portal, ISO 27001, geographic expansion (India, EU, APAC, LATAM) |

### 10.2 MVP Scope (Phase 1 — 6 Months)

**In Scope (MVP):**
- Document Control (with ISO 17025 templates)
- Quality Event Management
- CAPA Management
- Training & Competency
- Audit Management
- Equipment & Calibration
- Reporting & Dashboards
- Platform Services (Auth, Tenancy, Audit Trail, E-Signatures, RBAC, Notifications, File Storage, Search)

**Explicitly Out of Scope for MVP:**
Environmental Monitoring, Supplier Management, Risk Management (formal), Proficiency Testing, Customer Complaints (formal), Management Review automation, Method Validation, Measurement Uncertainty, Control Charts, Microbiology-specific features, AI features, SSO, Public REST API, LIMS integration, Multi-site management, Offline mode, Multi-language, Custom workflow builder

### 10.3 MVP Success Criteria

| Criterion | Target |
|---|---|
| Pilot labs actively using system | 5 of 5–10 pilots |
| Weekly active users per pilot | > 60% of registered users |
| End-to-end workflow functional | Document → Approve → Train → Deviation → CAPA → Close |
| Accreditation readiness | At least 1 pilot lab assessed using RainerQMS |
| 21 CFR Part 11 compliance | 100% compliant (e-signatures + audit trails) |
| Customer NPS | > 40 |
| Conversion intent | > 60% of pilots willing to convert to paid |

---

## 11. Gaps & Missing Information

### 11.1 Documented Gaps

| # | Gap | Description | Severity |
|---|---|---|---|
| G-01 | ⚠️ **Method Validation Module — Workflow Not Detailed** | The lab-specific features doc lists extensive Method Validation fields and parameters, but no end-to-end workflow (trigger, steps, roles, end state) is documented. Referenced in Phase 2 delivery but not described as a workflow. | High |
| G-02 | ⚠️ **Measurement Uncertainty — No Workflow Defined** | The Measurement Uncertainty feature is described at a field/feature level (GUM methodology, budget calculator, components) but the workflow for creating, reviewing, and updating an uncertainty budget is not defined. | Medium |
| G-03 | ⚠️ **Control Chart / QC Sample Workflow — Not Described** | Control charts (Shewhart, CUSUM, EWMA, Westgard rules) are listed as features but the workflow for setting up QC monitoring, responding to OOC results, and linking to quality events is not documented beyond brief feature descriptions. | Medium |
| G-04 | ⚠️ **Microbiology Lab Workflows — Not Described** | Extensive microbiology-specific features are listed (media prep, culture collection, sterility testing, etc.) but none have explicit end-to-end workflows with steps, roles, and outcomes. | Medium |
| G-05 | ⚠️ **Chemistry Lab Workflows — Not Described** | Chemistry features (CRM management, HPLC/GC/ICP workflows, balance management) are listed as features but end-to-end workflows are absent. | Medium |
| G-06 | ⚠️ **Scope of Accreditation Management — No Workflow** | Listed as a feature (scope registry, extension tracking, flexible scope, certificate tracking, accreditation body communication) but no workflow is defined. | Low |
| G-07 | ⚠️ **Onboarding Workflow Not Documented** | Phase 1 deliverables include an "Onboarding Wizard" but the onboarding process for new tenants (who does what, in what order) is not described in the business documentation. | Medium |
| G-08 | ⚠️ **Personnel Monitoring / Aseptic Technique Assessment Workflow** | Listed as a feature under microbiology lab features but no workflow is defined. | Low |
| G-09 | ⚠️ **GLP Study Performance Workflow** | GLP support mentions "study plan management, protocol deviation tracking, amendment workflows" but no detailed GLP study lifecycle workflow is documented. | Medium |
| G-10 | ⚠️ **Calibration Laboratory Certificate Workflow** | Calibration lab features (as-found/as-left, guard banding, recall management, out-of-tolerance impact) are described but a full calibration service certificate generation and delivery workflow for customer instruments is not detailed. | Medium |

### 11.2 Role/Permission Ambiguities

| # | Ambiguity | Detail |
|---|---|---|
| R-01 | ⚠️ **"Auditor" Role Permissions on Non-Audit Modules** | The Auditor role is described as having "read access to audited areas" but the exact boundaries (e.g., can an auditor read CAPAs they didn't create? All documents?) are not explicitly defined. |
| R-02 | ⚠️ **Section Head Cross-Section Access** | Section Heads have "read access to related sections" but "related" is not defined — this could mean adjacent sections, all sections, or only sections they interact with. |
| R-03 | ⚠️ **Analyst Write Permissions on Equipment** | Analysts can "log instrument use" but it is unclear whether they can create maintenance records, initiate calibration requests, or only add to the usage logbook. |
| R-04 | ⚠️ **Viewer Role Scope** | The Viewer role is described as having "access to specified modules" but who specifies which modules a Viewer can access (Tenant Admin? Quality Manager?) is not documented. |

### 11.3 Services Mentioned But Not Fully Explained

| # | Service/Feature | Issue |
|---|---|---|
| S-01 | ⚠️ **`workflow-engine` (Temporal)** | Listed in service catalog and tech stack but no documentation on how non-technical users configure workflows via the "no-code workflow designer." Deferred to Phase 2 but no design exists. |
| S-02 | ⚠️ **`search-service` Cross-Module Search** | Full-text search within documents is in MVP; "cross-module search" is listed as Phase 2 but no specification on what entities are indexed or how results are ranked. |
| S-03 | ⚠️ **AI Root Cause Suggestion** | Referenced as a feature but no description of the training data requirements, how suggestions are presented, or how accuracy is validated. |
| S-04 | ⚠️ **Cross-Tenant Benchmarking** | Mentioned as an opt-in analytics feature but data anonymization methodology, consent mechanism, and data governance are not described. |
| S-05 | ⚠️ **RainerQMS Marketplace** | Listed as a Phase 4 deliverable with no specification on governance, revenue model, or certification process for third-party connectors. |
| S-06 | ⚠️ **RainerQMS Academy** | Listed as Phase 4 but no description of content, delivery model, certification program, or whether it is included in pricing or a separate product. |
| S-07 | ⚠️ **Supplier Portal** | Listed as a Phase 4 feature (self-service portal for suppliers) but no description of the registration process, data scope visible to suppliers, or authentication model for external parties. |
| S-08 | ⚠️ **Client Portal** | Listed as Phase 4 (self-service portal for lab clients to submit samples, track status, view reports, file complaints) but security, data access boundaries, and provisioning are not described. |

### 11.4 Competitor Analysis & GTM Sections

> The documentation includes sections on competitor analysis (`02-competitor-analysis/`), go-to-market strategy (`03-gtm-strategy/`), and revenue projections (`04-pricing-strategy/`). These sections are **not included in this master document** as they cover business strategy rather than system behavior. They are available in the source documentation for reference.

---

*End of RainerQMS Master Documentation*

*Document synthesized from: README.md, 01-product-vision-and-overview.md, 02-target-market-and-user-personas.md, 03-core-modules-and-features.md, 04-laboratory-specific-features.md, 05-compliance-and-regulatory-framework.md, 06-multi-tenant-architecture-overview.md, 07-integration-and-interoperability.md, 08-user-workflows-and-processes.md, 09-business-requirements-document.md, 01-technical-architecture.md, 02-phased-development-roadmap.md, 03-mvp-scope-and-definition.md, 04-technology-stack.md, 01-pricing-model-and-tiers.md*
