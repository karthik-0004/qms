# RainerQMS — Module-by-Module Workflow Walkthrough

> **Document Purpose:** A practical, step-by-step walkthrough of every RainerQMS module written for someone with **zero prior QMS knowledge**. For each module, this document answers four questions in plain language:
>
> 1. **What is this module for?** (in one paragraph)
> 2. **Who are the people involved?** (roles + what each one does)
> 3. **What information does the system store?** (fields the user sees on screen)
> 4. **What is the step-by-step workflow?** (who does what, in order, like a movie script)
>
> Read this end-to-end and you will understand how the entire RainerQMS works, who does what, and what the screens look like.
>
> **Sources:** RainerQMS Master Documentation (spec) + MasterControl UI patterns + industry references (FreeQMS, TrackWise) for capabilities the spec omits.

---

## Table of Contents

1. [How to read this document](#how-to-read-this-document)
2. [The cast of characters (roles)](#the-cast-of-characters-roles)
3. [Module 1 — Document Control](#module-1--document-control)
4. [Module 2 — Quality Event Management](#module-2--quality-event-management)
5. [Module 3 — CAPA Management](#module-3--capa-management)
6. [Module 4 — Audit Management](#module-4--audit-management)
7. [Module 5 — Training & Competency](#module-5--training--competency)
8. [Module 6 — Equipment & Calibration](#module-6--equipment--calibration)
9. [Module 7 — Environmental Monitoring](#module-7--environmental-monitoring)
10. [Module 8 — Supplier Quality](#module-8--supplier-quality)
11. [Module 9 — Risk Management](#module-9--risk-management)
12. [Module 10 — Proficiency Testing (PT)](#module-10--proficiency-testing-pt)
13. [Module 11 — Customer Complaint Management](#module-11--customer-complaint-management)
14. [Module 12 — Management Review](#module-12--management-review)
15. [Module 13 — Reporting & Analytics](#module-13--reporting--analytics)
16. [Module 14 — Lab-Specific Features](#module-14--lab-specific-features)
17. [The big picture — how the modules talk to each other](#the-big-picture--how-the-modules-talk-to-each-other)

---

## How to read this document

Each module follows the **same 4-part structure**. Think of it like reading a recipe.

### The 4 parts of every module

| Part | What's in it |
|---|---|
| **1. Purpose** | One paragraph: why this module exists |
| **2. Roles involved** | Who does what — like a movie cast list |
| **3. Fields on the screen** | What the user types or picks (you can imagine the form layout) |
| **4. Step-by-step workflow** | Numbered actions: "User clicks X → system does Y → notifies Z" |

### The attendance analogy you used

Just like:
- Employee logs in → opens Attendance page → clicks "Mark Present" → system stamps date+time → manager sees it on dashboard

…every QMS workflow follows the same pattern: **someone does an action → system records it → next person gets notified → they do their action → repeat until done.**

---

## The cast of characters (roles)

Before diving into modules, here is the cast. Every workflow uses some subset of these 8 roles.

| Role | Real-life equivalent | What they do in the system |
|---|---|---|
| **Tenant Admin** | IT Manager of the lab company | Sets up the system, creates user accounts, configures the company's settings |
| **Quality Manager (QM)** | Head of Quality Department | The "boss" of quality — approves everything important, closes CAPAs, owns audits |
| **Lab Director** | Senior leader / Lab Head | Views high-level dashboards, approves company-wide policies, attends Management Reviews |
| **Section Head** | Team Leader (e.g. head of Microbiology team) | Approves things for their team, assigns training, runs audits within their area |
| **Analyst / Technician** | Lab employee who runs tests | Logs equipment use, reports problems, completes training, follows SOPs |
| **Auditor** | Internal or external inspector | Plans audits, executes checklists, records findings, writes reports |
| **Viewer** | Read-only user (e.g. client, intern) | Can only view certain screens, cannot edit or approve anything |
| **API User** | Software integration (e.g. LIMS) | A "robot" account that other software uses to send/receive data |

### How a person logs in (every module)

Every action below starts with this same flow:

1. User opens browser → goes to RainerQMS URL → enters email + password → (if enabled) enters MFA code from phone
2. System checks credentials → issues JWT token → loads the user's **personal dashboard** ("My RainerQMS")
3. Dashboard shows tiles: **My Tasks**, **My Recent**, **My Training Folder**, **My Subscriptions**, **Analytics**, **Start Task**, etc.
4. From here, the user clicks into whichever module they need.

This "login → dashboard → click into module" sequence is implicit in every workflow below. The workflows pick up from the point the user has already opened the module.

---

## Module 1 — Document Control

### 1.1 Purpose (in one paragraph)

This module is the **single source of truth for every controlled document in the lab** — SOPs (Standard Operating Procedures), Work Instructions, Test Methods, Policies, Forms, Manuals. It makes sure every employee reads the **latest approved version** of each document, that every change is reviewed and signed off properly, and that there is a complete history of every edit (who changed what, when, and why) — required for ISO 17025 and FDA 21 CFR Part 11 audits.

### 1.2 Roles involved

| Role | What they do in this module |
|---|---|
| **Author** (usually Section Head or Analyst) | Writes a new document or proposes a revision |
| **Reviewer** (Section Head, peer expert) | Reads the draft, suggests changes or approves |
| **Approver** (Quality Manager, sometimes Lab Director for policies) | Final sign-off with electronic signature |
| **Distribution List Members** (any employees affected) | Receive the new document and must acknowledge they've read it |
| **Document Owner** (Section Head) | Responsible for keeping the document up to date; gets reminders to review it periodically |
| **Quality Manager** | Oversees the whole document control program |

### 1.3 Fields on the screen (what the user sees)

When you open a document record, you see these fields:

| Field | Example value | What it means |
|---|---|---|
| Document Number | SOP-0001 | Unique ID |
| Title | "Labeling Procedure for Finished Goods" | Document name |
| Type | SOP / Work Instruction / Method / Policy / Form / Manual | Category |
| Status | Draft / Under Review / Approved / Effective / Superseded / Obsolete | Where in the lifecycle |
| Version | 2.0 | Version number |
| Revision | Rev 04 | Revision letter |
| Effective Date | 26 Mar 2026 | Date document goes live |
| Review Due Date | 26 Mar 2027 | Next periodic review |
| Owner | Rajesh Patel (Section Head, Microbiology) | Who maintains it |
| Approver(s) | Dr. Priya Sharma (QM) | Who must sign off |
| Distribution List | All Microbiology team (8 users) | Who must acknowledge |
| Vault | QA-Released | Storage zone |
| Folder / Taxonomy | Documents by Department > Microbiology | Where it sits in the file tree |
| Main File | Labeling.docx (uploaded) | The actual content |
| Change Summary | "Updated to align with revised ISO 17025 Clause 8.3" | What changed in this version |
| ISO Clause Mapping | 8.3.2 | Which regulation it satisfies |

### 1.4 Step-by-step workflow

**Trigger:** A new SOP is needed, OR an existing SOP needs revision, OR periodic review is due, OR a CAPA requires a document change.

#### Step 1 — Author creates a new document

- **Who:** Rajesh (Section Head, Microbiology)
- **Action:** Logs in → clicks **Documents** in left nav → clicks **Start Task → New Document**
- **What he fills in:** Title, Type (SOP), Folder (Microbiology), uploads the draft .docx file, enters Change Summary, picks Approver (Dr. Priya), picks Distribution List (his team)
- **What the system does:** Auto-generates Document Number `SOP-MICRO-0042`, sets Status = `Draft`, sets Version = `1.0`, sends an email **only to Rajesh** confirming creation

#### Step 2 — Author submits for review

- **Who:** Rajesh
- **Action:** From the document page, clicks **Submit for Review** button
- **What the system does:**
  - Status changes from `Draft` → `Under Review`
  - System looks up the reviewers (e.g. another senior microbiologist) and **sends them an email + in-app notification:** "You have a new document to review: SOP-MICRO-0042. Due: 7 days from now"
  - The reviewers see this in **My Tasks** on their dashboard

#### Step 3 — Reviewer reviews

- **Who:** Senior microbiology peer
- **Action:** Logs in → My Tasks → clicks the task → opens the document → reads it → either:
  - **Option A:** Clicks **Approve Review** → adds comment "Looks good" → submits
  - **Option B:** Clicks **Request Changes** → adds comment "Section 4.2 needs more detail" → submits
- **What the system does:**
  - **Option A:** Records reviewer's e-signature; if all reviewers have approved, the document moves to Approver stage. **Sends Dr. Priya an email:** "SOP-MICRO-0042 is ready for your approval"
  - **Option B:** Status changes back to `Draft`. **Sends Rajesh an email:** "Reviewer requested changes — see comments"

#### Step 4 — Approver approves (the big sign-off)

- **Who:** Dr. Priya (Quality Manager)
- **Action:** Logs in → My Tasks → clicks the task → reads the document one final time → clicks **Approve** button
- **What the system does:**
  - Prompts Dr. Priya to **re-enter her password** (this is the 21 CFR Part 11 requirement)
  - Asks her to **declare the meaning of her signature** ("I, Dr. Priya, approve this document as Quality Manager on 15 May 2026 14:32 UTC")
  - Creates a **cryptographic hash** linking her signature to this exact document version (so it can never be moved to another document)
  - Status changes from `Under Review` → `Approved`

#### Step 5 — Document becomes Effective

- **Who:** System (automatic)
- **Action:**
  - Status changes from `Approved` → `Effective` on the effective date
  - Previous version (if any) of SOP-MICRO-0042 is auto-marked `Superseded`
  - System **publishes an event on the event bus:** `Document.Effective(SOP-MICRO-0042, v2.0)`
- **What happens next:** Two other modules listen to this event…

#### Step 6 — Training auto-triggers (THIS IS THE MAGIC)

- **Who:** Training Service (automatic, see Module 5)
- **Action:** Hears the `Document.Effective` event → looks up who is on the Distribution List for SOP-MICRO-0042 (Rajesh's 8-person team) → creates **8 training assignments** automatically
- **What the team sees:** Each of the 8 team members receives an email: "New training assigned: Read and acknowledge SOP-MICRO-0042 v2.0. Due in 14 days."

#### Step 7 — Each team member acknowledges

- **Who:** Each Analyst / Technician (e.g. David)
- **Action:** Logs in → My Tasks → clicks "Read SOP-MICRO-0042" → reads document on screen → clicks **Take Exam** (if exam attached) → passes → clicks **Sign Off** → re-enters password
- **What the system does:** Records David's acknowledgment with e-signature + timestamp; updates the Training compliance dashboard

#### Step 8 — Periodic review reminder (one year later)

- **Who:** System (automatic)
- **Action:** 30 days before `review_due_date`, sends Rajesh an email: "SOP-MICRO-0042 is due for review on 26 Mar 2027. Click here to confirm it's still current OR initiate a revision."
- **Rajesh's options:**
  - **Confirm current** → next review date pushed forward 1 year
  - **Initiate revision** → starts a new cycle at Step 1 above

### 1.5 What the user sees on screen (UI layout)

```
┌─────────────────────────────────────────────────────────────────┐
│  My RainerQMS    [Search...]                    Rajesh Patel ▼  │
├──────┬──────────────────────────────────────────────────────────┤
│      │  Documents > Explorer                                     │
│ 📋   │                                                           │
│ Docs │  📁 Documents by Department                              │
│ ────│    📁 Microbiology                                        │
│ 🎓   │      📄 SOP-MICRO-0042 - Labeling Procedure (v2.0)  ⭐   │
│ Trng │      📄 SOP-MICRO-0041 - Media Prep                      │
│ ────│      📄 SOP-MICRO-0040 - Sterility Testing                │
│ 🔍   │    📁 Chemistry                                          │
│ Audit│    📁 Calibration Lab                                    │
│ ────│                                                           │
│ ⚠️   │  [+ New Document]  [Search Filter]                       │
│ CAPA │                                                           │
└──────┴──────────────────────────────────────────────────────────┘
```

When you click on `SOP-MICRO-0042`:

```
┌─────────────────────────────────────────────────────────────────┐
│  SOP-MICRO-0042 - Labeling Procedure         Status: Effective  │
├─────────────────────────────────────────────────────────────────┤
│  Info | Training | Controlled Copies | History | Versions       │
├─────────────────────────────────────────────────────────────────┤
│  Document Number: SOP-MICRO-0042    Version: 2.0    Rev: 04    │
│  Title: Labeling Procedure for Finished Goods                   │
│  Effective Date: 26 Mar 2026     Review Due: 26 Mar 2027        │
│  Owner: Rajesh Patel                                            │
│  Main File: Labeling.docx  [Download] [View] [Link]            │
│                                                                  │
│  Distribution List (8):  ✅ Acknowledged: 6   ⏳ Pending: 2     │
│                                                                  │
│  [Initiate Revision]  [Add to Favorites]  [Print]              │
└─────────────────────────────────────────────────────────────────┘
```

---

## Module 2 — Quality Event Management

### 2.1 Purpose (in one paragraph)

This module is the **"something went wrong, let's report it" system**. Whenever an analyst notices a problem — a test result outside acceptable range, equipment failure, a procedural deviation, contamination of a sample — they file a Quality Event. The system classifies how serious it is, triggers investigation, and decides whether it's a one-off (just fix it) or a systemic issue (escalate to CAPA — Module 3).

### 2.2 Roles involved

| Role | What they do in this module |
|---|---|
| **Reporter** (any Analyst, Section Head) | Notices the problem and files the report |
| **Section Head** | Decides immediate action (halt work? quarantine sample?) |
| **Investigator** (Section Head or designated person) | Digs into root cause |
| **Quality Manager** | Reviews findings, decides if it escalates to CAPA |
| **Affected Personnel** | People whose work might be impacted (e.g. analysts who used the failed equipment) |
| **Client** (external) | If reported test results were affected, the client must be notified |

### 2.3 Fields on the screen

When you open the Quality Event form, you see:

| Field | Example value |
|---|---|
| Event ID | QE-2026-0037 |
| Event Type | Deviation / Non-Conformance / Non-Conforming Work / OOS (Out-of-Spec) / OOT (Out-of-Tolerance) |
| Severity | Critical / Major / Minor |
| Description | "pH meter reading drifted 0.3 units mid-run on Sample S-2026-1144" |
| Date Discovered | 15 May 2026, 11:42 |
| Area | Microbiology Lab Room 3 |
| Linked Equipment | EQ-2018-0021 (pH Meter Mettler Toledo) |
| Linked Document | SOP-MICRO-0042 v2.0 |
| Linked Personnel | David Okonkwo (the analyst running the test) |
| Immediate Action Taken | "Sample re-run with backup pH meter; suspect meter taken out of service" |
| Status | Open / Under Investigation / CAPA Created / Closed |
| Root Cause | (filled in later) "Electrode reached end of life — replacement was 3 weeks overdue" |
| CAPA Reference | (filled in later) CAPA-2026-0018 |
| Client Notified | Yes / No / N/A |

### 2.4 Step-by-step workflow

**Trigger:** An analyst notices a problem during their work.

#### Step 1 — Analyst reports the event

- **Who:** David (Analyst)
- **Action:** Logs in → clicks **Quality Events** in left nav → clicks **+ Report Event**
- **What he fills in:** Description, Event Type (OOS), Severity (Major), Area, Linked Equipment, Date Discovered, Immediate Action
- **What the system does:** Generates Event ID `QE-2026-0037`, status = `Open`, **sends notification to David's Section Head + Quality Manager** within 5 minutes

#### Step 2 — Section Head decides immediate action

- **Who:** Rajesh (Section Head)
- **Action:** Sees notification → opens event → reviews → either:
  - Halts further work until investigation done
  - Quarantines affected samples
  - Authorizes work to continue with backup equipment
- **What the system does:** Records his decision in the event record with e-signature

#### Step 3 — Quality Manager triages severity

- **Who:** Dr. Priya (QM)
- **Action:** Reviews event → confirms or changes severity classification
- **System logic:** If Severity = **Critical**, system **automatically creates a CAPA** (jumps to Module 3). If Major or Minor, investigation proceeds locally first.

#### Step 4 — Investigator does root cause analysis

- **Who:** Investigator (often the Section Head)
- **Action:** Opens event → clicks **Start Investigation** → uses built-in tools:
  - **5-Why analysis** — keeps asking "why?" 5 times to drill to root cause
  - **Fishbone diagram** — categories: Machine, Method, Material, Man, Measurement, Environment
  - **Fault Tree** — for complex multi-cause events
  - **Pareto chart** — for recurring patterns
- **What he fills in:** Root cause text, evidence (uploaded photos, data files)

#### Step 5 — Quality Manager reviews the investigation

- **Who:** Dr. Priya
- **Action:** Reads investigation → either:
  - **Approves** root cause → decides if CAPA is needed
  - **Sends back** for more investigation

#### Step 6 — Decision: escalate to CAPA or close locally

- **Who:** Dr. Priya
- **Decision logic:**
  - **One-off issue, root cause addressed locally** → Close event
  - **Could happen again, systemic issue** → Click **Escalate to CAPA** → jumps to Module 3
- **What the system does on escalate:** Creates CAPA record, copies event details, links the two records bi-directionally

#### Step 7 — Client notification (if applicable)

- **Who:** Quality Manager
- **Action:** If reported test results were affected, draft and send client notification → uploads acknowledgment receipt → checks `client_notified = Yes`

#### Step 8 — Close the event

- **Who:** Quality Manager (with e-signature)
- **Action:** Clicks **Close Event** → status changes to `Closed`
- **System events:** Event data feeds into trend analysis dashboards; if CAPA is open, event remains linked until CAPA closure

### 2.5 Cross-module connection

This module **talks to**: CAPA (escalation), Equipment (linked equipment), Document Control (linked SOP/method), Training (if competence issue), Audit (event becomes an audit input).

---

## Module 3 — CAPA Management

### 3.1 Purpose (in one paragraph)

CAPA stands for **Corrective Action / Preventive Action**. When a Quality Event reveals a systemic problem, CAPA is the "let's actually fix it permanently and make sure it doesn't happen again" workflow. It forces the lab to: (1) understand the root cause, (2) plan specific actions with owners and deadlines, (3) implement those actions, (4) verify after 30/60/90 days that the fix worked. Required by ISO 17025 Clause 8.7 and FDA regulations.

### 3.2 Roles involved

| Role | What they do |
|---|---|
| **CAPA Initiator** | Person who triggers the CAPA (often from a Quality Event, audit finding, or complaint) |
| **CAPA Owner** | The "project manager" of the CAPA — accountable for getting it closed |
| **Action Owners** | People assigned individual action items (could be multiple) |
| **Investigators** | Team doing the root cause analysis |
| **Quality Manager** | Approves the investigation, action plan, and closure |
| **Effectiveness Reviewer** | Person who checks at 30/60/90 days if the fix worked |

### 3.3 Fields on the screen

| Field | Example value |
|---|---|
| CAPA ID | CAPA-2026-0018 |
| CAPA Type | Corrective / Preventive / Both |
| Source Type | Quality Event / Audit Finding / Complaint / PT Result / Management Review / Standalone |
| Source ID | QE-2026-0037 |
| Owner | Dr. Priya Sharma |
| Risk Severity | 1 (Low) – 5 (Critical) → e.g. 4 |
| Risk Occurrence | 1 – 5 → e.g. 3 |
| Risk Detectability | 1 – 5 → e.g. 2 |
| RPN (auto-calculated) | 4 × 3 × 2 = **24** |
| Root Cause | "Calibration interval too long for high-use pH meter" |
| RCA Tool Used | 5-Why |
| Actions[] | (multiple action items, see below) |
| Status | Identification / Investigation / Action Planning / Implementation / Effectiveness Check / Closed |
| Effectiveness Check Date | 14 Aug 2026 (90 days post-implementation) |
| Effectiveness Result | (filled later) Pass / Fail |
| Closed Date | (filled later) |

**Action item sub-fields:**

| Field | Example |
|---|---|
| Action ID | ACT-2026-0048 |
| Action Type | Corrective / Preventive |
| Description | "Shorten calibration interval for high-use pH meters from 6 months to 3 months" |
| Owner | Rajesh Patel |
| Due Date | 15 Jun 2026 |
| Expected Outcome | "Calibration drift detected before causing OOS" |
| Status | Pending / In Progress / Complete / Overdue |
| Evidence | (uploaded files when complete) |
| Sign-off | Action owner's e-signature on completion |

### 3.4 Step-by-step workflow

**Trigger:** Quality Event escalation OR audit finding (Major/Minor NC) OR complaint OR PT unsatisfactory result OR Management Review decision OR standalone initiation.

#### Step 1 — Identification

- **Who:** System (automatic if escalated from QE) OR Quality Manager (manual)
- **What happens:** CAPA-2026-0018 record created, source event linked, owner assigned (usually Dr. Priya), risk severity/occurrence/detectability scored. **Email sent to CAPA Owner:** "New CAPA assigned to you."

#### Step 2 — Investigation

- **Who:** CAPA Owner + investigation team
- **Action:** Opens CAPA → clicks **Start Investigation** → assembles team → collects data → uses RCA tools (5-Why, Fishbone, etc.) → AI may suggest probable causes based on historical similar events → documents root cause with evidence
- **What the system does:** Status → `Investigation`; saves all RCA tool outputs

#### Step 3 — Action Planning

- **Who:** CAPA Owner + Quality Manager
- **Action:** For each root cause, defines specific actions. Each action gets:
  - A clear description ("Shorten cal interval...")
  - An owner (Rajesh)
  - A due date
  - An expected outcome
  - Optional: impact assessment on existing documents/training/processes
- **What the system does:** Status → `Action Planning`; creates one record per action; **emails each action owner:** "You have a new action assigned. Due: [date]"

#### Step 4 — Quality Manager approves the plan

- **Who:** Dr. Priya
- **Action:** Reviews action plan → clicks **Approve Plan** → e-signs
- **What the system does:** Status → `Implementation`; locks the action list (no further changes without QM re-approval)

#### Step 5 — Action owners execute their actions

- **Who:** Each Action Owner (e.g. Rajesh for ACT-2026-0048)
- **Action:** Does the work → opens action record → uploads evidence (e.g. updated SOP, calibration schedule screenshot) → clicks **Mark Complete** → e-signs
- **What happens automatically:**
  - If an action requires a **document change**, a document workflow auto-initiates in Module 1
  - If an action requires **retraining**, a training task auto-creates in Module 5
- **What the system does:** Action status → `Complete`; once **all** actions complete, CAPA status → `Effectiveness Check`

#### Step 6 — Effectiveness Verification (the key step)

- **Who:** Effectiveness Reviewer (often the Quality Manager or a peer)
- **When:** Scheduled at 30 days, 60 days, and 90 days post-implementation
- **What they check:**
  - Has the problem recurred?
  - Have the relevant metrics improved (e.g. number of OOS events)?
  - Are the actions actually sustained (e.g. is the new shorter calibration interval being followed)?
- **Outcome:**
  - **Effective** → proceed to Closure (Step 7)
  - **Not effective** → CAPA returns to Investigation or Action Planning; new actions defined

#### Step 7 — Closure

- **Who:** Quality Manager
- **Action:** Writes final summary → clicks **Close CAPA** → re-enters password → e-signs with "I close this CAPA as effective"
- **What the system does:** Status → `Closed`; CAPA metrics dashboard updated; **recurrence monitoring activated** for a defined period (system watches for new events matching this root cause)

#### Escalation rule

If any action is **overdue**, system **automatically sends escalation emails** at 7 days, 14 days, and 30 days overdue — to the action owner, CAPA owner, and eventually the Lab Director.

### 3.5 Cross-module connection

CAPA **listens to**: Quality Events, Audit Findings, Complaints, PT Results, Management Review decisions.
CAPA **triggers**: Document changes (Module 1), Training assignments (Module 5).

---

## Module 4 — Audit Management

### 4.1 Purpose (in one paragraph)

This module manages **all types of audits** — internal audits (we check ourselves), external audits (accreditation body checks us, e.g. NABL/A2LA), supplier audits (we check our suppliers), regulatory inspections (FDA visits). It handles planning the annual schedule, executing individual audits with checklists, recording findings, classifying them by severity, and automatically pushing serious findings into the CAPA workflow.

### 4.2 Roles involved

| Role | What they do |
|---|---|
| **Audit Program Manager** | Plans the annual audit schedule for the whole lab |
| **Lead Auditor** | Plans and executes a specific audit |
| **Auditor(s)** | Assist the Lead Auditor (the audit team) |
| **Auditee** | The person/team being audited (provides evidence, responds to findings) |
| **Quality Manager** | Approves the audit program; oversees findings → CAPA flow |

### 4.3 Fields on the screen

**Audit record:**

| Field | Example value |
|---|---|
| Audit ID | AUD-2026-0011 |
| Audit Type | Internal / External (Accreditation) / Supplier / Regulatory |
| Scope | "Microbiology Section — Sterility Testing Procedures" |
| Criteria | ISO 17025:2017 |
| Lead Auditor | Julie Cook |
| Auditors[] | Sarah Chen, Mark Dombrro |
| Auditee | Rajesh Patel (Section Head, Microbiology) |
| Scheduled Date | 13 Mar 2026 |
| Performed Date | 14 Mar 2026 |
| Checklist ID | CHK-ISO17025-001 |
| Findings[] | (added during execution, see below) |
| Status | Planned / In Progress / Reporting / Auditee Response / Follow-Up / Closed |
| Audit Report | (auto-generated PDF) |

**Audit Finding record:**

| Field | Example |
|---|---|
| Finding ID | FND-2026-0034 |
| Audit ID | AUD-2026-0011 |
| Classification | **Major NC** (Non-Conformance) / Minor NC / Observation / OFI (Opportunity for Improvement) |
| Description | "Calibration records for pH meter EQ-2018-0021 missing for Feb 2026" |
| Evidence | (uploaded photos, document snapshots, interview notes) |
| ISO Clause | 6.4.5 |
| CAPA ID | (auto-linked) CAPA-2026-0018 |
| Auditee Response | (filled later) "We have updated the calibration schedule and retrained the technician" |

### 4.4 Step-by-step workflow

#### Step 1 — Annual Audit Plan (once a year)

- **Who:** Audit Program Manager (often the Quality Manager)
- **Action:** Logs in → Audit module → **Audit Calendar** → creates audit schedule for the year, dragging and dropping audits onto the calendar grid
- **What he considers:** Risk score per area (higher risk = more frequent audits), independence (auditor cannot audit their own section)
- **Approval:** Quality Manager and Lab Director e-sign the annual plan

#### Step 2 — Audit Preparation

- **Who:** Lead Auditor (Julie)
- **Action:** Opens her assigned audit AUD-2026-0011 → fills in:
  - Audit Plan (Scope, Criteria)
  - Selects or builds a Checklist (e.g. ISO 17025 template + custom items)
  - Reviews previous findings and open CAPAs for the area
  - Schedules opening meeting with Rajesh (auditee)
- **What the system does:** Sends **audit notification email** to auditee with checklist preview, expected date, and required documents

#### Step 3 — Audit Execution (the actual audit day)

- **Who:** Lead Auditor + Audit team + Auditee
- **Action:**
  1. **Opening Meeting** — Lead Auditor explains scope, criteria, timeline
  2. **Walk through the checklist** — auditors interview personnel, review documents, take photos, observe procedures
  3. **Record findings** — for each non-conformance found, create a Finding record with classification (Major NC, Minor NC, Observation, OFI) and evidence
  4. **Closing Meeting** — present preliminary findings to auditee
- **What the system does:**
  - For each finding classified as Major NC or Minor NC: **automatically creates a draft CAPA** (Module 3) with the finding pre-linked
  - Saves all evidence to the audit record

#### Step 4 — Audit Report

- **Who:** Lead Auditor
- **Action:** Compiles findings → system **auto-generates audit report PDF** → Lead Auditor reviews and finalizes → submits
- **What the system does:** Status → `Reporting`; distributes report to auditee and Quality Manager

#### Step 5 — Auditee Response

- **Who:** Rajesh (auditee, Section Head)
- **Action:** For each finding, writes a response explaining:
  - What action will be taken
  - Who is responsible
  - When it will be completed
- **What the system does:** The CAPAs auto-created in Step 3 now have auditee response copied into them → status → `Auditee Response`

#### Step 6 — Follow-Up

- **Who:** Lead Auditor + Quality Manager
- **Action:** Tracks the CAPAs to closure (see Module 3); once all findings have closed CAPAs, schedules follow-up audit if needed
- **What the system does:** When all findings resolved, status → `Closed`

#### Step 7 — Program Review (annual)

- **Who:** Audit Program Manager
- **Action:** Reviews effectiveness of the audit program annually; results feed into Management Review (Module 12)

### 4.5 What the user sees — Audit Calendar

```
┌──────────────────────────────────────────────────────────────────────┐
│  Audit Calendar    [Today] [< >]      March 2026   [Month | Week]    │
├──────────────────────────────────────────────────────────────────────┤
│  Sun  │  Mon  │  Tue  │  Wed  │  Thu  │  Fri  │  Sat                 │
│   1   │   2   │   3   │   4   │   5   │   6   │   7                  │
│       │       │       │       │       │ AUD-11│                      │
│       │       │       │       │       │Cal Lab│                      │
│   8   │   9   │  10   │  11   │  12   │  13   │  14                  │
│       │       │       │       │       │ Micro │ Micro                │
│       │       │       │       │       │ Audit │ Audit                │
│  15   │  16   │  17   │  18   │  19   │  20   │  21                  │
│       │ Design│       │       │       │       │                      │
│       │Records│       │       │       │       │                      │
└──────────────────────────────────────────────────────────────────────┘
   (Drag and drop events to reschedule)
   Color legend: 🟦 Internal  🟪 External  🟧 Supplier
```

---

## Module 5 — Training & Competency

### 5.1 Purpose (in one paragraph)

This module makes sure **every employee is trained on the documents and procedures relevant to their job**, that they pass assessments, and that their competency is on record. Auditors will ask "show me proof that the analyst who ran this test was trained on the current version of the SOP" — this module produces that proof instantly.

### 5.2 Roles involved

| Role | What they do |
|---|---|
| **Trainee** | Any employee assigned training (Analyst, Section Head, etc.) |
| **Trainer** | Person who delivers training (could be a senior peer or external expert) |
| **Supervisor** (Section Head) | Verifies trainee's competence; signs off |
| **Quality Manager** | Owns the training program; reviews compliance |
| **Tenant Admin** | Sets up Job Codes (roles) and links them to required Courses |

### 5.3 Key concepts before workflow

Two important concepts:

| Concept | What it is |
|---|---|
| **Course** | A training unit (usually linked to one document, e.g. "Read and acknowledge SOP-MICRO-0042") OR standalone (e.g. "Annual GMP refresher") |
| **Job Code** | A role group (e.g. "Microbiology Analyst Level 1") that has a list of required Courses |

When you assign someone to a Job Code, the system automatically assigns them every Course on that job code's list.

### 5.4 Fields on the screen

**Training Assignment record:**

| Field | Example |
|---|---|
| Assignment ID | TA-2026-0291 |
| Trainee | David Okonkwo |
| Course | "SOP-MICRO-0042 v2.0 - Labeling Procedure" |
| Trigger | Document Approval / Manual / CAPA Action / Role Change / Periodic |
| Assigned Date | 26 Mar 2026 |
| Due Date | 9 Apr 2026 |
| Status | Assigned / In Progress / Complete / Overdue |
| Completion Date | (filled later) |
| Assessment Score | (filled later) e.g. 92% |
| Passing Score | 80% |
| E-signature | (captured on completion) |

### 5.5 Step-by-step workflow

#### Step 1 — Training auto-assigned (most common trigger)

- **Trigger:** Document Approved event from Module 1
- **Who:** System (automatic)
- **Action:** When SOP-MICRO-0042 v2.0 becomes Effective, system looks up everyone with "Microbiology Analyst" job code → creates a training assignment for each one
- **What David sees:** Email + in-app notification: "New training assigned: SOP-MICRO-0042 v2.0. Due 9 Apr 2026."

#### Step 2 — Trainee opens the training task

- **Who:** David
- **Action:** Logs in → My Training Folder → clicks the assignment → sees the **5-step training screen**:

```
┌──────────────────────────────────────────────────────────────┐
│  Training Task                                                │
│                                                               │
│  📖 ─────► 📚 ─────► ✏️ ─────► 👁️ ─────► ✅                 │
│ Intro    Materials   Exam    Overview  Sign Off              │
│                                                               │
│  Step 1: Introduction                                         │
│  Source of Training: New document added to course             │
│  Training For Course: SOP-MICRO-0042 - Labeling               │
│  Description: Updated labeling procedure per ISO 17025 8.3   │
│  Instructions: 1. Read attached document                      │
│                2. Take exam                                   │
│                3. Sign-off on task                            │
│  Trainer: Dan Hefer                                           │
│                                                               │
│  [Next →]                                                     │
└──────────────────────────────────────────────────────────────┘
```

#### Step 3 — Read materials

- **Who:** David
- **Action:** Clicks Next → reads SOP-MICRO-0042 v2.0 in-app → clicks Next
- **System logs:** Time spent reading, completion of read

#### Step 4 — Take exam

- **Who:** David
- **Action:** Answers exam questions (multiple choice, drag-drop, fill-in-blank)
- **What the system does:** Auto-grades exam against `passing_score`; if pass → proceed; if fail → retry (configurable max attempts)

#### Step 5 — Overview / final review

- **Who:** David
- **Action:** Sees summary of what he's done; opportunity to go back

#### Step 6 — Sign-off

- **Who:** David
- **Action:** Re-enters password → e-signs "I have read, understood, and will follow SOP-MICRO-0042 v2.0"
- **What the system does:**
  - Records timestamp + e-signature
  - Status → `Complete`
  - **Emails David's Supervisor (Rajesh):** "David completed training on SOP-MICRO-0042 v2.0"
  - **Emails CC:** Optional second supervisor

#### Step 7 — Compliance reporting (any time)

- **Who:** Quality Manager (or Section Head for own team)
- **Action:** Opens **Job Code Status Matrix** — a grid showing:
  - Rows = employees in a Job Code
  - Columns = required Courses
  - Each cell = status icon (✅ Complete, ⏳ In Progress, ⚠️ Overdue, 🔒 Waiting on Prerequisite, ⏸️ Pending Launch)
- **Use case:** Auditor asks "show me training compliance for Microbiology" → QM exports this matrix to Excel → hands over

```
┌────────────────────────────────────────────────────────────────────┐
│  Job Code Status: Microbiology Analyst                              │
├────────────┬────────┬────────┬────────┬────────┬────────┬──────────┤
│ Employee   │ GMP    │ Labeling│ Sterility│ Media  │ ...    │ % Done  │
├────────────┼────────┼────────┼────────┼────────┼────────┼──────────┤
│ David O.   │   ✅   │   ✅   │   ✅   │   ⏳   │   ...  │   85%   │
│ Sarah C.   │   ✅   │   ✅   │   ✅   │   ✅   │   ...  │  100%   │
│ Mike H.    │   ✅   │   ⚠️   │   ✅   │   ⏳   │   ...  │   60%   │
│ ...        │        │        │        │        │        │         │
├────────────┴────────┴────────┴────────┴────────┴────────┴──────────┤
│  Average Completion: 82%        [Export to Excel]                   │
└────────────────────────────────────────────────────────────────────┘
```

### 5.6 Cross-module connection

Training **listens to**: Document Approved, CAPA Action (retraining requirement), Role Change.
Training **gates**: Document release (a new doc isn't released until trained personnel have acknowledged).

---

## Module 6 — Equipment & Calibration

### 6.1 Purpose (in one paragraph)

This module tracks **every instrument in the lab from purchase to retirement** — balances, pH meters, HPLCs, autoclaves, incubators, etc. Most importantly, it manages **calibration schedules** (every instrument must be calibrated periodically against a traceable standard) and handles **out-of-tolerance** situations (when a calibration fails, what's the impact on results we already reported?). This is **RainerQMS's biggest differentiator** vs. generic QMS products.

### 6.2 Roles involved

| Role | What they do |
|---|---|
| **Equipment Coordinator** (Section Head or designated) | Maintains equipment register |
| **Calibration Technician** | Performs calibrations |
| **Qualified Reviewer** | Reviews calibration results, approves return-to-service |
| **Quality Manager** | Handles out-of-tolerance impact assessments |
| **Analyst** | Uses the equipment, logs usage |

### 6.3 Fields on the screen

**Equipment record:**

| Field | Example |
|---|---|
| Equipment ID | EQ-2018-0021 |
| Asset Tag | LAB-PHM-021 |
| Name | "pH Meter — Mettler Toledo SevenCompact" |
| Manufacturer | Mettler Toledo |
| Model | SevenCompact S220 |
| Serial Number | 12345-XYZ |
| Location | Microbiology Lab Room 3 |
| Status | In Service / Calibration Due / Under Calibration / Under Maintenance / Out of Service / Decommissioned |
| Calibration Interval | Every 3 months (or every 500 uses) |
| Next Calibration Due | 15 Jun 2026 |
| Last Calibration Date | 15 Mar 2026 |
| Measurement Uncertainty | ± 0.02 pH units |

**Calibration record:**

| Field | Example |
|---|---|
| Calibration ID | CAL-2026-0089 |
| Equipment ID | EQ-2018-0021 |
| Calibration Date | 15 Mar 2026 |
| Technician | Mark Dombrro |
| Standards Used | NIST-Traceable Buffer Solutions (Lot #BUF-2026-04, expires 30 Jun 2026) |
| As-Found Readings | pH 4.00 standard → measured 4.03 (drift +0.03) |
| As-Left Readings | pH 4.00 standard → measured 4.00 (after adjustment) |
| Pass/Fail | Pass |
| Measurement Uncertainty | ± 0.02 |
| Certificate | (auto-generated PDF) |
| Next Due Date | 15 Jun 2026 |

### 6.4 Step-by-step workflow

#### Step 1 — Scheduling (automatic)

- **Who:** System
- **Action:** 30 days before due date, sends reminder to Calibration Technician + Equipment Coordinator
- At 14 days, 7 days, 1 day: progressively more urgent reminders
- **What system does on due date:** Sets equipment status → `Calibration Due`

#### Step 2 — Preparation

- **Who:** Calibration Technician (Mark)
- **Action:** Opens equipment record → clicks **Start Calibration** → reviews:
  - Calibration SOP (linked document)
  - Reference standards (system verifies they're currently calibrated and traceable)
  - Environmental conditions (temperature, humidity within range)
- **System checks:** If standards expired or environment out of range, **blocks calibration from starting**

#### Step 3 — Execution

- **Who:** Mark
- **Action:** Performs calibration → enters **As-Found readings** (what the instrument reads before adjustment) → makes adjustments if needed → enters **As-Left readings** (after adjustment) → system calculates pass/fail against acceptance criteria → calculates measurement uncertainty
- **What system does:** Generates calibration certificate PDF; status → `Under Review`

#### Step 4 — Review & Approval

- **Who:** Qualified Reviewer (e.g. Quality Manager)
- **Action:** Reviews calibration data → if **Pass** → returns equipment to service. If **Fail** → triggers Out-of-Tolerance handling (Step 5)

#### Step 5 — Out-of-Tolerance Handling (the critical path)

- **Who:** Quality Manager
- **Trigger:** As-Found readings outside acceptance criteria
- **Action:**
  1. Equipment immediately set to **Out of Service**
  2. **Quality Event auto-created** (Module 2) with severity = Major or Critical
  3. **Impact assessment** — system identifies all tests run on this equipment since the last successful calibration → which client results may be affected?
  4. **Client notifications** — if results were already reported, clients notified
  5. **Decision** — Repair / Re-calibrate / Decommission
  6. If systemic issue (e.g. recurring drift), **CAPA initiated** (Module 3)

#### Step 6 — Record Completion

- **Who:** System
- **Action:** All calibration data stored; certificate linked; next calibration date scheduled; equipment status → `In Service` (or remains OOS pending repair)

#### Bonus: Usage logbook

Every time an analyst uses the equipment for a test, they log it (one-click on mobile or desktop). System uses this for usage-based calibration triggers ("every 500 uses").

---

## Module 7 — Environmental Monitoring

### 7.1 Purpose (in one paragraph)

This module tracks **environmental conditions in the lab** — temperature, humidity, particulate counts, differential pressure — required for ISO 17025 Clause 6.3. Some readings are taken manually by analysts; others come from IoT sensors that report continuously. When readings exceed defined limits, the system raises an alert and may auto-create a Quality Event.

### 7.2 Roles involved

| Role | What they do |
|---|---|
| **Analyst** | Records manual readings (e.g. fridge temperature) |
| **IoT Sensors** | Auto-report readings (via MQTT/HTTP) |
| **Section Head** | Responds to excursions in their area |
| **Quality Manager** | Reviews recurring excursions, escalates to CAPA |

### 7.3 Fields on the screen

**Monitoring Point record:**

| Field | Example |
|---|---|
| Point ID | EM-FRIDGE-MICRO-01 |
| Location | Microbiology Lab Room 3, Sample Storage Fridge |
| Parameter | Temperature |
| Alert Limit | 8 °C (warning) |
| Action Limit | 10 °C (excursion — creates quality event) |
| Frequency | Continuous (IoT) OR Every 4 hours (manual) |
| Last Reading | 5.2 °C at 14:32 on 15 May 2026 |
| Status | Within Limits / Alert / Excursion |

### 7.4 Step-by-step workflow

#### Step 1 — Continuous monitoring (IoT)

- **Who:** IoT temperature sensor
- **Action:** Reports temperature every 5 minutes via MQTT
- **What system does:** Stores reading; checks against limits

#### Step 2 — Excursion detected

- **Trigger:** Fridge temperature spikes to 11 °C
- **What system does:**
  - Real-time push notification to Section Head + on-shift Analyst
  - Flags the monitoring point in dashboard
  - **Auto-creates a Quality Event** (Module 2) since action limit exceeded

#### Step 3 — Immediate action

- **Who:** On-shift Analyst
- **Action:** Investigates fridge → checks samples inside → if samples compromised, moves them; documents action

#### Step 4 — Investigation

- **Who:** Quality Manager
- **Action:** Reviews how long the excursion lasted, magnitude, impact on samples; if recurring → escalates to CAPA

#### Step 5 — Closure

- **Who:** Quality Manager
- **Action:** Once fridge confirmed back in range and impact assessed, closes Quality Event with summary

---

## Module 8 — Supplier Quality

### 8.1 Purpose (in one paragraph)

This module manages **every external supplier the lab depends on** — reagent suppliers, reference material providers, equipment vendors, external testing services. It tracks their approval status, qualifies new suppliers, monitors their ongoing performance, and links specific materials/parts to specific approved suppliers. If a supplier's approval drops, the system automatically disables the link so the lab can't accidentally use a non-approved supplier.

### 8.2 Roles involved

| Role | What they do |
|---|---|
| **Quality Manager** | Owns supplier qualification program |
| **QA Officer** | Tracks ongoing supplier performance, verifies CoAs (Certificates of Analysis) |
| **Section Head** | Identifies new suppliers needed |
| **External Supplier** | (via Guest Connect) Can respond to audit findings, comment on specs |

### 8.3 Fields on the screen

**Supplier record:**

| Field | Example |
|---|---|
| Supplier ID | SUP-2024-0012 |
| Supplier Name | Sigma-Aldrich |
| Supplier Type | Reagent / Reference Material / Service / Equipment |
| Status | Approved / Conditionally Approved / Under Qualification / Inactive / Certified / Disapproved |
| Criticality | Critical / Major / Minor |
| Risk Score | Low / Medium / High |
| Contacts[] | Sarah Kofax — skofax@sigma.com — +1-314-555-1234 |
| Materials/Parts/Services[] | (linked items, see below) |
| Next Re-qualification | 15 Mar 2027 |

**Material/Part subsection:**

| Type | Supplier's Part # | InfoCard # | Title | Approved |
|---|---|---|---|---|
| Reagent | KLR-00345 | 02-0002 Rev 01 | "Buffer Solution pH 4.00" | ✅ |
| SDS | (system-linked) | SDS-0002 | "WD-40 Safety Data Sheet" | ✅ |

### 8.4 Step-by-step workflow

#### Step 1 — New supplier identification

- **Who:** Section Head needs a new reagent
- **Action:** Submits supplier request to Quality Manager

#### Step 2 — Initial evaluation

- **Who:** Quality Manager
- **Action:** Opens Supplier module → **+ New Supplier** → fills basic info → sends **qualification questionnaire** to supplier; for Critical suppliers, schedules on-site audit
- **What system does:** Status → `Under Qualification`

#### Step 3 — Approval decision

- **Who:** Quality Manager
- **Decision:**
  - **Approved** → added to Approved Supplier List (ASL)
  - **Conditionally Approved** → with conditions and timeline (e.g. "Approved for 90 days; must submit ISO 9001 cert within that window")
  - **Disapproved** → documented and supplier notified

#### Step 4 — Linking materials

- **Who:** QA Officer
- **Action:** For each material the lab buys from this supplier, links the part number to the Supplier record
- **Result:** When an Analyst orders a reagent, the system shows only approved suppliers

#### Step 5 — Ongoing monitoring

- **Who:** QA Officer
- **Action:** Each shipment received → verifies Certificate of Analysis (CoA) → logs incoming inspection → updates scorecard
- **System tracks:** On-time delivery %, quality NCRs, scorecard updated quarterly

#### Step 6 — Re-qualification

- **Who:** Quality Manager
- **When:** Annually for Critical, biannually for Major
- **Action:** Reviews cumulative performance → re-approves OR drops status

#### Auto-disable links (critical safety feature)

If supplier status drops from `Approved` → `Conditionally Approved` or below, **system automatically disables all material/part links** to that supplier → analysts can no longer order from them.

#### Secure Guest Connect

If we audit a supplier and they need to respond to findings, the Quality Manager can issue them a **Guest Connect** link (limited-time, scoped access) so they can log in to comment on findings without being a full user.

---

## Module 9 — Risk Management

### 9.1 Purpose (in one paragraph)

This module proactively identifies, assesses, and tracks risks **before** they become quality events. Different from CAPA (which is reactive), Risk Management asks: "what could go wrong?" Special importance for testing labs: **Impartiality Risk Register** (ISO 17025 Clause 4.1) — tracking situations where lab employees might have a conflict of interest (e.g. testing samples for a client they have personal ties to).

### 9.2 Roles involved

| Role | What they do |
|---|---|
| **Risk Owner** (Section Head or designated) | Owns a specific risk |
| **Quality Manager** | Owns the risk register; reviews assessments |
| **Lab Director** | Approves high-risk mitigation plans |

### 9.3 Fields on the screen

**Risk record:**

| Field | Example |
|---|---|
| Risk ID | RSK-2026-0021 |
| Category | Operational / Impartiality / Financial / Regulatory / Safety |
| Description | "Reference standards may degrade if stored outside spec range" |
| Severity | 1–5 |
| Likelihood | 1–5 |
| Risk Score | Severity × Likelihood = 12 |
| Mitigation Plan | "Install backup temperature alarm; weekly verification by analyst" |
| Owner | Rajesh Patel |
| Status | Identified / Mitigated / Accepted / Monitoring |
| Review Date | Quarterly |

### 9.4 Step-by-step workflow

#### Step 1 — Risk identification

- Anyone can identify a risk → submits to Quality Manager
- Common triggers: New equipment, new procedure, audit finding, near-miss

#### Step 2 — Assessment

- Risk Owner + Quality Manager score Severity × Likelihood → produce Risk Score
- If Score ≥ defined threshold → goes to Lab Director for review

#### Step 3 — Mitigation Plan

- Define controls to reduce risk
- For impartiality risks (Clause 4.1), specific controls like: rotation of analysts, blind testing, independent review

#### Step 4 — Implementation

- Controls put in place
- Each control becomes an action with an owner and due date

#### Step 5 — Monitoring

- Quarterly review of risk register
- New risks added; closed risks archived

---

## Module 10 — Proficiency Testing (PT)

### 10.1 Purpose (in one paragraph)

This module manages **inter-laboratory comparison programs** — required by ISO 17025 to prove the lab can produce accurate results. The lab participates in PT schemes where multiple labs test the same unknown sample, and statistical scores (z-score, En number) show how each lab performs. **Unsatisfactory results automatically trigger CAPAs.** This is a **lab-specific module not found in generic QMS products like MasterControl.**

### 10.2 Roles involved

| Role | What they do |
|---|---|
| **PT Coordinator** (Section Head) | Manages PT participation for their section |
| **Analyst** | Runs the PT samples blind (without knowing the reference value) |
| **Quality Manager** | Reviews PT performance, escalates unsatisfactory results |

### 10.3 Fields on the screen

**PT Round record:**

| Field | Example |
|---|---|
| PT ID | PT-2026-Q2-MICRO-001 |
| Provider | LGC / NSI / FAPAS / Bipea |
| Scheme Name | "Microbiological Examination of Water" |
| Round | Q2 2026 |
| Sample Received Date | 5 Apr 2026 |
| Result Due Date | 30 Apr 2026 |
| Reported Result | "TVC: 45 CFU/mL" |
| Reference Value (revealed later) | 47 CFU/mL |
| z-score | -0.4 |
| En number | 0.3 |
| Status | Pending / Submitted / Awaiting Score / Satisfactory / Unsatisfactory |

### 10.4 Step-by-step workflow

#### Step 1 — PT sample arrives

- **Who:** Section Head logs receipt → assigns analyst (blind)

#### Step 2 — Analyst runs the test

- Analyst tests sample exactly as per SOP → enters result

#### Step 3 — Result submitted to provider

- System packages result → sent to PT provider

#### Step 4 — Provider returns scores

- z-score, En number returned
- Acceptance criteria: |z| ≤ 2 is satisfactory

#### Step 5 — Decision

- **Satisfactory** (|z| ≤ 2) → close round, file results
- **Questionable** (2 < |z| ≤ 3) → investigate
- **Unsatisfactory** (|z| > 3) → **CAPA auto-created** → root cause investigation

#### Step 6 — Trend analysis

- System tracks PT performance over time → identifies methods that consistently underperform

---

## Module 11 — Customer Complaint Management

### 11.1 Purpose (in one paragraph)

This module captures and resolves **complaints from clients** — disputes about test results, delivery issues, communication problems. Required by ISO 17025 Clause 7.9. Every complaint is investigated, responded to, and tracked; recurring or systemic complaints escalate to CAPA.

### 11.2 Roles involved

| Role | What they do |
|---|---|
| **QA Officer** | First responder; logs complaint |
| **Investigator** (Section Head) | Investigates root cause |
| **Quality Manager** | Approves response, decides escalation |
| **Customer** | (external) Submits complaint via portal/email |

### 11.3 Fields on the screen

| Field | Example |
|---|---|
| Complaint ID | CMP-2026-0044 |
| Customer | ABC Foods Inc. |
| Received Via | Email / Phone / Web Form / Client Portal |
| Severity | Critical / Major / Minor |
| Description | "Result for sample S-2026-1144 disagrees with our in-house result by 30%" |
| Category | Test Result Dispute / Turnaround Time / Communication / Invoice |
| Date Received | 15 May 2026 |
| Date Resolved | (filled later) |
| Investigator | Rajesh Patel |
| Root Cause | (filled later) |
| Response Sent | (filled later) |
| CAPA Reference | (if escalated) |

### 11.4 Step-by-step workflow

#### Step 1 — Complaint received

- Customer submits via email/portal → system auto-acknowledges receipt → logs complaint → notifies QA Officer

#### Step 2 — Triage

- QA Officer classifies severity → assigns Investigator

#### Step 3 — Investigation

- Investigator pulls all related records: original test, sample chain-of-custody, equipment used, analyst, training records
- Documents findings

#### Step 4 — Response preparation

- Drafts response → Quality Manager reviews → response sent to customer

#### Step 5 — Corrective action (if needed)

- If systemic issue → CAPA initiated (Module 3)

#### Step 6 — Closure

- Customer acknowledges response → complaint closed → data feeds into trend dashboards and Management Review

---

## Module 12 — Management Review

### 12.1 Purpose (in one paragraph)

ISO 17025 Clause 8.9 requires lab leadership to conduct a **formal annual review** of the quality management system. This module **auto-compiles all the required inputs** (audit results, CAPA status, customer feedback, training stats, PT performance, etc.) — saving days of manual prep — and tracks the decisions and action items from the meeting.

### 12.2 Roles involved

| Role | What they do |
|---|---|
| **Quality Manager** | Schedules review, prepares data, captures minutes |
| **Lab Director** | Chairs the review meeting |
| **Section Heads** | Attend, contribute, accept action items |

### 12.3 Step-by-step workflow

#### Step 1 — Scheduling

- Quality Manager schedules annual review (typical: Q1) → invites Lab Director + Section Heads

#### Step 2 — Auto-Data Compilation

- 30 days before meeting, system auto-pulls 12 required ISO 17025 Clause 8.9.2 inputs:
  - Status of actions from previous review
  - Policy/objectives suitability
  - Audit results (internal & external)
  - CAPA status
  - External assessments
  - Quality indicators/KPIs
  - Supplier performance
  - Customer feedback (complaints, satisfaction)
  - Risk register status
  - Training status
  - Resource adequacy
  - PT performance
- Generates **Management Review Package PDF** ready for the meeting

#### Step 3 — Review Meeting

- Lab Director chairs → each input discussed → decisions captured → action items assigned with owners and due dates

#### Step 4 — Follow-up

- Action items tracked to completion → results carried forward to next review

---

## Module 13 — Reporting & Analytics

### 13.1 Purpose (in one paragraph)

This is the **business intelligence layer** sitting on top of all other modules. It provides real-time dashboards, KPIs, compliance scorecards, trend charts, and (in Phase 3) AI-powered insights. Auditors love this — instead of digging through individual records, they see the whole picture in seconds.

### 13.2 Standard dashboards

| Dashboard | What it shows |
|---|---|
| **Quality Scorecard** | Overall quality health: open CAPAs, overdue training, calibration compliance |
| **CAPA by Department** | Pie chart of which sections have the most CAPAs |
| **Complaints by Product** | Pie chart of which products generate most complaints |
| **NCMR Disposition** | What we do with non-conforming materials (Scrap / Rework / Return / Accept) |
| **Training Compliance** | % of required training completed across the lab |
| **Audit Findings Trend** | Findings over time, by type, by area |
| **PT Performance** | z-score trends over time |
| **Equipment Calibration Status** | Pie chart: In Service / Due / Overdue / OOS |

### 13.3 Phase 3 AI features

- **Trend Detection** — system flags emerging issues before they become events
- **Root Cause Suggestion** — for a new CAPA, AI suggests probable causes from historical similar events
- **Exam Generation** — auto-generates training quizzes from SOP content
- **Predictive Compliance** — forecasts which areas are at risk of failing next audit

---

## Module 14 — Lab-Specific Features

This isn't a single module — it's a collection of lab-specific capabilities distributed across other modules. Brief summary:

| Feature | Lab type | What it does |
|---|---|---|
| **Method Validation** | Chemistry, Microbiology | Validates that a test method is fit for purpose (accuracy, precision, LOD, LOQ) |
| **Measurement Uncertainty** | All testing labs | Calculates uncertainty budget per GUM methodology |
| **Control Charts** | Chemistry, Calibration | Shewhart, CUSUM, EWMA, Westgard rules for QC monitoring |
| **Media Prep QC** | Microbiology | Tracks each batch of growth medium prepared, sterility check, performance check |
| **Culture Collection** | Microbiology | Tracks reference strain inventory with passage number |
| **CRM Tracking** | Chemistry | Certified Reference Material inventory with expiration dates |
| **HPLC/GC/ICP Workflows** | Chemistry | Instrument-specific QC, system suitability tests |
| **Calibration Certificates** | Calibration Labs | Generates customer-facing calibration certificates for client instruments |
| **Aseptic Technique Assessment** | Microbiology | Periodic personnel competency check in sterile technique |

These features are **deferred to Phase 2 or later** in the development roadmap, but they are RainerQMS's **competitive moat vs. MasterControl/TrackWise**.

---

## The big picture — how the modules talk to each other

Now that you've seen each module, here's how they interconnect. This is the **whole point** of an integrated QMS: data flows automatically between modules so people don't manually re-enter the same information in 5 places.

### The 9 key cross-module flows

| # | When this happens... | This module fires an event... | These modules listen and react |
|---|---|---|---|
| 1 | A document is approved and becomes Effective | Document Control (M1) | Training (M5) auto-assigns reading + acknowledgment to distribution list members |
| 2 | A document is approved | Document Control (M1) | Notifications go to owner + distribution list |
| 3 | A Critical quality event is created | Quality Event (M2) | CAPA (M3) auto-creates a CAPA |
| 4 | An audit finding is created as Major/Minor NC | Audit (M4) | CAPA (M3) auto-creates a draft CAPA |
| 5 | A calibration fails (Out-of-Tolerance) | Equipment (M6) | Quality Event (M2) auto-creates a non-conformance |
| 6 | An environmental excursion exceeds action limit | Environmental Monitoring (M7) | Quality Event (M2) auto-creates a deviation |
| 7 | A PT result is unsatisfactory (|z| > 3) | PT (M10) | CAPA (M3) auto-initiates a CAPA |
| 8 | A CAPA action is overdue (7/14/30 days) | CAPA (M3) | Notification escalation to management |
| 9 | A training assignment is overdue | Training (M5) | Notification to employee + supervisor |

### A full end-to-end example (the "story" auditors love)

Imagine this Monday morning at the lab:

1. **08:15** — IoT sensor reports the sample fridge spiked to 11 °C overnight (Module 7)
2. **08:15** — System auto-creates Quality Event QE-2026-0050 (Module 2)
3. **08:16** — On-shift Analyst gets a phone notification → goes to fridge → moves samples to backup → logs immediate action
4. **09:30** — Section Head reviews event → assesses impact → finds 4 client samples affected
5. **10:00** — Quality Manager escalates to CAPA-2026-0019 (Module 3) — this is a recurring problem
6. **10:30** — Quality Manager + Section Head investigate → root cause: fridge compressor failing
7. **11:00** — Action plan: (a) Replace fridge (action owner: Tenant Admin, due in 2 weeks), (b) Update SOP-MICRO-0050 to add daily manual temp check
8. **14:00** — SOP revision initiated (Module 1) → Author drafts updated SOP
9. **Next day** — SOP reviewed and approved → becomes Effective → **Training auto-assigned to all 8 microbiology analysts** (Module 5)
10. **2 weeks later** — Each analyst completes training → signs off
11. **3 weeks later** — New fridge installed → Equipment record created (Module 6) → calibration scheduled (every 3 months)
12. **90 days later** — Effectiveness check on CAPA-2026-0019 → no new temperature excursions → CAPA closed
13. **Annual Management Review** — fridge incident shows up in the quality indicators (Module 12) → contributes to next year's capital budget decision

**That entire 9-month story is traceable in the system end-to-end**, with every action timestamped and e-signed. An ISO 17025 assessor can ask "show me what happened with the fridge incident" and get this exact trail in 30 seconds.

---

## Reading guide for newcomers

If you've never seen a QMS before, here's the order I recommend reading the modules:

| Order | Module | Why first |
|---|---|---|
| 1 | **Module 1 — Document Control** | Foundation of everything; understand version control + e-signature here |
| 2 | **Module 5 — Training** | See how doc approval auto-triggers training (the magic of integrated QMS) |
| 3 | **Module 2 — Quality Events** | See how problems get reported |
| 4 | **Module 3 — CAPA** | See how problems get permanently fixed |
| 5 | **Module 4 — Audit** | See how the QMS gets checked |
| 6 | **Module 6 — Equipment** | RainerQMS differentiator vs. generic QMS |
| 7 | The rest | Read in any order |

Then re-read **"The big picture"** section at the end — by then it will make complete sense.

---

*End of RainerQMS Module-by-Module Workflow Walkthrough*
