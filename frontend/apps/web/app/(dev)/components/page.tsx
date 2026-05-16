"use client"

import { useState } from "react"
import { FileText, PenTool, AlertTriangle, CheckCircle2, Users, Calendar, BarChart3 } from "lucide-react"

import { StatusBadge } from "@/components/qms-shared/StatusBadge"
import { SeverityBadge } from "@/components/qms-shared/SeverityBadge"
import { DateInfoGrid } from "@/components/qms-shared/DateInfoGrid"
import { ModuleHeader } from "@/components/qms-shared/ModuleHeader"
import { WorkflowStepBar } from "@/components/qms-shared/WorkflowStepBar"
import { FilterSidebar } from "@/components/qms-shared/FilterSidebar"
import { DashboardTiles } from "@/components/qms-shared/DashboardTiles"
import { FileUploadDropzone } from "@/components/qms-shared/FileUploadDropzone"
import { EventTimeline } from "@/components/qms-shared/EventTimeline"
import { InfoCard } from "@/components/qms-shared/InfoCard"
import { FBSForm } from "@/components/qms-shared/FBSForm"
import { SignatureDialog } from "@/components/qms-shared/SignatureDialog"
import { MatrixGrid } from "@/components/qms-shared/MatrixGrid"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

const sections = [
  { id: "status-badge", label: "StatusBadge" },
  { id: "severity-badge", label: "SeverityBadge" },
  { id: "date-info-grid", label: "DateInfoGrid" },
  { id: "module-header", label: "ModuleHeader" },
  { id: "workflow-step-bar", label: "WorkflowStepBar" },
  { id: "filter-sidebar", label: "FilterSidebar" },
  { id: "dashboard-tiles", label: "DashboardTiles" },
  { id: "file-upload-dropzone", label: "FileUploadDropzone" },
  { id: "event-timeline", label: "EventTimeline" },
  { id: "info-card", label: "InfoCard" },
  { id: "fbs-form", label: "FBSForm" },
  { id: "signature-dialog", label: "SignatureDialog" },
  { id: "matrix-grid", label: "MatrixGrid" },
]

