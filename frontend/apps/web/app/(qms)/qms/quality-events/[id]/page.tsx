"use client";

import Link from "next/link";
import type { Route } from "next";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { AlertTriangle, ArrowLeft, Home, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  useCloseQualityEvent,
  useCreateCAPA,
  useDeleteQualityEvent,
  useQualityEvent,
  useUpdateQualityEvent,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

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

  const [closeOpen, setCloseOpen] = useState(false);
  const [resolution, setResolution] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [escalateOpen, setEscalateOpen] = useState(false);
  const [capaTitle, setCapaTitle] = useState("");
  const [capaDesc, setCapaDesc] = useState("");

  if (!id) {
    return <p className="p-6 text-muted-foreground">Invalid quality event.</p>;
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
    return <p className="p-6 text-destructive text-sm">You do not have permission to view this event.</p>;
  }

  if (isError) {
    return (
      <div className="p-6 space-y-4">
        <p className="text-destructive text-sm">{handleApiError(error)}</p>
        <Button variant="outline" onClick={() => router.push("/qms/quality-events" as Route)}>
          Back to list
        </Button>
      </div>
    );
  }

  if (isLoading || !ev) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading event…
      </div>
    );
  }

  const closed = ev.status === "closed";
  const allowWrite = canWrite && !closed;

  const openEscalate = () => {
    setCapaTitle(`CAPA: ${ev.title}`);
    setCapaDesc(ev.description ?? "");
    setEscalateOpen(true);
  };

  const onEscalate = () => {
    if (!capaTitle.trim() || !capaDesc.trim()) {
      toast.error("Title and description are required.");
      return;
    }
    const capaNumber = `CAPA-${Date.now()}`;
    createCapaMut.mutate(
      {
        capa_number: capaNumber,
        title: capaTitle.trim(),
        description: capaDesc.trim(),
        source_type: "quality_event",
        source_id: ev.id,
        severity: ev.severity,
      },
      {
        onSuccess: async (capa) => {
          try {
            await updateMut.mutateAsync({ id: ev.id, data: { capa_id: capa.id } });
            toast.success("CAPA created and linked to this event.");
            setEscalateOpen(false);
            void refetch();
          } catch (e) {
            toast.error(handleApiError(e));
          }
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onClose = () => {
    closeMut.mutate(
      { id: ev.id, resolution: resolution.trim() || null },
      {
        onSuccess: () => {
          toast.success("Event closed.");
          setCloseOpen(false);
          setResolution("");
          void refetch();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onDelete = () => {
    deleteMut.mutate(ev.id, {
      onSuccess: () => {
        toast.success("Event deleted.");
        router.push("/qms/quality-events" as Route);
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
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/quality-events" as Route)} className="h-7 px-2">
          <Home className="h-4 w-4 mr-1" />
          Quality events
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="font-medium font-mono text-xs">{ev.event_number}</span>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <AlertTriangle className="h-6 w-6 shrink-0" />
            <span className="break-words">{ev.title}</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1 font-mono">{ev.event_number}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {allowWrite && (
            <>
              <Button size="sm" variant="outline" onClick={openEscalate} className="min-h-11">
                Escalate to CAPA
              </Button>
              <Button size="sm" variant="outline" onClick={() => setCloseOpen(true)} className="min-h-11">
                Close
              </Button>
              <Button size="sm" variant="destructive" onClick={() => setDeleteOpen(true)} className="min-h-11">
                Delete
              </Button>
            </>
          )}
        </div>
      </div>

      {ev.capa_id && (
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-base">Linked CAPA</CardTitle>
          </CardHeader>
          <CardContent>
            <Button variant="outline" className="min-h-11" asChild>
              <Link href={`/qms/capa/${ev.capa_id}` as Route}>Open CAPA {ev.capa_id.slice(0, 8)}…</Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Details</CardTitle>
          </CardHeader>
          <CardContent className="text-sm space-y-2 text-muted-foreground">
            <p>
              <span className="font-medium text-foreground">Status:</span> {ev.status}
            </p>
            <p>
              <span className="font-medium text-foreground">Severity:</span> {ev.severity}
            </p>
            <p>
              <span className="font-medium text-foreground">Type:</span> {ev.event_type}
            </p>
            <p>
              <span className="font-medium text-foreground">Detected:</span>{" "}
              {new Date(ev.detected_at).toLocaleString()}
            </p>
            {ev.description && <p className="pt-2 whitespace-pre-wrap text-foreground/90">{ev.description}</p>}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Assignment</CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-muted-foreground space-y-2">
            <p>
              <span className="font-medium text-foreground">Assigned to:</span>{" "}
              <span className="font-mono text-xs">{ev.assigned_to ?? "—"}</span>
            </p>
            <p>
              <span className="font-medium text-foreground">Department:</span> {ev.department ?? "—"}
            </p>
          </CardContent>
        </Card>
      </div>

      <Dialog open={escalateOpen} onOpenChange={setEscalateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Escalate to CAPA</DialogTitle>
            <DialogDescription>Creates a CAPA linked to this quality event and stores the CAPA id on the event.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label htmlFor="ct">CAPA title</Label>
              <Input id="ct" value={capaTitle} onChange={(e) => setCapaTitle(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="cd">CAPA description</Label>
              <Textarea id="cd" value={capaDesc} onChange={(e) => setCapaDesc(e.target.value)} rows={4} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEscalateOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onEscalate} disabled={createCapaMut.isPending || updateMut.isPending}>
              {createCapaMut.isPending || updateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Create CAPA"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={closeOpen} onOpenChange={setCloseOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Close quality event</DialogTitle>
          </DialogHeader>
          <div className="py-2">
            <Label htmlFor="res">Resolution (optional)</Label>
            <Textarea id="res" value={resolution} onChange={(e) => setResolution(e.target.value)} rows={3} className="mt-1" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCloseOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onClose} disabled={closeMut.isPending}>
              {closeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Close event"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete quality event</DialogTitle>
            <DialogDescription>Closed events cannot be deleted. This action cannot be undone.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={onDelete} disabled={deleteMut.isPending}>
              {deleteMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Delete"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
