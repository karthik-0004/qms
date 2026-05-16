"use client";

import type { Route } from "next";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  AlertTriangle, ArrowLeft, Loader2, Save, X, Plus, ChevronRight
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
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent } from "@/components/ui/card";
import { FBSForm } from "@/components/qms-shared/FBSForm";
import { WorkflowStepBar } from "@/components/qms-shared/WorkflowStepBar";
import { StatusBadge } from "@/components/qms-shared/StatusBadge";
import { SeverityBadge } from "@/components/qms-shared/SeverityBadge";
import { ModuleHeader } from "@/components/qms-shared/ModuleHeader";
import {
  useQualityEvent, useUpdateQualityEvent, useCloseQualityEvent,
  useDeleteQualityEvent, useCreateCAPA,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

const QE_STEPS = [
  { key: "open", label: "Open", icon: "📋" },
  { key: "investigating", label: "Investigating", icon: "🔍" },
  { key: "pending_capa", label: "Pending CAPA", icon: "⚡" },
  { key: "closed", label: "Closed", icon: "✅" },
];

const EVENT_TYPES = ["deviation", "non_conformance", "oos", "oot", "nc_work", "observation"];
const SEVERITIES = ["critical", "major", "minor", "observation"];
const PRIORITIES = ["high", "medium", "low"];
const RCA_TOOLS = ["5_why", "fishbone", "fault_tree", "pareto", "manual"];

function RootCauseTab({
  ev, canWrite, onSave,
}: {
  ev: { root_cause?: string | null; immediate_action?: string | null };
  canWrite: boolean;
  onSave: (data: Record<string, unknown>) => void;
}) {
  const [tool, setTool] = useState("5_why");
  const [whys, setWhys] = useState(["", "", "", "", ""]);
  const [fishbone, setFishbone] = useState({
    machine: "", method: "", material: "", man: "", measurement: "", environment: "",
  });
  const [summary, setSummary] = useState(ev.root_cause ?? "");
  const [immediateAction, setImmediateAction] = useState(ev.immediate_action ?? "");

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2">
        <div>
          <Label>RCA Tool</Label>
          <Select value={tool} onValueChange={setTool}>
            <SelectTrigger className="mt-1">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="5_why">5-Why</SelectItem>
              <SelectItem value="fishbone">Fishbone (Ishikawa)</SelectItem>
              <SelectItem value="fault_tree">Fault Tree</SelectItem>
              <SelectItem value="pareto">Pareto Analysis</SelectItem>
              <SelectItem value="manual">Manual Analysis</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {tool === "5_why" && (
        <div className="space-y-3">
          <p className="text-sm font-medium">5-Why Analysis</p>
          {whys.map((w, i) => (
            <div key={i} className="flex items-start gap-3">
              <span className="mt-2 text-sm font-bold text-muted-foreground w-16 shrink-0">Why {i + 1}:</span>
              <Input
                value={w}
                onChange={(e) => {
                  const next = [...whys];
                  next[i] = e.target.value;
                  setWhys(next);
                }}
                placeholder={`Why ${i + 1}...`}
                disabled={!canWrite}
              />
              {i < whys.length - 1 && (
                <ChevronRight className="h-4 w-4 mt-2 text-muted-foreground shrink-0" />
              )}
            </div>
          ))}
        </div>
      )}

      {tool === "fishbone" && (
        <div className="grid gap-3 md:grid-cols-2">
          {Object.entries(fishbone).map(([key, val]) => (
            <div key={key}>
              <Label className="capitalize">{key}</Label>
              <Textarea
                value={val}
                onChange={(e) => setFishbone((f) => ({ ...f, [key]: e.target.value }))}
                rows={2}
                className="mt-1"
                disabled={!canWrite}
              />
            </div>
          ))}
        </div>
      )}

      <div>
        <Label>Immediate Action Taken</Label>
        <Textarea
          value={immediateAction}
          onChange={(e) => setImmediateAction(e.target.value)}
          rows={2}
          className="mt-1"
          placeholder="Describe any immediate containment actions taken..."
          disabled={!canWrite}
        />
      </div>

      <div>
        <Label>Root Cause Summary *</Label>
        <Textarea
          value={summary}
          onChange={(e) => setSummary(e.target.value)}
          rows={4}
          className="mt-1"
          placeholder="Summarize the identified root cause..."
          disabled={!canWrite}
        />
      </div>

      {canWrite && (
        <Button
          onClick={() => onSave({ root_cause: summary, immediate_action: immediateAction })}
          size="sm"
        >
          <Save className="h-4 w-4 mr-1" /> Save Root Cause
        </Button>
      )}
    </div>
  );
}

