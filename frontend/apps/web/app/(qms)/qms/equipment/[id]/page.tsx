"use client";

import type { Route } from "next";
import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import {
  ArrowLeft, Loader2, Wrench, Plus, CheckCircle2, XCircle, Clock, Save, X, Trash2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent,
  AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle,
} from "@/components/ui/dialog";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FBSForm } from "@/components/qms-shared/FBSForm";
import { StatusBadge } from "@/components/qms-shared/StatusBadge";
import { ModuleHeader } from "@/components/qms-shared/ModuleHeader";
import {
  useCalibrateEquipment, useDecommissionEquipment, useDeleteEquipment,
  useEquipmentCalibrations, useEquipmentItem, useUpdateEquipment,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

function calStatusBadge(eq: { next_calibration_date?: string | null; next_calibration?: string | null; requires_calibration?: boolean }) {
  if (!eq.requires_calibration) return <Badge variant="secondary">Not Required</Badge>;
  const d = eq.next_calibration_date ?? eq.next_calibration;
  if (!d) return <Badge variant="outline">No date set</Badge>;
  const diff = (new Date(d).getTime() - Date.now()) / 86400000;
  if (diff < 0) return <Badge className="bg-red-100 text-red-700">Overdue</Badge>;
  if (diff < 14) return <Badge className="bg-amber-100 text-amber-700">Due Soon ({Math.round(diff)}d)</Badge>;
  return <Badge className="bg-emerald-100 text-emerald-700">In Date</Badge>;
}

export default function EquipmentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = String(params.id ?? "");
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("equipment:read");
  const canWrite = hasPermission("equipment:write");

  const { data: eq, isLoading, isError, error, refetch } = useEquipmentItem(id);
  const { data: calibrations = [] } = useEquipmentCalibrations(id);
  const calMut = useCalibrateEquipment();
  const decomMut = useDecommissionEquipment();
  const updateMut = useUpdateEquipment();
  const deleteMut = useDeleteEquipment();

  const [editField, setEditField] = useState<string | null>(null);
  const [fieldVal, setFieldVal] = useState("");

  const [calOpen, setCalOpen] = useState(false);
  const [calDate, setCalDate] = useState(new Date().toISOString().slice(0, 10));
  const [calPassed, setCalPassed] = useState(true);
  const [calNotes, setCalNotes] = useState("");

  const [decomOpen, setDecomOpen] = useState(false);
  const [decomReason, setDecomReason] = useState("");
  const [deleteOpen, setDeleteOpen] = useState(false);

  if (!id) return <p className="p-6 text-muted-foreground">Invalid equipment.</p>;
  if (permLoading || isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" /> Loading…
      </div>
    );
  }
  if (!canRead) return <p className="p-6 text-destructive text-sm">No permission.</p>;
  if (isError) return <p className="p-6 text-destructive text-sm">{handleApiError(error)}</p>;
  if (!eq) return null;

  const decommissioned = eq.status === "decommissioned";
  const allowWrite = canWrite && !decommissioned;

  const saveField = (field: string, value: unknown) => {
    updateMut.mutate({ id, data: { [field]: value } as Parameters<typeof updateMut.mutate>[0]["data"] }, {
      onSuccess: () => { toast.success("Saved."); setEditField(null); void refetch(); },
      onError: (e) => toast.error(handleApiError(e)),
    });
  };

  const InfoRow = ({ label, value, field, type = "text" }: {
    label: string; value: string | null | undefined; field?: string; type?: string;
  }) => (
    <div className="flex justify-between items-start py-2 border-b last:border-0">
      <span className="text-xs text-muted-foreground w-36 shrink-0">{label}</span>
      {field && allowWrite && editField === field ? (
        <div className="flex gap-2 flex-1">
          <Input
            type={type}
            value={fieldVal}
            onChange={(e) => setFieldVal(e.target.value)}
            className="h-7 text-xs"
            autoFocus
          />
          <Button size="sm" className="h-7 px-2" onClick={() => saveField(field, fieldVal)}>
            <Save className="h-3 w-3" />
          </Button>
          <Button size="sm" variant="ghost" className="h-7 px-2" onClick={() => setEditField(null)}>
            <X className="h-3 w-3" />
          </Button>
        </div>
      ) : (
        <span
          className={`text-xs text-right flex-1 ${field && allowWrite ? "cursor-pointer hover:text-primary" : ""}`}
          onClick={() => { if (field && allowWrite) { setEditField(field); setFieldVal(value ?? ""); } }}
        >
          {value || <span className="text-muted-foreground italic">{field && allowWrite ? "Click to set" : "—"}</span>}
        </span>
      )}
    </div>
  );

  const tabs = [
    {
      id: "info",
      label: "Information",
      icon: "📋",
      content: (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Left: grouped sections */}
          <div className="space-y-6">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Equipment Information</CardTitle></CardHeader>
              <CardContent className="text-sm">
                <InfoRow label="Asset Tag" value={eq.asset_tag} />
                <InfoRow label="Name" value={eq.name} field="name" />
                <InfoRow label="Type" value={eq.equipment_type} />
                <InfoRow label="Manufacturer" value={eq.manufacturer} field="manufacturer" />
                <InfoRow label="Model" value={eq.model} field="model" />
                <InfoRow label="Serial Number" value={eq.serial_number} field="serial_number" />
                <InfoRow label="Status" value={undefined} />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Location & Assignment</CardTitle></CardHeader>
              <CardContent className="text-sm">
                <InfoRow label="Location" value={eq.location} field="location" />
                <InfoRow label="Department" value={eq.department} field="department" />
                <InfoRow label="Assigned To" value={eq.assigned_to} field="assigned_to" />
              </CardContent>
            </Card>
          </div>

          <div className="space-y-6">
            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Calibration Schedule</CardTitle></CardHeader>
              <CardContent className="text-sm space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-muted-foreground">Requires Calibration</span>
                  <span className={`text-xs font-medium ${eq.requires_calibration ? "text-emerald-600" : "text-muted-foreground"}`}>
                    {eq.requires_calibration ? "Yes" : "No"}
                  </span>
                </div>
                <InfoRow label="Frequency (days)" value={eq.calibration_frequency_days?.toString()} />
                <InfoRow label="Last Calibration" value={eq.last_calibration_date ? new Date(eq.last_calibration_date).toLocaleDateString() : null} />
                <InfoRow label="Next Calibration" value={eq.next_calibration_date ? new Date(eq.next_calibration_date).toLocaleDateString() : null} />
                <div className="flex justify-between items-center pt-1">
                  <span className="text-xs text-muted-foreground">Cal Status</span>
                  {calStatusBadge(eq)}
                </div>
                {allowWrite && eq.requires_calibration && (
                  <Button size="sm" className="w-full mt-2" onClick={() => setCalOpen(true)}>
                    <Plus className="h-4 w-4 mr-1" /> Record Calibration
                  </Button>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2"><CardTitle className="text-sm">Preventive Maintenance</CardTitle></CardHeader>
              <CardContent className="text-sm">
                <div className="flex justify-between">
                  <span className="text-xs text-muted-foreground">Requires PM</span>
                  <span className={`text-xs font-medium ${eq.requires_pm ? "text-emerald-600" : "text-muted-foreground"}`}>
                    {eq.requires_pm ? "Yes" : "No"}
                  </span>
                </div>
                <InfoRow label="PM Frequency (days)" value={eq.pm_frequency_days?.toString()} />
                <InfoRow label="Last PM Date" value={eq.last_pm_date ? new Date(eq.last_pm_date).toLocaleDateString() : null} />
                <InfoRow label="Next PM Date" value={eq.next_pm_date ? new Date(eq.next_pm_date).toLocaleDateString() : null} />
              </CardContent>
            </Card>

            {eq.notes && (
              <Card>
                <CardHeader className="pb-2"><CardTitle className="text-sm">Notes</CardTitle></CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground whitespace-pre-wrap">{eq.notes}</p>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      ),
    },
    {
      id: "calibration-history",
      label: "Calibration History",
      icon: "📅",
      content: (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Calibration Records ({calibrations.length})</h3>
            {allowWrite && eq.requires_calibration && (
              <Button size="sm" onClick={() => setCalOpen(true)}>
                <Plus className="h-4 w-4 mr-1" /> Record Calibration
              </Button>
            )}
          </div>
          {calibrations.length === 0 ? (
            <p className="text-sm text-muted-foreground italic">No calibration records yet.</p>
          ) : (
            <div className="space-y-3">
              {calibrations.map((c) => (
                <Card key={c.id}>
                  <CardContent className="pt-4">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        {c.passed ? (
                          <CheckCircle2 className="h-5 w-5 text-emerald-600 shrink-0" />
                        ) : (
                          <XCircle className="h-5 w-5 text-red-600 shrink-0" />
                        )}
                        <div>
                          <p className="text-sm font-medium">
                            {new Date(c.calibration_date).toLocaleDateString()}
                            <Badge className={`ml-2 text-xs ${c.passed ? "bg-emerald-100 text-emerald-700" : "bg-red-100 text-red-700"}`}>
                              {c.passed ? "PASS" : "FAIL"}
                            </Badge>
                          </p>
                          {c.calibrated_by && <p className="text-xs text-muted-foreground">By: {c.calibrated_by}</p>}
                          {c.notes && <p className="text-xs text-muted-foreground mt-1">{c.notes}</p>}
                          {c.as_found_reading && <p className="text-xs text-muted-foreground">As-found: {c.as_found_reading}</p>}
                          {c.as_left_reading && <p className="text-xs text-muted-foreground">As-left: {c.as_left_reading}</p>}
                          {c.measurement_uncertainty != null && (
                            <p className="text-xs text-muted-foreground">Uncertainty: ±{c.measurement_uncertainty}</p>
                          )}
                        </div>
                      </div>
                      <p className="text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(c.created_at).toLocaleDateString()}
                      </p>
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
      id: "usage-log",
      label: "Usage Logbook",
      icon: "📝",
      content: (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Track equipment usage, idle time, and maintenance windows.
          </p>
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground italic">No usage entries logged yet.</p>
            </CardContent>
          </Card>
        </div>
      ),
    },
    {
      id: "attachments",
      label: "Attachments",
      icon: "📎",
      content: (
        <div className="space-y-3">
          <p className="text-sm text-muted-foreground">
            Manuals, certificates, and other documents.
          </p>
          <Card>
            <CardContent className="pt-4">
              <p className="text-sm text-muted-foreground italic">No attachments yet.</p>
            </CardContent>
          </Card>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6 p-6 max-w-6xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <Button variant="ghost" size="sm" className="h-7 px-2" onClick={() => router.push("/qms/equipment" as Route)}>
          <ArrowLeft className="h-3 w-3 mr-1" />Equipment
        </Button>
        <span>/</span>
        <span className="font-mono text-xs text-foreground">{eq.asset_tag}</span>
      </div>

      {/* Header */}
      <ModuleHeader
        icon={<Wrench className="h-6 w-6" />}
        title={eq.name}
        description={`${eq.asset_tag} · ${eq.equipment_type}`}
        actions={
          <div className="flex flex-wrap gap-2">
            <StatusBadge status={eq.status} />
            {calStatusBadge(eq)}
            {allowWrite && !decommissioned && (
              <Button size="sm" variant="outline" onClick={() => setDecomOpen(true)}>Decommission</Button>
            )}
            {canWrite && (
              <Button size="sm" variant="destructive" onClick={() => setDeleteOpen(true)}>
                <Trash2 className="h-4 w-4" />
              </Button>
            )}
          </div>
        }
      />

      {/* FBS-style tabs */}
      <FBSForm tabs={tabs} defaultTab="info" />

      {/* Record Calibration dialog */}
      <Dialog open={calOpen} onOpenChange={setCalOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Record Calibration</DialogTitle>
            <DialogDescription>Record the result of a calibration event for {eq.name}.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div>
              <Label>Calibration Date *</Label>
              <Input type="date" value={calDate} onChange={(e) => setCalDate(e.target.value)} className="mt-1" />
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="passed"
                checked={calPassed}
                onCheckedChange={(v) => setCalPassed(!!v)}
              />
              <Label htmlFor="passed">Calibration Passed</Label>
            </div>
            <div>
              <Label>Notes / Observations</Label>
              <Textarea value={calNotes} onChange={(e) => setCalNotes(e.target.value)} rows={3} className="mt-1" />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setCalOpen(false)}>Cancel</Button>
            <Button
              onClick={() => {
                if (!calDate) return toast.error("Date required.");
                calMut.mutate(
                  { id, data: { calibration_date: calDate, passed: calPassed, notes: calNotes || null } },
                  {
                    onSuccess: () => {
                      toast.success(calPassed ? "Calibration recorded — PASS" : "Calibration recorded — FAIL. Auto-QE may be created.");
                      setCalOpen(false);
                      setCalNotes("");
                      setCalPassed(true);
                      void refetch();
                    },
                    onError: (e) => toast.error(handleApiError(e)),
                  },
                );
              }}
              disabled={calMut.isPending}
            >
              {calMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              {calPassed ? "Record Pass" : "Record Fail (OOT)"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Decommission dialog */}
      <Dialog open={decomOpen} onOpenChange={setDecomOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Decommission Equipment</DialogTitle>
            <DialogDescription>This equipment will be marked as decommissioned and no further calibrations can be recorded.</DialogDescription>
          </DialogHeader>
          <div className="py-2">
            <Label>Reason *</Label>
            <Textarea value={decomReason} onChange={(e) => setDecomReason(e.target.value)} rows={3} className="mt-1" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDecomOpen(false)}>Cancel</Button>
            <Button
              variant="destructive"
              onClick={() => {
                if (!decomReason.trim()) return toast.error("Reason required.");
                decomMut.mutate({ id, reason: decomReason }, {
                  onSuccess: () => { toast.success("Equipment decommissioned."); setDecomOpen(false); void refetch(); },
                  onError: (e) => toast.error(handleApiError(e)),
                });
              }}
              disabled={decomMut.isPending}
            >
              {decomMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              Decommission
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete dialog */}
      <AlertDialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Equipment</AlertDialogTitle>
            <AlertDialogDescription>Delete {eq.name} ({eq.asset_tag})? This cannot be undone.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={deleteMut.isPending}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              onClick={(e: React.MouseEvent) => {
                e.preventDefault();
                deleteMut.mutate(id, {
                  onSuccess: () => { toast.success("Deleted."); router.push("/qms/equipment" as Route); },
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