export default function ComponentSandboxPage() {
  const [sigOpen, setSigOpen] = useState(false)
  const [activeSection, setActiveSection] = useState("status-badge")

  return (
    <div className="min-h-screen bg-background">
      <div className="flex">
        {/* Sidebar nav */}
        <aside className="w-56 shrink-0 border-r min-h-screen p-3 space-y-1">
          <h2 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider px-2 mb-3">
            QMS Components
          </h2>
          {sections.map((s) => (
            <button
              key={s.id}
              onClick={() => setActiveSection(s.id)}
              className={`w-full text-left px-2 py-1.5 rounded text-sm transition-colors ${
                activeSection === s.id
                  ? "bg-primary/10 text-primary font-medium"
                  : "text-muted-foreground hover:text-foreground hover:bg-muted"
              }`}
            >
              {s.label}
            </button>
          ))}
        </aside>

        {/* Main content */}
        <main className="flex-1 p-8 space-y-8 max-w-4xl">
          <h1 className="text-2xl font-bold">QMS Components — Dev Sandbox</h1>
          <p className="text-muted-foreground -mt-4">
            Visual reference for all 14 shared components. Each section shows all variant permutations.
          </p>

          {/* ── StatusBadge ── */}
          {activeSection === "status-badge" && (
            <Section title="StatusBadge" description="Colored badge for document lifecycle status. Matches §2.2 color tokens.">
              <div className="flex flex-wrap gap-3">
                <StatusBadge status="draft" />
                <StatusBadge status="under_review" />
                <StatusBadge status="approved" />
                <StatusBadge status="effective" />
                <StatusBadge status="superseded" />
                <StatusBadge status="obsolete" />
              </div>
            </Section>
          )}

          {/* ── SeverityBadge ── */}
          {activeSection === "severity-badge" && (
            <Section title="SeverityBadge" description="Colored badge for event/CAPA severity levels.">
              <div className="flex flex-wrap gap-3">
                <SeverityBadge severity="critical" />
                <SeverityBadge severity="major" />
                <SeverityBadge severity="minor" />
                <SeverityBadge severity="observation" />
                <SeverityBadge severity="high" />
                <SeverityBadge severity="medium" />
                <SeverityBadge severity="low" />
              </div>
            </Section>
          )}

          {/* ── DateInfoGrid ── */}
          {activeSection === "date-info-grid" && (
            <Section title="DateInfoGrid" description="2×3 grid for date information sections (Document InfoCard).">
              <DateInfoGrid
                items={[
                  { label: "Created", value: "07 Nov 2025" },
                  { label: "Released", value: "26 Mar 2026" },
                  { label: "Effective", value: "26 Mar 2026" },
                  { label: "Expires", value: null },
                  { label: "Moved to Phase", value: "26 Mar 2026" },
                  { label: "Next Review", value: "26 Mar 2027" },
                ]}
              />
            </Section>
          )}

          {/* ── ModuleHeader ── */}
          {activeSection === "module-header" && (
            <Section title="ModuleHeader" description="Breadcrumb + title + action buttons. Foundation for every page.">
              <ModuleHeader
                title="Document Control"
                subtitle="Manage SOPs, work instructions, and quality documents"
                icon={<FileText className="h-6 w-6" />}
                breadcrumbs={[
                  { label: "Home", href: "/dashboard" },
                  { label: "Documents" },
                ]}
                actions={
                  <>
                    <Button size="sm" variant="outline">Search</Button>
                    <Button size="sm">+ New Document</Button>
                  </>
                }
              />
            </Section>
          )}

          {/* ── WorkflowStepBar ── */}
          {activeSection === "workflow-step-bar" && (
            <Section title="WorkflowStepBar" description="Horizontal step progress bar with active/complete/pending states.">
              <Card>
                <CardContent className="pt-6">
                  <p className="text-sm text-muted-foreground mb-4">Current: Investigation</p>
                  <WorkflowStepBar
                    steps={[
                      { key: "open", label: "Open" },
                      { key: "investigation", label: "Investigation" },
                      { key: "root_cause", label: "Root Cause" },
                      { key: "implementation", label: "Implementation" },
                      { key: "effectiveness", label: "Effectiveness" },
                      { key: "closed", label: "Closed" },
                    ]}
                    currentStep="investigation"
                    completedSteps={["open"]}
                  />
                </CardContent>
              </Card>
            </Section>
          )}

          {/* ── FilterSidebar ── */}
          {activeSection === "filter-sidebar" && (
            <Section title="FilterSidebar" description="Right-side collapsible multi-filter panel with checkbox groups.">
              <div className="flex items-start gap-4">
                <FilterSidebar
                  groups={[
                    {
                      id: "status",
                      label: "Status",
                      type: "checkbox",
                      value: [],
                      options: [
                        { label: "Draft", value: "draft" },
                        { label: "Under Review", value: "under_review" },
                        { label: "Effective", value: "effective" },
                        { label: "Obsolete", value: "obsolete" },
                      ],
                      onChange: () => {},
                    },
                    {
                      id: "type",
                      label: "Type",
                      type: "select",
                      value: "",
                      options: [
                        { label: "SOP", value: "sop" },
                        { label: "WI", value: "wi" },
                        { label: "Method", value: "method" },
                      ],
                      onChange: () => {},
                    },
                    {
                      id: "department",
                      label: "Department",
                      type: "text",
                      value: "",
                      onChange: () => {},
                    },
                  ]}
                />
                <p className="text-sm text-muted-foreground">Click &quot;Filters&quot; to open the sidebar panel.</p>
              </div>
            </Section>
          )}

          {/* ── DashboardTiles ── */}
          {activeSection === "dashboard-tiles" && (
            <Section title="DashboardTiles" description="Configurable grid of tiles with icon + label + count + click action.">
              <DashboardTiles
                columns={4}
                tiles={[
                  { id: "1", icon: <FileText />, label: "My Tasks", count: 12 },
                  { id: "2", icon: <PenTool />, label: "My Recent", count: 5 },
                  { id: "3", icon: <AlertTriangle />, label: "Overdue CAPAs", count: 3, color: "bg-red-50" },
                  { id: "4", icon: <CheckCircle2 />, label: "Completed", count: 28 },
                  { id: "5", icon: <Users />, label: "Training", count: 8 },
                  { id: "6", icon: <Calendar />, label: "Calibration Due", count: 2, color: "bg-amber-50" },
                  { id: "7", icon: <BarChart3 />, label: "Reports" },
                  { id: "8", icon: <FileText />, label: "Documents Due", count: 4 },
                ]}
              />
            </Section>
          )}

          {/* ── FileUploadDropzone ── */}
          {activeSection === "file-upload-dropzone" && (
            <Section title="FileUploadDropzone" description="Drag-and-drop file upload with progress and virus scan status.">
              <FileUploadDropzone
                onFilesSelected={(files) => console.log("Files:", files)}
                accept={[".pdf", ".docx", ".xlsx", ".png", ".jpg"]}
              />
            </Section>
          )}

          {/* ── EventTimeline ── */}
          {activeSection === "event-timeline" && (
            <Section title="EventTimeline" description="Vertical timeline of audit-trail events with actor, timestamp, action, diffs.">
              <EventTimeline
                events={[
                  {
                    id: "1",
                    action: "document_created",
                    actor: "rajesh.patel@lab.com",
                    timestamp: new Date(Date.now() - 86400000 * 5).toISOString(),
                    description: "Document created in Draft status",
                  },
                  {
                    id: "2",
                    action: "submitted_for_review",
                    actor: "rajesh.patel@lab.com",
                    timestamp: new Date(Date.now() - 86400000 * 3).toISOString(),
                    description: "Submitted for approval review",
                  },
                  {
                    id: "3",
                    action: "approved",
                    actor: "priya.sharma@lab.com",
                    timestamp: new Date(Date.now() - 86400000 * 1).toISOString(),
                    description: "Approved with e-signature",
                    before: { status: "under_review" },
                    after: { status: "approved" },
                  },
                ]}
              />
            </Section>
          )}

          {/* ── InfoCard ── */}
          {activeSection === "info-card" && (
            <Section title="InfoCard" description="Two-column layout with left-side form sections + right-side vertical tabs. MasterControl-quality.">
              <InfoCard
                title="Labeling Procedure for Finished Goods"
                subtitle="SOP-MICRO-0042"
                status={<StatusBadge status="effective" />}
                actions={
                  <>
                    <Button size="sm" variant="outline">Initiate Revision</Button>
                    <Button size="sm">Acknowledge</Button>
                  </>
                }
                sections={[
                  {
                    id: "version-info",
                    title: "Version Information",
                    content: (
                      <div className="grid grid-cols-2 gap-3 text-sm">
                        <div><span className="text-muted-foreground">Document Number:</span> SOP-MICRO-0042</div>
                        <div><span className="text-muted-foreground">Version:</span> 2.0</div>
                        <div><span className="text-muted-foreground">ISO Clauses:</span> 8.3, 8.4</div>
                        <div><span className="text-muted-foreground">Vault:</span> QA-Released</div>
                      </div>
                    ),
                  },
                  {
                    id: "date-info",
                    title: "Date Information",
                    content: (
                      <DateInfoGrid
                        items={[
                          { label: "Created", value: "07 Nov 2025" },
                          { label: "Effective", value: "26 Mar 2026" },
                          { label: "Next Review", value: "26 Mar 2027" },
                        ]}
                      />
                    ),
                  },
                  {
                    id: "owner",
                    title: "Owner & Approvers",
                    content: (
                      <div className="text-sm space-y-1">
                        <div><span className="text-muted-foreground">Owner:</span> Rajesh Patel</div>
                        <div><span className="text-muted-foreground">Approver:</span> Dr. Priya Sharma</div>
                      </div>
                    ),
                  },
                ]}
                tabs={[
                  {
                    id: "information",
                    label: "Information",
                    content: <p className="text-sm text-muted-foreground p-2">Main content rendered here.</p>,
                  },
                  {
                    id: "training",
                    label: "Training",
                    content: <p className="text-sm text-muted-foreground p-2">Linked training courses and compliance.</p>,
                  },
                  {
                    id: "history",
                    label: "History",
                    content: (
                      <EventTimeline
                        events={[
                          { id: "1", action: "created", actor: "rajesh", timestamp: new Date().toISOString() },
                        ]}
                      />
                    ),
                  },
                ]}
              />
            </Section>
          )}

          {/* ── FBSForm ── */}
          {activeSection === "fbs-form" && (
            <Section title="FBSForm" description="Tabbed form container for QE/CAPA/Complaint detail pages. Tab-by-tab validation ready.">
              <FBSForm
                header={
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">QE-2026-0037</p>
                      <p className="text-xs text-muted-foreground">Current Step: Investigation</p>
                    </div>
                    <StatusBadge status="under_review" />
                  </div>
                }
                tabs={[
                  { id: "about", label: "About", content: <p className="text-sm p-4">Form number, status, created by, dates.</p> },
                  { id: "event-info", label: "Event Information", icon: "✏️", content: <p className="text-sm p-4">Title, description, type, severity, department, dates.</p> },
                  { id: "investigation", label: "Investigation", content: <p className="text-sm p-4">Investigator, notes, assigned to, due date.</p> },
                  { id: "root-cause", label: "Root Cause", content: <p className="text-sm p-4">5-Why or Fishbone analysis, evidence files.</p> },
                  { id: "action-items", label: "Action Items", content: <p className="text-sm p-4">Corrective/preventive actions list.</p> },
                  { id: "resolution", label: "Resolution", content: <p className="text-sm p-4">Resolution summary, closure date, verified by.</p> },
                ]}
              />
            </Section>
          )}

          {/* ── SignatureDialog ── */}
          {activeSection === "signature-dialog" && (
            <Section title="SignatureDialog" description="Re-auth + signature meaning declaration modal for 21 CFR Part 11.">
              <Button onClick={() => setSigOpen(true)}>Open Signature Dialog</Button>
              <SignatureDialog
                open={sigOpen}
                onOpenChange={setSigOpen}
                meaning="I approve this document for release"
                onConfirm={async (sig) => {
                  await new Promise((r) => setTimeout(r, 1000))
                  console.log("Signed with:", sig)
                }}
                requireReauth
              />
            </Section>
          )}

          {/* ── MatrixGrid ── */}
          {activeSection === "matrix-grid" && (
            <Section title="MatrixGrid" description="Sticky-header rows × columns grid with status icon cells for Job Code Matrix.">
              <MatrixGrid
                columns={[
                  { id: "gmp", label: "GMP" },
                  { id: "lbl", label: "Labeling" },
                  { id: "ster", label: "Sterility" },
                  { id: "media", label: "Media Prep" },
                  { id: "ils", label: "IL Sample" },
                ]}
                rows={[
                  { id: "1", label: "Carpenter, Rob", cells: { gmp: "complete", lbl: "complete", ster: "complete", media: "in_progress", ils: "in_progress" } },
                  { id: "2", label: "Christensen, Sam", cells: { gmp: "complete", lbl: "complete", ster: "complete", media: "complete", ils: "complete" } },
                  { id: "3", label: "Harper, Jeff", cells: { gmp: "complete", lbl: "overdue", ster: "complete", media: "in_progress", ils: "complete" } },
                  { id: "4", label: "Toms, David", cells: { gmp: "overdue", lbl: "overdue", ster: "overdue", media: "overdue", ils: "overdue" } },
                  { id: "5", label: "Little, Doug", cells: { gmp: "complete", lbl: "pending", ster: "pending", media: "pending", ils: "pending" } },
                  { id: "6", label: "Lewis, Kai", cells: { gmp: "complete", lbl: "waiting", ster: "in_progress", media: "in_progress", ils: "in_progress" } },
                ]}
                footer={
                  <span>Average Percentage Completed: 46% · 0 of 6 have completed all training</span>
                }
              />
            </Section>
          )}
        </main>
      </div>
    </div>
  )
}

function Section({ title, description, children }: { title: string; description: string; children: React.ReactNode }) {
  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <Card>
        <CardContent className="pt-6">{children}</CardContent>
      </Card>
    </div>
  )
}
