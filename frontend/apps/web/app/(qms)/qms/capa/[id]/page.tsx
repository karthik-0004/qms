"use client";

import Link from "next/link";
import type { Route } from "next";
import { useMemo, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft,
  ClipboardList,
  Home,
  Loader2,
  CheckCircle2,
  Circle,
  Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  useCAPA,
  useCAPAActions,
  useAddCapaAction,
  useCloseCAPA,
  useCompleteCapaAction,
  useDeleteCAPA,
  useUpdateCAPA,
  useVerifyCapaEffectiveness,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

const LIFECYCLE_STEPS = [
  { status: "open", label: "Open" },
  { status: "under_investigation", label: "Investigation" },
  { status: "root_cause_identified", label: "Root cause" },
  { status: "implementation", label: "Implementation" },
  { status: "effectiveness_check", label: "Effectiveness" },
  { status: "closed", label: "Closed" },
] as const;

function stepIndexForStatus(status: string): number {
  const i = LIFECYCLE_STEPS.findIndex((s) => s.status === status);
  return i === -1 ? 0 : i;
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

  const [rootCauseOpen, setRootCauseOpen] = useState(false);
  const [rootCause, setRootCause] = useState("");
  const [rootMethod, setRootMethod] = useState("");
  const [actionOpen, setActionOpen] = useState(false);
  const [actionType, setActionType] = useState("corrective");
  const [actionDesc, setActionDesc] = useState("");
  const [verifyOpen, setVerifyOpen] = useState(false);
  const [verifyOk, setVerifyOk] = useState(true);
  const [verifyNotes, setVerifyNotes] = useState("");
  const [completeOpen, setCompleteOpen] = useState(false);
  const [completeActionId, setCompleteActionId] = useState<string | null>(null);
  const [completeEvidence, setCompleteEvidence] = useState("");

  const [deleteOpen, setDeleteOpen] = useState(false);

  const onDeleteConfirm = () => {
    deleteMut.mutate(id, {
      onSuccess: () => {
        toast.success("CAPA deleted");
        router.push("/qms/capa" as Route);
      },
      onError: (e) => toast.error(`Failed to delete CAPA: ${handleApiError(e)}`),
    });
  };

  const closed = capa?.status === "closed";
  const currentStep = capa ? stepIndexForStatus(capa.status) : 0;

  const allowWrite = canWrite && !closed;
  const allowApprove = canApprove && !closed;

  const sourceQeHref = useMemo(() => {
    if (!capa?.source_id) return null;
    const st = (capa.source_type ?? "").toLowerCase();
    if (st.includes("quality") || st === "quality_event") {
      return `/qms/quality-events/${capa.source_id}` as Route;
    }
    return null;
  }, [capa?.source_id, capa?.source_type]);

  if (!id) {
    return <p className="p-6 text-muted-foreground">Invalid CAPA.</p>;
  }

  if (permLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading…
      </div>
    );
  }

  if (!canRead) {
    return <p className="p-6 text-destructive text-sm">You do not have permission to view this CAPA.</p>;
  }

  if (isError) {
    return (
      <div className="p-6 space-y-4">
        <p className="text-destructive text-sm">{handleApiError(error)}</p>
        <Button variant="outline" onClick={() => router.push("/qms/capa" as Route)}>
          Back to CAPAs
        </Button>
      </div>
    );
  }

  if (isLoading || !capa) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading CAPA…
      </div>
    );
  }

  const onSaveRootCause = () => {
    if (!rootCause.trim()) {
      toast.error("Root cause is required.");
      return;
    }
    updateMut.mutate(
      { id, data: { root_cause: rootCause.trim(), root_cause_method: rootMethod.trim() || null } },
      {
        onSuccess: () => {
          toast.success("Root cause updated.");
          setRootCauseOpen(false);
          void refetch();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onAddAction = () => {
    if (!actionDesc.trim()) {
      toast.error("Description is required.");
      return;
    }
    addActionMut.mutate(
      { capaId: id, data: { action_type: actionType, description: actionDesc.trim() } },
      {
        onSuccess: () => {
          toast.success("Action added.");
          setActionOpen(false);
          setActionDesc("");
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onCompleteAction = () => {
    if (!completeActionId) return;
    completeActionMut.mutate(
      { capaId: id, actionId: completeActionId, data: { evidence: completeEvidence.trim() || null } },
      {
        onSuccess: () => {
          toast.success("Action marked complete.");
          setCompleteOpen(false);
          setCompleteActionId(null);
          setCompleteEvidence("");
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onVerify = () => {
    verifyMut.mutate(
      { id, data: { verified: verifyOk, notes: verifyNotes.trim() || null } },
      {
        onSuccess: () => {
          toast.success("Effectiveness recorded.");
          setVerifyOpen(false);
          void refetch();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onClose = () => {
    closeMut.mutate(id, {
      onSuccess: () => {
        toast.success("CAPA closed.");
        void refetch();
      },
      onError: (e) => toast.error(handleApiError(e)),
    });
  };

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm flex-wrap">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")} className="h-7 px-2">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/capa" as Route)} className="h-7 px-2">
          <Home className="h-4 w-4 mr-1" />
          CAPA
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="font-medium font-mono text-xs">{capa.capa_number}</span>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex flex-col gap-2">
          <div>
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <ClipboardList className="h-6 w-6 shrink-0" />
              <span className="break-words">{capa.title}</span>
            </h1>
            <p className="text-muted-foreground text-sm mt-1 font-mono">{capa.capa_number}</p>
          </div>
          {sourceQeHref && (
            <Button variant="outline" size="sm" className="w-fit min-h-11" asChild>
              <Link href={sourceQeHref}>Linked quality event</Link>
            </Button>
          )}
        </div>
        {canWrite && (
          <Button size="sm" variant="destructive" onClick={() => setDeleteOpen(true)} className="min-h-11 shrink-0">
            <Trash2 className="h-4 w-4 mr-1" />
            Delete
          </Button>
        )}
      </div>

      <Card>
        <CardHeader className="pb-2">
          <CardTitle className="text-base">Lifecycle (6 steps)</CardTitle>
          <p className="text-xs text-muted-foreground">
            Step highlights follow backend status values. Read-only while closed.
          </p>
        </CardHeader>
        <CardContent>
          <ol className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {LIFECYCLE_STEPS.map((step, idx) => {
              const done = closed || idx < currentStep;
              const active = !closed && idx === currentStep;
              return (
                <li
                  key={step.status}
                  className={`rounded-lg border px-2 py-3 text-center text-xs font-medium min-h-[72px] flex flex-col items-center justify-center gap-1 ${
                    active ? "border-primary bg-primary/5" : "border-border"
                  }`}
                >
                  {done ? (
                    <CheckCircle2 className="h-4 w-4 text-green-600 shrink-0" aria-hidden />
                  ) : (
                    <Circle className="h-4 w-4 text-muted-foreground shrink-0" aria-hidden />
                  )}
                  <span className="leading-tight">{step.label}</span>
                </li>
              );
            })}
          </ol>
          <p className="text-xs text-muted-foreground mt-3 capitalize">
            Current status: <span className="font-mono">{capa.status.replace(/_/g, " ")}</span>
          </p>
        </CardContent>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Overview</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2 text-muted-foreground">
            <p>
              <span className="font-medium text-foreground">Type:</span> {capa.capa_type}
            </p>
            <p>
              <span className="font-medium text-foreground">Severity:</span> {capa.severity}
            </p>
            <p>
              <span className="font-medium text-foreground">Owner:</span>{" "}
              <span className="font-mono text-xs">{capa.owner_id ?? "—"}</span>
            </p>
            <p>
              <span className="font-medium text-foreground">Due:</span>{" "}
              {capa.due_date ? new Date(capa.due_date).toLocaleDateString() : "—"}
            </p>
            {capa.description && (
              <p className="pt-2 whitespace-pre-wrap text-foreground/90">{capa.description}</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between gap-2">
            <CardTitle className="text-base">Effectiveness & close</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-2">
            {capa.effectiveness_verified !== undefined && capa.effectiveness_verified !== null && (
              <p className="text-sm text-muted-foreground">
                Verified:{" "}
                <span className="font-medium text-foreground">{String(capa.effectiveness_verified)}</span>
                {capa.effectiveness_check_date && (
                  <span className="block text-xs mt-1">
                    {new Date(capa.effectiveness_check_date).toLocaleString()}
                  </span>
                )}
              </p>
            )}
            <div className="flex flex-wrap gap-2 mt-2">
              {allowApprove && (
                <>
                  <Button size="sm" variant="outline" onClick={() => setVerifyOpen(true)} className="min-h-11">
                    Verify effectiveness
                  </Button>
                  <Button size="sm" onClick={onClose} disabled={closeMut.isPending} className="min-h-11">
                    {closeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Close CAPA"}
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between gap-2 flex-wrap">
          <CardTitle className="text-base">Actions</CardTitle>
          {allowWrite && (
            <div className="flex flex-wrap gap-2">
              <Button size="sm" variant="outline" onClick={() => setRootCauseOpen(true)} className="min-h-11">
                Edit root cause
              </Button>
              <Button size="sm" onClick={() => setActionOpen(true)} className="min-h-11">
                Add action
              </Button>
            </div>
          )}
        </CardHeader>
        <CardContent>
          {actionsLoading ? (
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" /> Loading actions…
            </p>
          ) : actions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No actions yet.</p>
          ) : (
            <ul className="space-y-3">
              {actions.map((a) => (
                <li key={a.id} className="rounded-md border border-border p-3 text-sm">
                  <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-2">
                    <div>
                      <p className="font-medium capitalize">{a.action_type}</p>
                      <p className="text-muted-foreground mt-1 whitespace-pre-wrap">{a.description}</p>
                      <p className="text-xs text-muted-foreground mt-2">
                        Status: {a.status}
                        {a.completed_at && ` · ${new Date(a.completed_at).toLocaleString()}`}
                      </p>
                    </div>
                    {allowWrite && a.status !== "completed" && (
                      <Button
                        size="sm"
                        variant="secondary"
                        className="min-h-11 shrink-0"
                        onClick={() => {
                          setCompleteActionId(a.id);
                          setCompleteOpen(true);
                        }}
                      >
                        Complete
                      </Button>
                    )}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Dialog open={rootCauseOpen} onOpenChange={setRootCauseOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Root cause</DialogTitle>
            <DialogDescription>Update investigation outcome (requires CAPA write).</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label htmlFor="rc">Root cause</Label>
              <Textarea id="rc" value={rootCause} onChange={(e) => setRootCause(e.target.value)} rows={4} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="rm">Method (optional)</Label>
              <Input id="rm" value={rootMethod} onChange={(e) => setRootMethod(e.target.value)} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRootCauseOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onSaveRootCause} disabled={updateMut.isPending}>
              {updateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={actionOpen} onOpenChange={setActionOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add CAPA action</DialogTitle>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label htmlFor="at">Action type</Label>
              <Input id="at" value={actionType} onChange={(e) => setActionType(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="ad">Description</Label>
              <Textarea id="ad" value={actionDesc} onChange={(e) => setActionDesc(e.target.value)} rows={3} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setActionOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onAddAction} disabled={addActionMut.isPending}>
              {addActionMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Add"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={verifyOpen} onOpenChange={setVerifyOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Verify effectiveness</DialogTitle>
            <DialogDescription>Requires CAPA approve permission.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={verifyOk} onChange={(e) => setVerifyOk(e.target.checked)} className="h-4 w-4" />
              Mark as effective
            </label>
            <div>
              <Label htmlFor="vn">Notes</Label>
              <Textarea id="vn" value={verifyNotes} onChange={(e) => setVerifyNotes(e.target.value)} rows={2} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setVerifyOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onVerify} disabled={verifyMut.isPending}>
              {verifyMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={completeOpen} onOpenChange={setCompleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Complete action</DialogTitle>
          </DialogHeader>
          <div className="py-2">
            <Label htmlFor="ev">Evidence (optional)</Label>
            <Textarea
              id="ev"
              value={completeEvidence}
              onChange={(e) => setCompleteEvidence(e.target.value)}
              rows={3}
              className="mt-1"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCompleteOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onCompleteAction} disabled={completeActionMut.isPending}>
              {completeActionMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Complete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete CAPA</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{capa.capa_number}</strong> — {capa.title}? This action cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMut.isPending}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={(e: React.MouseEvent) => {
                e.preventDefault();
                onDeleteConfirm();
              }}
              disabled={deleteMut.isPending}
            >
              {deleteMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Delete"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