export default function QualityEventDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = String(params.id ?? "");
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("quality_event:read");
  const canWrite = hasPermission("quality_event:write");

  const { data: ev, isLoading, isError, error, refetch } = useQualityEvent(id);
  const updateMut = useUpdateQualityEvent();
  const closeMut = useCloseQualityEvent();
  const deleteMut = useDeleteQualityEvent();
  const createCapaMut = useCreateCAPA();

  // edit state for inline fields
  const [editField, setEditField] = useState<string | null>(null);
  const [fieldVal, setFieldVal] = useState("");

  // dialogs
  const [closeOpen, setCloseOpen] = useState(false);
  const [resolution, setResolution] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [escalateOpen, setEscalateOpen] = useState(false);
  const [capaTitle, setCapaTitle] = useState("");
  const [capaDesc, setCapaDesc] = useState("");

  if (!id) return <p className="p-6 text-muted-foreground">Invalid event.</p>;
  if (permLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" /> Loading…
      </div>
    );
  }
  if (!canRead) return <p className="p-6 text-destructive text-sm">No permission.</p>;
  if (isError) return <p className="p-6 text-destructive text-sm">{handleApiError(error)}</p>;
  if (!ev) return null;

  const closed = ev.status === "closed";
  const allowWrite = canWrite && !closed;

  const saveField = (field: string, value: unknown) => {
    updateMut.mutate(
      { id: ev.id, data: { [field]: value } },
      {
        onSuccess: () => { toast.success("Saved."); setEditField(null); void refetch(); },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onEscalate = () => {
    if (!capaTitle.trim()) return toast.error("Title required.");
    createCapaMut.mutate(
      {
        capa_number: `CAPA-${Date.now()}`,
        title: capaTitle.trim(),
        description: capaDesc.trim(),
        source_type: "quality_event",
        source_id: ev.id,
        severity: ev.severity,
      },
      {
        onSuccess: async (capa) => {
          await updateMut.mutateAsync({ id: ev.id, data: { capa_id: capa.id, capa_required: true } });
          toast.success("CAPA created and linked.");
          setEscalateOpen(false);
          void refetch();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const tabs = [
    {
      id: "about",
      label: "About",
      icon: "📋",
      content: (
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-3 text-sm">
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Form #</span>
              <span className="font-mono font-medium">{ev.event_number}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Status</span>
              <StatusBadge status={ev.status} />
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Severity</span>
              <SeverityBadge severity={ev.severity} />
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-muted-foreground">Created</span>
              <span>{new Date(ev.created_at).toLocaleDateString()}</span>
            </div>
            {ev.due_date && (
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Due Date</span>
                <span className="text-amber-600 font-medium">{new Date(ev.due_date).toLocaleDateString()}</span>
              </div>
            )}
            {ev.closed_at && (
              <div className="flex justify-between border-b pb-2">
                <span className="text-muted-foreground">Closed At</span>
                <span>{new Date(ev.closed_at).toLocaleDateString()}</span>
              </div>
            )}
          </div>
          {ev.capa_id && (
            <Card>
              <CardContent className="pt-4">
                <p className="text-sm font-medium mb-2">Linked CAPA</p>
                <Button size="sm" variant="outline" asChild>
                  <a href={`/qms/capa/${ev.capa_id}` as Route}>Open CAPA ↗</a>
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      ),
    },
    {
      id: "event-info",
      label: "Event Information",
      icon: "⚠️",
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
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
                  onClick={() => { if (allowWrite) { setEditField("title"); setFieldVal(ev.title); } }}
                >
                  {ev.title}
                </p>
              )}
            </div>
            <div>
              <Label>Event Type</Label>
              {allowWrite ? (
                <Select defaultValue={ev.event_type} onValueChange={(v) => saveField("event_type", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {EVENT_TYPES.map((t) => <SelectItem key={t} value={t}>{t.replace(/_/g, " ").toUpperCase()}</SelectItem>)}
                  </SelectContent>
                </Select>
              ) : (
                <p className="mt-1 p-2 text-sm">{ev.event_type}</p>
              )}
            </div>
            <div>
              <Label>Severity</Label>
              {allowWrite ? (
                <Select defaultValue={ev.severity} onValueChange={(v) => saveField("severity", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {SEVERITIES.map((s) => <SelectItem key={s} value={s}>{s}</SelectItem>)}
                  </SelectContent>
                </Select>
              ) : (
                <div className="mt-1"><SeverityBadge severity={ev.severity} /></div>
              )}
            </div>
            <div>
              <Label>Priority</Label>
              {allowWrite ? (
                <Select defaultValue={ev.priority ?? "medium"} onValueChange={(v) => saveField("priority", v)}>
                  <SelectTrigger className="mt-1"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {PRIORITIES.map((p) => <SelectItem key={p} value={p}>{p}</SelectItem>)}
                  </SelectContent>
                </Select>
              ) : (
                <p className="mt-1 p-2 text-sm">{ev.priority ?? "—"}</p>
              )}
            </div>
            <div>
              <Label>Department</Label>
              {editField === "department" ? (
                <div className="flex gap-2 mt-1">
                  <Input value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} autoFocus />
                  <Button size="sm" onClick={() => saveField("department", fieldVal)}><Save className="h-4 w-4" /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditField(null)}><X className="h-4 w-4" /></Button>
                </div>
              ) : (
                <p
                  className={`mt-1 p-2 rounded border border-transparent text-sm ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                  onClick={() => { if (allowWrite) { setEditField("department"); setFieldVal(ev.department ?? ""); } }}
                >
                  {ev.department ?? "—"}
                </p>
              )}
            </div>
            <div>
              <Label>Location</Label>
              {editField === "location" ? (
                <div className="flex gap-2 mt-1">
                  <Input value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} autoFocus />
                  <Button size="sm" onClick={() => saveField("location", fieldVal)}><Save className="h-4 w-4" /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditField(null)}><X className="h-4 w-4" /></Button>
                </div>
              ) : (
                <p
                  className={`mt-1 p-2 rounded border border-transparent text-sm ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                  onClick={() => { if (allowWrite) { setEditField("location"); setFieldVal((ev as { location?: string | null }).location ?? ""); } }}
                >
                  {(ev as { location?: string | null }).location ?? "—"}
                </p>
              )}
            </div>
            <div>
              <Label>Detected At</Label>
              <p className="mt-1 p-2 text-sm">{new Date(ev.detected_at).toLocaleString()}</p>
            </div>
            <div>
              <Label>Detected By</Label>
              <p className="mt-1 p-2 text-sm font-mono text-xs">{ev.detected_by ?? "—"}</p>
            </div>
          </div>
          <div>
            <Label>Description</Label>
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
                onClick={() => { if (allowWrite) { setEditField("description"); setFieldVal(ev.description ?? ""); } }}
              >
                {ev.description || <span className="text-muted-foreground italic">Click to add description…</span>}
              </p>
            )}
          </div>
          {(ev.tags as string[] | undefined)?.length ? (
            <div>
              <Label>Tags</Label>
              <div className="flex flex-wrap gap-1 mt-1">
                {(ev.tags as string[]).map((t) => <Badge key={t} variant="secondary">{t}</Badge>)}
              </div>
            </div>
          ) : null}
        </div>
      ),
    },
    {
      id: "investigation",
      label: "Investigation",
      icon: "🔍",
      content: (
        <div className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label>Assigned Investigator</Label>
              {editField === "assigned_to" ? (
                <div className="flex gap-2 mt-1">
                  <Input value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} placeholder="User ID" autoFocus />
                  <Button size="sm" onClick={() => saveField("assigned_to", fieldVal)}><Save className="h-4 w-4" /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditField(null)}><X className="h-4 w-4" /></Button>
                </div>
              ) : (
                <p
                  className={`mt-1 p-2 rounded border border-transparent text-sm font-mono ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                  onClick={() => { if (allowWrite) { setEditField("assigned_to"); setFieldVal(ev.assigned_to ?? ""); } }}
                >
                  {ev.assigned_to ?? <span className="text-muted-foreground not-italic font-sans">Unassigned — click to assign</span>}
                </p>
              )}
            </div>
            <div>
              <Label>Due Date</Label>
              {editField === "due_date" ? (
                <div className="flex gap-2 mt-1">
                  <Input type="date" value={fieldVal} onChange={(e) => setFieldVal(e.target.value)} autoFocus />
                  <Button size="sm" onClick={() => saveField("due_date", fieldVal)}><Save className="h-4 w-4" /></Button>
                  <Button size="sm" variant="ghost" onClick={() => setEditField(null)}><X className="h-4 w-4" /></Button>
                </div>
              ) : (
                <p
                  className={`mt-1 p-2 rounded border border-transparent text-sm ${allowWrite ? "hover:border-border cursor-pointer" : ""}`}
                  onClick={() => { if (allowWrite) { setEditField("due_date"); setFieldVal(ev.due_date?.slice(0, 10) ?? ""); } }}
                >
                  {ev.due_date ? new Date(ev.due_date).toLocaleDateString() : <span className="text-muted-foreground italic">Set due date…</span>}
                </p>
              )}
            </div>
          </div>
          <p className="text-sm text-muted-foreground italic">Investigation notes and findings are captured in the Root Cause tab.</p>
        </div>
      ),
    },
    {
      id: "root-cause",
      label: "Root Cause",
      icon: "🧩",
      content: (
        <RootCauseTab
          ev={ev}
          canWrite={!!allowWrite}
          onSave={(data) =>
            updateMut.mutate({ id: ev.id, data }, {
              onSuccess: () => { toast.success("Root cause saved."); void refetch(); },
              onError: (e) => toast.error(handleApiError(e)),
            })
          }
        />
      ),
    },
    {
      id: "action-items",
      label: "Action Items",
      icon: "⚡",
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Corrective Actions</h3>
            {allowWrite && !ev.capa_id && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setCapaTitle(`CAPA: ${ev.title}`);
                  setCapaDesc(ev.description ?? "");
                  setEscalateOpen(true);
                }}
              >
                <Plus className="h-4 w-4 mr-1" /> Escalate to CAPA
              </Button>
            )}
          </div>
          {ev.capa_id ? (
            <Card>
              <CardContent className="pt-4 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium">CAPA Linked</p>
                  <p className="text-xs text-muted-foreground font-mono mt-1">{ev.capa_id}</p>
                </div>
                <Button size="sm" variant="outline" asChild>
                  <a href={`/qms/capa/${ev.capa_id}` as Route}>Open CAPA ↗</a>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <p className="text-sm text-muted-foreground">
              {ev.capa_required ? "CAPA required — not yet created." : "No actions escalated to CAPA yet."}
            </p>
          )}
        </div>
      ),
    },
    {
      id: "communications",
      label: "Communications Log",
      icon: "💬",
      content: (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Append-only log of communications related to this event.
          </p>
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground italic">No communications logged yet.</p>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: "resolution",
      label: "Resolution",
      icon: "✅",
      content: (
        <div className="space-y-4">
          {ev.status === "closed" ? (
            <Card>
              <CardContent className="pt-4 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-emerald-600 font-medium">Event Closed</span>
                  <Badge variant="secondary">{new Date(ev.closed_at!).toLocaleDateString()}</Badge>
                </div>
              </CardContent>
            </Card>
          ) : (
            <>
              <div>
                <Label>Resolution Summary</Label>
                <Textarea
                  value={resolution}
                  onChange={(e) => setResolution(e.target.value)}
                  rows={4}
                  className="mt-1"
                  placeholder="Describe how this event was resolved…"
                  disabled={!allowWrite}
                />
              </div>
              {allowWrite && (
                <Button
                  onClick={() => setCloseOpen(true)}
                  variant="default"
                >
                  ✅ Close Event
                </Button>
              )}
            </>
          )}
        </div>
      ),
    },
  ];

  const currentStepKey = ev.status === "open" ? "open"
    : ev.status === "investigating" ? "investigating"
    : ev.status === "pending_capa" ? "pending_capa"
    : "closed";

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={() => router.push("/qms/quality-events" as Route)}>
          <ArrowLeft className="h-3 w-3 mr-1" />Quality Events
        </Button>
        <span>/</span>
        <span className="font-mono text-xs text-foreground">{ev.event_number}</span>
      </div>

      {/* Header */}
      <ModuleHeader
        icon={<AlertTriangle className="h-6 w-6" />}
        title={ev.title}
        description={ev.event_number}
        actions={
          <div className="flex flex-wrap gap-2">
            <StatusBadge status={ev.status} />
            <SeverityBadge severity={ev.severity} />
            {canWrite && (
              <Button size="sm" variant="destructive" onClick={() => setDeleteOpen(true)}>Delete</Button>
            )}
          </div>
        }
      />

      {/* Workflow Step Bar */}
      <WorkflowStepBar
        steps={QE_STEPS}
        currentStep={currentStepKey}
        completedSteps={
          currentStepKey === "investigating" ? ["open"]
          : currentStepKey === "pending_capa" ? ["open", "investigating"]
          : currentStepKey === "closed" ? ["open", "investigating", "pending_capa"]
          : []
        }
      />

      {/* FBS Tabbed Form */}
      <FBSForm tabs={tabs} defaultTab="about" />

      {/* Escalate to CAPA dialog */}
      <Dialog open={escalateOpen} onOpenChange={setEscalateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Escalate to CAPA</DialogTitle>
            <DialogDescription>Create a CAPA linked to this quality event.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label>CAPA Title *</Label>
              <Input value={capaTitle} onChange={(e) => setCapaTitle(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={capaDesc} onChange={(e) => setCapaDesc(e.target.value)} rows={3} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEscalateOpen(false)}>Cancel</Button>
            <Button onClick={onEscalate} disabled={createCapaMut.isPending || updateMut.isPending}>
              {createCapaMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              Create CAPA
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Close dialog */}
      <Dialog open={closeOpen} onOpenChange={setCloseOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Close Quality Event</DialogTitle>
          </DialogHeader>
          <div className="py-2">
            <Label>Resolution</Label>
            <Textarea value={resolution} onChange={(e) => setResolution(e.target.value)} rows={3} className="mt-1" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCloseOpen(false)}>Cancel</Button>
            <Button
              onClick={() => closeMut.mutate({ id: ev.id, resolution: resolution || null }, {
                onSuccess: () => { toast.success("Event closed."); setCloseOpen(false); void refetch(); },
                onError: (e) => toast.error(handleApiError(e)),
              })}
              disabled={closeMut.isPending}
            >
              {closeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              Close Event
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Quality Event</DialogTitle>
            <DialogDescription>This cannot be undone.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>Cancel</Button>
            <Button
              variant="destructive"
              disabled={deleteMut.isPending}
              onClick={() => deleteMut.mutate(ev.id, {
                onSuccess: () => { toast.success("Deleted."); router.push("/qms/quality-events" as Route); },
                onError: (e) => toast.error(handleApiError(e)),
              })}
            >
              {deleteMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
