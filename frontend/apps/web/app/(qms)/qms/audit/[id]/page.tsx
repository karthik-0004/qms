"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  useAudit,
  useAuditFindings,
  useUpdateAudit,
  useStartAudit,
  useCompleteAudit,
  useDeleteAudit,
  useAddAuditFinding,
} from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  ChevronLeft,
  Play,
  CheckCircle2,
  Trash2,
  AlertTriangle,
  Plus,
  ClipboardCheck,
  FileText,
  Eye,
} from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import type { AuditFinding } from "@/lib/api/services/qms";

// ── Status helpers ────────────────────────────────────────────────────────────

const STATUS_STEPS = ["planned", "in_progress", "completed"];

const STATUS_COLOR: Record<string, string> = {
  planned: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-gray-100 text-gray-600",
};

const FINDING_CLASS_COLOR: Record<string, string> = {
  major_nc: "bg-red-100 text-red-700",
  minor_nc: "bg-orange-100 text-orange-700",
  observation: "bg-blue-100 text-blue-700",
  opportunity: "bg-green-100 text-green-700",
  positive: "bg-emerald-100 text-emerald-700",
};

// ── Sub components ────────────────────────────────────────────────────────────

function StepBar({ status }: { status: string }) {
  const idx = STATUS_STEPS.indexOf(status);
  return (
    <div className="flex items-center gap-0">
      {STATUS_STEPS.map((s, i) => (
        <div key={s} className="flex items-center">
          <div
            className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold border-2 transition-colors ${
              i < idx
                ? "bg-green-500 border-green-500 text-white"
                : i === idx
                ? "bg-blue-600 border-blue-600 text-white"
                : "bg-white border-gray-300 text-gray-400"
            }`}
          >
            {i < idx ? "✓" : i + 1}
          </div>
          <span
            className={`ml-1.5 text-xs font-medium hidden sm:block ${
              i === idx ? "text-blue-600" : i < idx ? "text-green-600" : "text-gray-400"
            }`}
          >
            {s.replace("_", " ")}
          </span>
          {i < STATUS_STEPS.length - 1 && (
            <div className={`w-12 h-0.5 mx-2 ${i < idx ? "bg-green-400" : "bg-gray-200"}`} />
          )}
        </div>
      ))}
    </div>
  );
}

function InfoRow({
  label,
  value,
  onEdit,
}: {
  label: string;
  value: string | null | undefined;
  onEdit?: (v: string) => void;
}) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? "");

  if (editing && onEdit) {
    return (
      <div className="flex items-center gap-2 py-2 border-b border-gray-100 last:border-0">
        <span className="text-xs text-gray-500 w-32 shrink-0">{label}</span>
        <Input
          autoFocus
          className="h-7 text-sm flex-1"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onBlur={() => {
            onEdit(draft);
            setEditing(false);
          }}
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              onEdit(draft);
              setEditing(false);
            } else if (e.key === "Escape") {
              setEditing(false);
            }
          }}
        />
      </div>
    );
  }

  return (
    <div
      className={`flex items-start gap-2 py-2 border-b border-gray-100 last:border-0 ${onEdit ? "cursor-pointer hover:bg-gray-50 rounded px-1 -mx-1" : ""}`}
      onClick={() => onEdit && setEditing(true)}
    >
      <span className="text-xs text-gray-500 w-32 shrink-0 pt-0.5">{label}</span>
      <span className="text-sm text-gray-900 flex-1">{value || <span className="text-gray-400 italic">—</span>}</span>
    </div>
  );
}

// ── Tabs ─────────────────────────────────────────────────────────────────────

type Tab = "information" | "documentation" | "findings" | "checklist";

const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: "information", label: "Information", icon: Eye },
  { key: "documentation", label: "Documentation", icon: FileText },
  { key: "findings", label: "Findings / Observations", icon: AlertTriangle },
  { key: "checklist", label: "Checklist", icon: ClipboardCheck },
];

// ── Page ─────────────────────────────────────────────────────────────────────

export default function AuditWorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>("information");
  const [showDelete, setShowDelete] = useState(false);
  const [showAddFinding, setShowAddFinding] = useState(false);
  const [showComplete, setShowComplete] = useState(false);
  const [completeSummary, setCompleteSummary] = useState("");

  const { data: audit, isLoading } = useAudit(id);
  const { data: findings = [] } = useAuditFindings(id);
  const updateAudit = useUpdateAudit();
  const startAudit = useStartAudit();
  const completeAudit = useCompleteAudit();
  const deleteAudit = useDeleteAudit();
  const addFinding = useAddAuditFinding();

  const [findingForm, setFindingForm] = useState({
    classification: "observation",
    description: "",
    iso_clause: "",
    response_due_date: "",
  });

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="text-gray-400 text-sm">Loading audit…</div>
      </div>
    );
  }

  if (!audit) {
    return (
      <div className="p-6">
        <div className="text-red-500 text-sm">Audit not found.</div>
        <Link href="/qms/audit/list">
          <Button variant="link" className="mt-2">Back to audits</Button>
        </Link>
      </div>
    );
  }

  async function patch(data: Record<string, unknown>) {
    try {
      await updateAudit.mutateAsync({ id, data });
    } catch {
      toast.error("Failed to save");
    }
  }

  async function handleStart() {
    try {
      await startAudit.mutateAsync(id);
      toast.success("Audit started");
    } catch {
      toast.error("Failed to start audit");
    }
  }

  async function handleComplete() {
    try {
      await completeAudit.mutateAsync({ id, summary: completeSummary || undefined });
      toast.success("Audit completed");
      setShowComplete(false);
    } catch {
      toast.error("Failed to complete audit");
    }
  }

  async function handleDelete() {
    try {
      await deleteAudit.mutateAsync(id);
      toast.success("Audit deleted");
      router.push("/qms/audit/list");
    } catch {
      toast.error("Failed to delete audit");
    }
  }

  async function handleAddFinding() {
    if (!findingForm.description.trim()) {
      toast.error("Description is required");
      return;
    }
    try {
      await addFinding.mutateAsync({
        auditId: id,
        data: {
          classification: findingForm.classification,
          description: findingForm.description,
          iso_clause: findingForm.iso_clause || null,
          response_due_date: findingForm.response_due_date || null,
        },
      });
      toast.success("Finding added");
      setShowAddFinding(false);
      setFindingForm({ classification: "observation", description: "", iso_clause: "", response_due_date: "" });
    } catch {
      toast.error("Failed to add finding");
    }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-gray-200 bg-white">
        <div className="flex items-start gap-4">
          <Link href="/qms/audit/list">
            <Button variant="ghost" size="sm" className="-ml-2">
              <ChevronLeft className="w-4 h-4 mr-1" />
              Audits
            </Button>
          </Link>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3">
              <h1 className="text-lg font-semibold text-gray-900 truncate">{audit.title}</h1>
              <Badge className={`text-xs shrink-0 ${STATUS_COLOR[audit.status] ?? "bg-gray-100 text-gray-600"}`}>
                {audit.status.replace("_", " ")}
              </Badge>
              <Badge className="text-xs shrink-0 bg-gray-100 text-gray-600">{audit.audit_type}</Badge>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{audit.audit_number}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            {audit.status === "planned" && (
              <Button size="sm" onClick={handleStart} disabled={startAudit.isPending} className="bg-yellow-500 hover:bg-yellow-600 text-white">
                <Play className="w-3.5 h-3.5 mr-1.5" />
                Start Audit
              </Button>
            )}
            {audit.status === "in_progress" && (
              <Button size="sm" onClick={() => setShowComplete(true)} className="bg-green-600 hover:bg-green-700 text-white">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                Complete
              </Button>
            )}
            <Button
              size="sm"
              variant="outline"
              className="text-red-600 border-red-200 hover:bg-red-50"
              onClick={() => setShowDelete(true)}
            >
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
        <div className="mt-4">
          <StepBar status={audit.status} />
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white px-6">
        <div className="flex gap-0">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${
                activeTab === key
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-gray-500 hover:text-gray-700"
              }`}
            >
              <Icon className="w-4 h-4" />
              {label}
              {key === "findings" && findings.length > 0 && (
                <span className="ml-1 bg-gray-200 text-gray-600 text-xs rounded-full px-1.5 py-0.5">
                  {findings.length}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === "information" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Audit Details</CardTitle>
              </CardHeader>
              <CardContent>
                <InfoRow label="Audit Number" value={audit.audit_number} />
                <InfoRow label="Title" value={audit.title} onEdit={(v) => patch({ title: v })} />
                <InfoRow label="Audit Type" value={audit.audit_type} />
                <InfoRow label="Status" value={audit.status} />
                <InfoRow label="Score" value={audit.score != null ? String(audit.score) : null} onEdit={(v) => patch({ score: v ? Number(v) : null })} />
              </CardContent>
            </Card>

            <Card className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Scope & Criteria</CardTitle>
              </CardHeader>
              <CardContent>
                <InfoRow label="Scope" value={audit.scope} onEdit={(v) => patch({ scope: v || null })} />
                <InfoRow label="Criteria" value={audit.criteria} onEdit={(v) => patch({ criteria: v || null })} />
                <InfoRow label="Lead Auditor" value={audit.lead_auditor_id} onEdit={(v) => patch({ lead_auditor_id: v || null })} />
                <InfoRow label="Auditee" value={audit.auditee_id} onEdit={(v) => patch({ auditee_id: v || null })} />
              </CardContent>
            </Card>

            <Card className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Schedule</CardTitle>
              </CardHeader>
              <CardContent>
                <InfoRow
                  label="Scheduled Start"
                  value={audit.scheduled_start ? format(new Date(audit.scheduled_start), "PPP") : null}
                  onEdit={(v) => patch({ scheduled_start: v || null })}
                />
                <InfoRow
                  label="Scheduled End"
                  value={audit.scheduled_end ? format(new Date(audit.scheduled_end), "PPP") : null}
                  onEdit={(v) => patch({ scheduled_end: v || null })}
                />
                <InfoRow
                  label="Performed Start"
                  value={audit.performed_start ? format(new Date(audit.performed_start), "PPP") : null}
                />
                <InfoRow
                  label="Performed End"
                  value={audit.performed_end ? format(new Date(audit.performed_end), "PPP") : null}
                />
                <InfoRow label="Created" value={format(new Date(audit.created_at), "PPP")} />
              </CardContent>
            </Card>

            <Card className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Findings Summary</CardTitle>
              </CardHeader>
              <CardContent>
                <InfoRow label="Total Findings" value={String(audit.finding_count)} />
                <InfoRow label="Major NCs" value={String(audit.major_nc_count)} />
                <InfoRow label="Minor NCs" value={String(audit.minor_nc_count)} />
                <InfoRow label="Tags" value={audit.tags.join(", ") || null} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "documentation" && (
          <div className="max-w-3xl space-y-6">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Audit Summary / Report</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <Label className="text-xs text-gray-500">Summary</Label>
                  <Textarea
                    rows={6}
                    className="text-sm resize-none"
                    placeholder="Enter the audit summary, key findings, and overall assessment…"
                    defaultValue={audit.summary ?? ""}
                    onBlur={(e) => patch({ summary: e.target.value || null })}
                  />
                </div>
                {audit.report_file_id && (
                  <p className="text-xs text-gray-500 mt-3">
                    Report file: <span className="font-medium">{audit.report_file_id}</span>
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "findings" && (
          <div className="max-w-4xl space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-gray-700">
                {findings.length} finding{findings.length !== 1 ? "s" : ""}
              </h2>
              {audit.status !== "completed" && (
                <Button size="sm" onClick={() => setShowAddFinding(true)} className="bg-blue-600 hover:bg-blue-700 text-white">
                  <Plus className="w-4 h-4 mr-1.5" />
                  Add Finding
                </Button>
              )}
            </div>
            {findings.length === 0 ? (
              <div className="text-center py-12 text-gray-400 text-sm">
                <AlertTriangle className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                No findings recorded yet
              </div>
            ) : (
              <div className="space-y-3">
                {(findings as AuditFinding[]).map((f) => (
                  <Card key={f.id} className="border border-gray-200">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-gray-500">{f.finding_number}</span>
                            <Badge className={`text-xs ${FINDING_CLASS_COLOR[f.classification] ?? "bg-gray-100 text-gray-600"}`}>
                              {f.classification.replace(/_/g, " ")}
                            </Badge>
                            {f.iso_clause && (
                              <span className="text-xs text-gray-400">§ {f.iso_clause}</span>
                            )}
                          </div>
                          <p className="text-sm text-gray-800">{f.description}</p>
                          {f.auditee_response && (
                            <div className="mt-2 bg-gray-50 rounded p-2">
                              <p className="text-xs text-gray-500 font-medium mb-0.5">Auditee Response</p>
                              <p className="text-xs text-gray-700">{f.auditee_response}</p>
                            </div>
                          )}
                        </div>
                        <div className="text-xs text-gray-400 shrink-0">
                          {format(new Date(f.created_at), "MMM d")}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === "checklist" && (
          <div className="max-w-3xl">
            {!audit.checklist_id ? (
              <div className="text-center py-12 text-gray-400 text-sm">
                <ClipboardCheck className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                <p>No checklist assigned to this audit.</p>
                <Link href="/qms/audit/checklists">
                  <Button variant="link" size="sm" className="mt-2">Browse Checklists</Button>
                </Link>
              </div>
            ) : (
              <p className="text-sm text-gray-600">
                Checklist ID: <span className="font-medium">{audit.checklist_id}</span>
              </p>
            )}
          </div>
        )}
      </div>

      {/* Add Finding Dialog */}
      <Dialog open={showAddFinding} onOpenChange={setShowAddFinding}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Add Finding / Observation</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs">Classification *</Label>
              <Select
                value={findingForm.classification}
                onValueChange={(v) => setFindingForm((f) => ({ ...f, classification: v }))}
              >
                <SelectTrigger className="h-9 text-sm">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="major_nc">Major NC</SelectItem>
                  <SelectItem value="minor_nc">Minor NC</SelectItem>
                  <SelectItem value="observation">Observation</SelectItem>
                  <SelectItem value="opportunity">Opportunity for Improvement</SelectItem>
                  <SelectItem value="positive">Positive Finding</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Description *</Label>
              <Textarea
                className="text-sm resize-none"
                rows={3}
                placeholder="Describe the finding…"
                value={findingForm.description}
                onChange={(e) => setFindingForm((f) => ({ ...f, description: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">ISO Clause</Label>
              <Input
                className="h-9 text-sm"
                placeholder="e.g. 8.5.1"
                value={findingForm.iso_clause}
                onChange={(e) => setFindingForm((f) => ({ ...f, iso_clause: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Response Due Date</Label>
              <Input
                type="date"
                className="h-9 text-sm"
                value={findingForm.response_due_date}
                onChange={(e) => setFindingForm((f) => ({ ...f, response_due_date: e.target.value }))}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowAddFinding(false)}>
              Cancel
            </Button>
            <Button
              size="sm"
              className="bg-blue-600 hover:bg-blue-700 text-white"
              disabled={addFinding.isPending}
              onClick={handleAddFinding}
            >
              {addFinding.isPending ? "Saving…" : "Add Finding"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Complete Dialog */}
      <Dialog open={showComplete} onOpenChange={setShowComplete}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Complete Audit</DialogTitle>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <p className="text-sm text-gray-600">
              Mark this audit as completed. This will finalize the record.
            </p>
            <div className="space-y-1">
              <Label className="text-xs">Summary (optional)</Label>
              <Textarea
                rows={4}
                className="text-sm resize-none"
                placeholder="Overall audit summary…"
                value={completeSummary}
                onChange={(e) => setCompleteSummary(e.target.value)}
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowComplete(false)}>
              Cancel
            </Button>
            <Button
              size="sm"
              className="bg-green-600 hover:bg-green-700 text-white"
              disabled={completeAudit.isPending}
              onClick={handleComplete}
            >
              {completeAudit.isPending ? "Completing…" : "Complete Audit"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirm */}
      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Audit?</AlertDialogTitle>
            <AlertDialogDescription>
              This will permanently delete <strong>{audit.audit_number}</strong> and all its findings. This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-red-600 hover:bg-red-700"
              onClick={handleDelete}
            >
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
