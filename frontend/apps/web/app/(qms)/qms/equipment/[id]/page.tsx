"use client";

import type { Route } from "next";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Home, Loader2, Pencil, Trash2, Wrench } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
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
  useCalibrateEquipment,
  useCreateQualityEvent,
  useDecommissionEquipment,
  useDeleteEquipment,
  useEquipmentItem,
  useUpdateEquipment,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

function nextCalLabel(eq: { next_calibration_date?: string | null; next_calibration?: string | null }) {
  const d = eq.next_calibration_date ?? eq.next_calibration;
  return d ? new Date(String(d)).toLocaleDateString() : "—";
}

export default function EquipmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = String(params.id ?? "");
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("equipment:read");
  const canWrite = hasPermission("equipment:write");
  const canWriteQe = hasPermission("quality_event:write");

  const { data: eq, isLoading, isError, error, refetch } = useEquipmentItem(id);
  const calMut = useCalibrateEquipment();
  const decomMut = useDecommissionEquipment();
  const createQeMut = useCreateQualityEvent();
  const updateMut = useUpdateEquipment();
  const deleteMut = useDeleteEquipment();

  const [calOpen, setCalOpen] = useState(false);
  const [calDate, setCalDate] = useState("");
  const [calPassed, setCalPassed] = useState(true);
  const [calNotes, setCalNotes] = useState("");
  const [decomOpen, setDecomOpen] = useState(false);
  const [decomReason, setDecomReason] = useState("");

  const [editOpen, setEditOpen] = useState(false);
  const [editName, setEditName] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editLocation, setEditLocation] = useState("");
  const [editDepartment, setEditDepartment] = useState("");
  const [editAssignedTo, setEditAssignedTo] = useState("");
  const [editNotes, setEditNotes] = useState("");
  const [editRequiresCalibration, setEditRequiresCalibration] = useState(false);
  const [editCalFreqDays, setEditCalFreqDays] = useState<string>("");

  const [deleteOpen, setDeleteOpen] = useState(false);

  const openEdit = () => {
    if (!eq) return;
    setEditName(eq.name ?? "");
    setEditDescription(eq.description ?? "");
    setEditLocation(eq.location ?? "");
    setEditDepartment(eq.department ?? "");
    setEditAssignedTo(eq.assigned_to ?? "");
    setEditNotes(eq.notes ?? "");
    setEditRequiresCalibration(eq.requires_calibration ?? false);
    setEditCalFreqDays(eq.calibration_frequency_days != null ? String(eq.calibration_frequency_days) : "");
    setEditOpen(true);
  };

  const onEditSubmit = () => {
    if (!editName.trim()) {
      toast.error("Name is required.");
      return;
    }
    updateMut.mutate(
      {
        id,
        data: {
          name: editName.trim(),
          description: editDescription.trim() || null,
          location: editLocation.trim() || null,
          department: editDepartment.trim() || null,
          assigned_to: editAssignedTo.trim() || null,
          notes: editNotes.trim() || null,
          requires_calibration: editRequiresCalibration,
          calibration_frequency_days: editCalFreqDays ? Number(editCalFreqDays) : null,
        },
      },
      {
        onSuccess: () => {
          toast.success("Equipment updated");
          setEditOpen(false);
          void refetch();
        },
        onError: (e) => toast.error(`Failed to update equipment: ${handleApiError(e)}`),
      },
    );
  };

  const onDeleteConfirm = () => {
    deleteMut.mutate(id, {
      onSuccess: () => {
        toast.success("Equipment deleted");
        router.push("/qms/equipment" as Route);
      },
      onError: (e) => toast.error(`Failed to delete equipment: ${handleApiError(e)}`),
    });
  };

  if (!id) {
    return <p className="p-6 text-muted-foreground">Invalid equipment.</p>;
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
    return <p className="p-6 text-destructive text-sm">You do not have permission to view this asset.</p>;
  }

  if (isError) {
    return (
      <div className="p-6 space-y-4">
        <p className="text-destructive text-sm">{handleApiError(error)}</p>
        <Button variant="outline" onClick={() => router.push("/qms/equipment" as Route)}>
          Back to equipment
        </Button>
      </div>
    );
  }

  if (isLoading || !eq) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading equipment…
      </div>
    );
  }

  const decommissioned = eq.status === "decommissioned";

  const onCalibrate = () => {
    if (!calDate) {
      toast.error("Calibration date is required.");
      return;
    }
    const iso = new Date(calDate).toISOString();
    calMut.mutate(
      { id, data: { calibration_date: iso, passed: calPassed, notes: calNotes.trim() || null } },
      {
        onSuccess: async () => {
          toast.success("Calibration recorded.");
          setCalOpen(false);
          setCalNotes("");
          void refetch();
          if (!calPassed && canWriteQe) {
            const eventNumber = `QE-CAL-${Date.now()}`;
            createQeMut.mutate(
              {
                event_number: eventNumber,
                title: `Calibration failure: ${eq.name}`,
                event_type: "calibration_failure",
                description: `Equipment ${eq.asset_tag} (${eq.name}) failed calibration on ${iso}. Notes: ${calNotes || "—"}`,
                detected_at: iso,
                severity: "major",
                department: eq.department ?? undefined,
              },
              {
                onSuccess: () => toast.success("Quality event opened for failed calibration."),
                onError: (e) => toast.error(handleApiError(e)),
              },
            );
          } else if (!calPassed && !canWriteQe) {
            toast.error("Calibration failed — you lack permission to create a quality event.");
          }
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onDecommission = () => {
    if (!decomReason.trim()) {
      toast.error("Reason is required.");
      return;
    }
    decomMut.mutate(
      { id, reason: decomReason.trim() },
      {
        onSuccess: () => {
          toast.success("Equipment decommissioned.");
          setDecomOpen(false);
          setDecomReason("");
          void refetch();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm flex-wrap">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")} className="h-7 px-2">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/equipment" as Route)} className="h-7 px-2">
          <Home className="h-4 w-4 mr-1" />
          Equipment
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="font-medium font-mono text-xs">{eq.asset_tag}</span>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Wrench className="h-6 w-6 shrink-0" />
            <span className="break-words">{eq.name}</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1 font-mono">{eq.asset_tag}</p>
        </div>
        {canWrite && (
          <div className="flex flex-wrap gap-2">
            {!decommissioned && (
              <>
                <Button size="sm" variant="outline" onClick={() => setCalOpen(true)} className="min-h-11">
                  Record calibration
                </Button>
                <Button size="sm" variant="outline" onClick={openEdit} className="min-h-11">
                  <Pencil className="h-4 w-4 mr-1" />
                  Edit
                </Button>
                <Button size="sm" variant="destructive" onClick={() => setDecomOpen(true)} className="min-h-11">
                  Decommission
                </Button>
              </>
            )}
            <Button size="sm" variant="destructive" onClick={() => setDeleteOpen(true)} className="min-h-11">
              <Trash2 className="h-4 w-4 mr-1" />
              Delete
            </Button>
          </div>
        )}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Asset details</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2 text-muted-foreground">
          <p>
            <span className="font-medium text-foreground">Status:</span> {eq.status}
          </p>
          <p>
            <span className="font-medium text-foreground">Type:</span> {eq.equipment_type}
          </p>
          <p>
            <span className="font-medium text-foreground">Next calibration:</span> {nextCalLabel(eq)}
          </p>
          <p>
            <span className="font-medium text-foreground">Location:</span> {eq.location ?? "—"}
          </p>
          {eq.notes && <p className="pt-2 whitespace-pre-wrap text-foreground/90">{eq.notes}</p>}
        </CardContent>
      </Card>

      <Dialog open={calOpen} onOpenChange={setCalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Record calibration</DialogTitle>
            <DialogDescription>If calibration fails, a quality event is created when you have quality_event:write.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label htmlFor="cd">Calibration date / time</Label>
              <Input
                id="cd"
                type="datetime-local"
                value={calDate}
                onChange={(e) => setCalDate(e.target.value)}
                className="mt-1"
              />
            </div>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={calPassed} onChange={(e) => setCalPassed(e.target.checked)} className="h-4 w-4" />
              Passed
            </label>
            <div>
              <Label htmlFor="cn">Notes</Label>
              <Textarea id="cn" value={calNotes} onChange={(e) => setCalNotes(e.target.value)} rows={2} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onCalibrate} disabled={calMut.isPending}>
              {calMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={decomOpen} onOpenChange={setDecomOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Decommission equipment</DialogTitle>
          </DialogHeader>
          <div className="py-2">
            <Label htmlFor="dr">Reason</Label>
            <Textarea id="dr" value={decomReason} onChange={(e) => setDecomReason(e.target.value)} rows={3} className="mt-1" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDecomOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={onDecommission} disabled={decomMut.isPending}>
              {decomMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Decommission"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={editOpen} onOpenChange={setEditOpen}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Equipment</DialogTitle>
            <DialogDescription>Update the details for this asset.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label htmlFor="edit-name">Name *</Label>
              <Input id="edit-name" value={editName} onChange={(e) => setEditName(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="edit-description">Description</Label>
              <Textarea id="edit-description" value={editDescription} onChange={(e) => setEditDescription(e.target.value)} rows={2} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="edit-location">Location</Label>
              <Input id="edit-location" value={editLocation} onChange={(e) => setEditLocation(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="edit-department">Department</Label>
              <Input id="edit-department" value={editDepartment} onChange={(e) => setEditDepartment(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="edit-assigned">Assigned To</Label>
              <Input id="edit-assigned" value={editAssignedTo} onChange={(e) => setEditAssignedTo(e.target.value)} className="mt-1" />
            </div>
            <div>
              <Label htmlFor="edit-notes">Notes</Label>
              <Textarea id="edit-notes" value={editNotes} onChange={(e) => setEditNotes(e.target.value)} rows={2} className="mt-1" />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="edit-requires-cal"
                checked={editRequiresCalibration}
                onCheckedChange={(v) => setEditRequiresCalibration(Boolean(v))}
              />
              <Label htmlFor="edit-requires-cal">Requires Calibration</Label>
            </div>
            {editRequiresCalibration && (
              <div>
                <Label htmlFor="edit-cal-freq">Calibration Frequency (days)</Label>
                <Input
                  id="edit-cal-freq"
                  type="number"
                  min={1}
                  value={editCalFreqDays}
                  onChange={(e) => setEditCalFreqDays(e.target.value)}
                  className="mt-1"
                />
              </div>
            )}
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setEditOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onEditSubmit} disabled={updateMut.isPending}>
              {updateMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Save"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Equipment</AlertDialogTitle>
            <AlertDialogDescription>
              Are you sure you want to delete <strong>{eq.name}</strong>? This action cannot be undone.
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
