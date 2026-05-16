"use client";

import type { Route } from "next";
import { useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ClipboardList, ArrowLeft, Loader2, Save, X, Plus, Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FBSForm } from "@/components/qms-shared/FBSForm";
import { WorkflowStepBar } from "@/components/qms-shared/WorkflowStepBar";
import { StatusBadge } from "@/components/qms-shared/StatusBadge";
import { SeverityBadge } from "@/components/qms-shared/SeverityBadge";
import { ModuleHeader } from "@/components/qms-shared/ModuleHeader";
import {
  useCAPA, useCAPAActions, useAddCapaAction, useCloseCAPA, useCompleteCapaAction,
  useDeleteCAPA, useUpdateCAPA, useVerifyCapaEffectiveness,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

const LIFECYCLE_STEPS = [
  { key: "open", label: "Open", icon: "📋" },
  { key: "under_investigation", label: "Investigation", icon: "🔍" },
  { key: "root_cause_identified", label: "Root Cause", icon: "🧩" },
  { key: "implementation", label: "Implementation", icon: "⚙️" },
  { key: "effectiveness_check", label: "Effectiveness", icon: "📊" },
  { key: "closed", label: "Closed", icon: "✅" },
];

const STATUS_ORDER = ["open", "under_investigation", "root_cause_identified", "implementation", "effectiveness_check", "closed"];

function getCompletedSteps(status: string): string[] {
  const idx = STATUS_ORDER.indexOf(status);
  return STATUS_ORDER.slice(0, Math.max(0, idx));
}

export default function CapaDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = String(params.id ?? "");
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("capa:read");
  const canWrite = hasPermission("capa:write");
  const canApprove = hasPermission("capa:approve");

  const { data: capa, isLoading, isError, error, refetch } = useCAPA(id);
  const { data: actions = [], isLoading: actionsLoading } = useCAPAActions(id);

  const updateMut = useUpdateCAPA();
  const addActionMut = useAddCapaAction();
  const completeActionMut = useCompleteCapaAction();
  const verifyMut = useVerifyCapaEffectiveness();
  const closeMut = useCloseCAPA();
  const deleteMut = useDeleteCAPA();

  const [editField, setEditField] = useState<string | null>(null);
  const [fieldVal, setFieldVal] = useState("");

  // risk assessment sliders
  const [riskSeverity, setRiskSeverity] = useState(3);
  const [riskOccurrence, setRiskOccurrence] = useState(3);
  const [riskDetectability, setRiskDetectability] = useState(3);
  const rpn = riskSeverity * riskOccurrence * riskDetectability;

  // dialogs
  const [actionOpen, setActionOpen] = useState(false);
  const [actionType, setActionType] = useState("corrective");
  const [actionDesc, setActionDesc] = useState("");
  const [actionAssignedTo, setActionAssignedTo] = useState("");
  const [actionDueDate, setActionDueDate] = useState("");

  const [verifyOpen, setVerifyOpen] = useState(false);
  const [verifyOk, setVerifyOk] = useState(true);
  const [verifyNotes, setVerifyNotes] = useState("");

  const [completeOpen, setCompleteOpen] = useState(false);
  const [completeActionId, setCompleteActionId] = useState<string | null>(null);
  const [completeEvidence, setCompleteEvidence] = useState("");

  const [deleteOpen, setDeleteOpen] = useState(false);

  if (!id) return <p className="p-6 text-muted-foreground">Invalid CAPA.</p>;
  if (permLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" /> Loading…
      </div>
    );
  }
  if (!canRead) return <p className="p-6 text-destructive text-sm">No permission.</p>;
  if (isError) return <p className="p-6 text-destructive text-sm">{handleApiError(error)}</p>;
  if (!capa) return null;

  const closed = capa.status === "closed";
  const allowWrite = canWrite && !closed;
  const allowApprove = canApprove && !closed;

  const saveField = (field: string, value: unknown) => {
    updateMut.mutate({ id, data: { [field]: value } }, {
      onSuccess: () => { toast.success("Saved."); setEditField(null); void refetch(); },
      onError: (e) => toast.error(handleApiError(e)),
    });
  };

  const sourceHref = useMemo(() => {
    if (!capa.source_id) return null;
    const st = (capa.source_type ?? "").toLowerCase();
    if (st.includes("quality") || st === "quality_event") return `/qms/quality-events/${capa.source_id}`;
    if (st.includes("audit")) return `/qms/audit/${capa.source_id}`;
    if (st.includes("complaint")) return `/qms/complaints/${capa.source_id}`;
    return null;
  }, [capa.source_id, capa.source_type]);

  const tabs = [
    {
      id: "about",
      label: "About",
      icon: "📋",
      content: (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3 text-sm">
            {[
              ["CAPA #", <span className="font-mono font-medium" key="n">{capa.capa_number}</span>],
              ["Type", capa.capa_type],
              ["Status", <StatusBadge key="s" status={capa.status} />],
              ["Severity", <SeverityBadge key="sv" severity={capa.severity} />],
              ["Created", new Date(capa.created_at).toLocaleDateString()],
              ["Owner", capa.owner_id ? <span key="o" className="font-mono text-xs">{capa.owner_id}</span> : "—"],
              ["Target Close", capa.target_close_date ? new Date(capa.target_close_date).toLocaleDateString() : "—"],
              ["Actual Close", capa.actual_close_date ? new Date(capa.actual_close_date).toLocaleDateString() : "—"],
            ].map(([label, value]) => (
              <div key={String(label)} className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">{label}</span>
                <span>{value}</span>
              </div>
            ))}
          </div>
          <div>
            <Label>Title</Label>
            {editField === "title" ? (
              <div className="flex gap-2 mt-1">
                <Input value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} autoFocus />
                <Button size="sm" onClick={() => saveField("title", fieldVal)}><Save className="h-4 w-4" /></Button>
                <Button size="sm" variant="ghost" onClick={() => setEditField(null)}><X className="h-4 w-4" /></Button>
              </div>
            ) : (
              <p
                className={`mt-1 p-2 rounded border border-transparent text-sm ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                onClick={() => { if (allowWrite) { setEditField("title"); setFieldVal(capa.title); } }}
              >
                {capa.title}
              </p>
            )}
            <Label className="mt-3">Description</Label>
            {editField === "description" ? (
              <div className="mt-1 space-y-2">
                <Textarea value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} rows={4} autoFocus />
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => saveField("description", fieldVal)}><Save className="h-4 w-4 mr-1" />Save</Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditField(null)}>Cancel</Button>
                </div>
              </div>
            ) : (
              <p
                className={`mt-1 p-2 rounded border border-transparent text-sm whitespace-pre-wrap ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                onClick={() => { if (allowWrite) { setEditField("description"); setFieldVal(capa.description ?? ""); } }}
              >
                {capa.description || <span className="text-muted-foreground italic">Click to add…</span>}
              </p>
            )}
          </div>
        </div>
      ),
    },
    {
      id: "source",
      label: "Source",
      icon: "🔗",
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Source Type</Label>
              <p className="mt-1 p-2 text-sm capitalize">{capa.source_type?.replace(/_/g, " ") ?? "—"}</p>
            </div>
            <div>
              <Label>Source Reference</Label>
              {sourceHref ? (
                <Button size="sm" variant="outline" className="mt-1" asChild>
                  <a href={sourceHref as Route}>View Source Record ↗</a>
                </Button>
              ) : (
                <p className="mt-1 p-2 text-sm font-mono text-xs">{capa.source_id ?? "—"}</p>
              )}
            </div>
          </div>
        </div>
      ),
    },
    {
      id: "risk",
      label: "Risk Assessment",
      icon: "⚠️",
      content: (
        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-3">
            {[
              ["Severity", riskSeverity, setRiskSeverity],
              ["Occurrence", riskOccurrence, setRiskOccurrence],
              ["Detectability", riskDetectability, setRiskDetectability],
            ].map(([label, val, setter]) => (
              <div key={String(label)}>
                <Label>{String(label)} (1–5)</Label>
                <div className="flex items-center gap-3 mt-2">
                  <input
                    type="range"
                    min={1}
                    max={5}
                    value={Number(val)}
                    onChange={(e) => (setter as React.Dispatch<React.SetStateAction<number>>)(Number(e.target.value))}
                    className="flex-1"
                    disabled={!allowWrite}
                  />
                  <span className="font-bold text-lg w-6 text-center">{String(val)}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="flex items-center gap-4 p-4 rounded-lg border bg-muted/30">
            <div className="text-center">
              <p className="text-xs text-muted-foreground">RPN</p>
              <p className={`text-3xl font-bold ${rpn > 60 ? "text-red-600" : rpn > 30 ? "text-amber-500" : "text-emerald-600"}`}>
                {rpn}
              </p>
              <p className="text-xs text-muted-foreground">= {riskSeverity} × {riskOccurrence} × {riskDetectability}</p>
            </div>
            <div className="text-sm text-muted-foreground">
              <p>{rpn > 60 ? "🔴 High Risk — immediate action required" : rpn > 30 ? "🟡 Medium Risk — monitor closely" : "🟢 Low Risk — standard controls sufficient"}</p>
            </div>
          </div>
          {allowWrite && (
            <Button
              size="sm"
              onClick={() => saveField("risk_score", rpn)}
            >
              <Save className="h-4 w-4 mr-1" /> Save Risk Assessment
            </Button>
          )}
        </div>
      ),
    },
    {
      id: "investigation",
      label: "Investigation",
      icon: "🔍",
      content: (
        <div className="space-y-4">
          <div>
            <Label>Root Cause Method</Label>
            {editField === "root_cause_method" ? (
              <div className="flex gap-2 mt-1">
                <Input value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} placeholder="e.g. 5-Why, Fishbone" autoFocus />
                <Button size="sm" onClick={() => saveField("root_cause_method", fieldVal)}><Save className="h-4 w-4" /></Button>
                <Button size="sm" variant="ghost" onClick={() => setEditField(null)}><X className="h-4 w-4" /></Button>
              </div>
            ) : (
              <p
                className={`mt-1 p-2 rounded border border-transparent text-sm ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                onClick={() => { if (allowWrite) { setEditField("root_cause_method"); setFieldVal(capa.root_cause_method ?? ""); } }}
              >
                {capa.root_cause_method || <span className="text-muted-foreground italic">Click to set method…</span>}
              </p>
            )}
          </div>
          <div>
            <Label>Root Cause</Label>
            {editField === "root_cause" ? (
              <div className="mt-1 space-y-2">
                <Textarea value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} rows={5} autoFocus />
                <div className="flex gap-2">
                  <Button size="sm" onClick={() => saveField("root_cause", fieldVal)}><Save className="h-4 w-4 mr-1" />Save</Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditField(null)}>Cancel</Button>
                </div>
              </div>
            ) : (
              <p
                className={`mt-1 p-2 rounded border border-transparent text-sm whitespace-pre-wrap min-h-[80px] ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                onClick={() => { if (allowWrite) { setEditField("root_cause"); setFieldVal(capa.root_cause ?? ""); } }}
              >
                {capa.root_cause || <span className="text-muted-foreground italic">Click to document root cause…</span>}
              </p>
            )}
          </div>
        </div>
      ),
    },
    {
      id: "action-plan",
      label: "Action Plan",
      icon: "📋",
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">CAPA Actions ({actions.length})</h3>
            {allowWrite && (
              <Button size="sm" onClick={() => setActionOpen(true)}>
                <Plus className="h-4 w-4 mr-1" /> Add Action
              </Button>
            )}
          </div>
          {actionsLoading ? (
            <div className="flex items-center gap-2 text-muted-foreground text-sm"><Loader2 className="h-4 w-4 animate-spin" />Loading…</div>
          ) : actions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No actions yet. Add corrective or preventive actions above.</p>
          ) : (
            <div className="space-y-3">
              {actions.map((a) => (
                <Card key={a.id}>
                  <CardContent className="pt-4">
                    <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={a.action_type === "corrective" ? "default" : "secondary"} className="text-xs">
                            {a.action_type}
                          </Badge>
                          <Badge variant={a.status === "completed" ? "outline" : "secondary"} className="text-xs capitalize">
                            {a.status}
                          </Badge>
                        </div>
                        <p className="text-sm">{a.description}</p>
                        {a.assigned_to && <p className="text-xs text-muted-foreground mt-1">Assigned: {a.assigned_to}</p>}
                        {a.due_date && <p className="text-xs text-muted-foreground">Due: {new Date(a.due_date).toLocaleDateString()}</p>}
                        {a.completed_at && <p className="text-xs text-emerald-600">Completed: {new Date(a.completed_at).toLocaleDateString()}</p>}
                      </div>
                      {allowWrite && a.status !== "completed" && (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => { setCompleteActionId(a.id); setCompleteOpen(true); }}
                        >
                          Complete
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      ),
    },
    {
      id: "implementation",
      label: "Implementation",
      icon: "⚙️",
      content: (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Track completion of each action item. Use the Action Plan tab to mark actions complete with evidence.
          </p>
          <div className="space-y-2">
            {actions.map((a) => (
              <div key={a.id} className="flex items-center gap-3 p-3 rounded-lg border">
                <span className={`text-lg ${a.status === "completed" ? "text-emerald-600" : "text-slate-400"}`}>
                  {a.status === "completed" ? "✅" : "⬜"}
                </span>
                <div className="flex-1">
                  <p className="text-sm font-medium">{a.description}</p>
                  {a.evidence && <p className="text-xs text-muted-foreground mt-1">Evidence: {a.evidence}</p>}
                </div>
              </div>
            ))}
            {actions.length === 0 && (
              <p className="text-sm text-muted-foreground italic">No actions defined yet.</p>
            )}
          </div>
        </div>
      ),
    },
    {
      id: "effectiveness",
      label: "Effectiveness",
      icon: "📊",
      content: (
        <div className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Verify that corrective actions have been effective after implementation.
          </p>
          {capa.effectiveness_verified !== undefined && capa.effectiveness_verified !== null ? (
            <Card>
              <CardContent className="pt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className={capa.effectiveness_verified ? "text-emerald-600 font-medium" : "text-red-600 font-medium"}>
                    {capa.effectiveness_verified ? "✅ Effective" : "❌ Not Effective"}
                  </span>
                </div>
                {capa.effectiveness_check_date && (
                  <p className="text-xs text-muted-foreground">Checked: {new Date(capa.effectiveness_check_date).toLocaleString()}</p>
                )}
              </CardContent>
            </Card>
          ) : (
            <p className="text-sm text-muted-foreground italic">Effectiveness not yet verified.</p>
          )}
          {allowApprove && (
            <Button size="sm" variant="outline" onClick={() => setVerifyOpen(true)}>
              Verify Effectiveness
            </Button>
          )}
        </div>
      ),
    },
    {
      id: "closure",
      label: "Closure",
      icon: "🔒",
      content: (
        <div className="space-y-4">
          {closed ? (
            <Card>
              <CardContent className="pt-4">
                <div className="flex items-center gap-2">
                  <span className="text-emerald-600 font-bold text-lg">✅</span>
                  <div>
                    <p className="font-medium">CAPA Closed</p>
                    {capa.actual_close_date && (
                      <p className="text-xs text-muted-foreground">{new Date(capa.actual_close_date).toLocaleDateString()}</p>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                Closing a CAPA requires effectiveness verification. Ensure all actions are complete before closing.
              </p>
              {allowApprove && (
                <Button
                  onClick={() => closeMut.mutate(id, {
                    onSuccess: () => { toast.success("CAPA closed."); void refetch(); },
                    onError: (e) => toast.error(handleApiError(e)),
                  })}
                  disabled={closeMut.isPending}
                >
                  {closeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : "🔒"} Close CAPA
                </Button>
              )}
            </>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={() => router.push("/qms/capa" as Route)}>
          <ArrowLeft className="h-3 w-3 mr-1" />CAPA
        </Button>
        <span>/</span>
        <span className="font-mono text-xs text-foreground">{capa.capa_number}</span>
      </div>

      {/* Header */}
      <ModuleHeader
        icon={<ClipboardList className="h-6 w-6" />}
        title={capa.title}
        description={capa.capa_number}
        actions={
          <div className="flex flex-wrap gap-2">
            <StatusBadge status={capa.status} />
            <SeverityBadge severity={capa.severity} />
            {canWrite && (
              <Button size="sm" variant="destructive" onClick={() => setDeleteOpen(true)}>
                <Trash2 className="h-4 w-4 mr-1" />Delete
              </Button>
            )}
          </div>
        }
      />

      {/* 6-step lifecycle bar */}
      <WorkflowStepBar
        steps={LIFECYCLE_STEPS}
        currentStep={capa.status}
        completedSteps={getCompletedSteps(capa.status)}
      />

      {/* FBS Tabbed Form */}
      <FBSForm tabs={tabs} defaultTab="about" />

      {/* Add Action dialog */}
      <Dialog open={actionOpen} onOpenChange={setActionOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Add CAPA Action</DialogTitle></DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label>Action Type</Label>
              <Select value={actionType} onValueChange={setActionType}>
                <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="corrective">Corrective</SelectItem>
                  <SelectItem value="preventive">Preventive</SelectItem>
                  <SelectItem value="systemic">Systemic</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Description *</Label>
              <Textarea value={actionDesc} onChange={(e) => setActionDesc(e.target.value)} rows={3} className="mt-1" />
            </div>
            <div>
              <Label>Assigned To</Label>
              <Input value={actionAssignedTo} onChange={(e) => setActionAssignedTo(e.target.value)} className="mt-1" placeholder="User ID or name" />
            </div>
            <div>
              <Label>Due Date</Label>
              <Input type="date" value={actionDueDate} onChange={(e) => setActionDueDate(e.target.value)} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setActionOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                if (!actionDesc.trim()) return toast.error("Description required.");
                addActionMut.mutate(
                  { capaId: id, data: { action_type: actionType, description: actionDesc.trim(), assigned_to: actionAssignedTo || null, due_date: actionDueDate || null } },
                  {
                    onSuccess: () => { toast.success("Action added."); setActionOpen(false); setActionDesc(""); setActionAssignedTo(""); setActionDueDate(""); },
                    onError: (e) => toast.error(handleApiError(e)),
                  },
                );
              }}
              disabled={addActionMut.isPending}
            >
              {addActionMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}Add
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Complete action dialog */}
      <Dialog open={completeOpen} onOpenChange={setCompleteOpen}>
        <DialogContent>
          <DialogHeader><DialogTitle>Complete Action</DialogTitle></DialogHeader>
          <div className="py-2">
            <Label>Evidence / Notes</Label>
            <Textarea value={completeEvidence} onChange={(e) => setCompleteEvidence(e.target.value)} rows={3} className="mt-1" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCompleteOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                if (!completeActionId) return;
                completeActionMut.mutate(
                  { capaId: id, actionId: completeActionId, data: { evidence: completeEvidence || null } },
                  {
                    onSuccess: () => { toast.success("Action completed."); setCompleteOpen(false); setCompleteActionId(null); setCompleteEvidence(""); },
                    onError: (e) => toast.error(handleApiError(e)),
                  },
                );
              }}
              disabled={completeActionMut.isPending}
            >
              {completeActionMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}Complete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Verify effectiveness dialog */}
      <Dialog open={verifyOpen} onOpenChange={setVerifyOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Verify Effectiveness</DialogTitle>
            <DialogDescription>Record the outcome of the effectiveness check.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <label className="flex items-center gap-2 text-sm cursor-pointer">
              <input type="checkbox" checked={verifyOk} onChange={(e) => setVerifyOk(e.target.checked)} className="h-4 w-4 rounded" />
              Mark as effective
            </label>
            <div>
              <Label>Notes</Label>
              <Textarea value={verifyNotes} onChange={(e) => setVerifyNotes(e.target.value)} rows={3} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setVerifyOpen(false)}>Cancel</Button>
            <Button
              onClick={() => verifyMut.mutate({ id, data: { verified: verifyOk, notes: verifyNotes || null } }, {
                onSuccess: () => { toast.success("Effectiveness recorded."); setVerifyOpen(false); void refetch(); },
                onError: (e) => toast.error(handleApiError(e)),
              })}
              disabled={verifyMut.isPending}
            >
              {verifyMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}Submit
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete dialog */}
      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete CAPA</AlertDialogTitle>
            <AlertDialogDescription>
              Delete <strong>{capa.capa_number}</strong>? This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMut.isPending}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={(e: React.MouseEvent) => {
                e.preventDefault();
                deleteMut.mutate(id, {
                  onSuccess: () => { toast.success("Deleted."); router.push("/qms/capa" as Route); },
                  onError: (e) => toast.error(handleApiError(e)),
                });
              }}
              disabled={deleteMut.isPending}
            >
              {deleteMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
