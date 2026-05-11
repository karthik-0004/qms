"use client";

import { useState, lazy, Suspense } from "react";
import { useRouter } from "next/navigation";
import { AlertTriangle, Plus, Search, ChevronLeft, ChevronRight, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useQualityEvents, useCreateQualityEvent } from "@/lib/hooks/queries/qms";
import type { QualityEvent } from "@/lib/api/services/qms";
import { toast } from "sonner";

const Dialog = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.Dialog })));
const DialogContent = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogContent })));
const DialogDescription = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogDescription })));
const DialogFooter = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogFooter })));
const DialogHeader = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogHeader })));
const DialogTitle = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogTitle })));
const DialogTrigger = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogTrigger })));

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  open: { label: "Open", color: "bg-blue-100 text-blue-700" },
  under_investigation: { label: "Investigating", color: "bg-amber-100 text-amber-700" },
  pending_capa: { label: "Pending CAPA", color: "bg-purple-100 text-purple-700" },
  closed: { label: "Closed", color: "bg-green-100 text-green-700" },
  cancelled: { label: "Cancelled", color: "bg-slate-100 text-slate-500" },
};

const SEVERITY_CONFIG: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  major: "bg-orange-100 text-orange-700",
  minor: "bg-yellow-100 text-yellow-700",
  observation: "bg-slate-100 text-slate-600",
};

const PAGE_SIZE = 10;

export default function QualityEventsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    description: "",
    severity: "minor",
    event_type: "deviation",
  });

  const { data, isLoading: loading } = useQualityEvents({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const createEvent = useCreateQualityEvent();

  const events: QualityEvent[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;

  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = events;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    createEvent.mutate(
      {
        event_number: `QE-${Date.now()}`,
        title: formData.title,
        event_type: formData.event_type,
        severity: formData.severity,
        description: formData.description,
        detected_at: new Date().toISOString(),
      },
      {
        onSuccess: () => {
          toast.success("Quality event created successfully");
          setDialogOpen(false);
          setFormData({ title: "", description: "", severity: "minor", event_type: "deviation" });
        },
        onError: (error: unknown) => {
          const err = error as { response?: { data?: { detail?: string } }; message?: string };
          const errorMessage =
            err?.response?.data?.detail || err?.message || "Failed to create quality event";
          toast.error(String(errorMessage));
        },
      }
    );
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-sm">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <Home className="h-4 w-4 mr-1" />
          Home
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">Quality Events</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <AlertTriangle className="h-6 w-6" />
            Quality Events
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Track deviations, OOS results, and quality incidents</p>
        </div>
        <Suspense fallback={<Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Report Event</Button>}>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Report Event</Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Report Quality Event</DialogTitle>
                <DialogDescription>
                  Create a new quality event to track deviations, OOS results, or quality incidents.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Event title"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="description">Description</Label>
                    <Input
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Detailed description of the event"
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="event_type">Event Type</Label>
                      <select
                        id="event_type"
                        value={formData.event_type}
                        onChange={(e) => setFormData({ ...formData, event_type: e.target.value })}
                        className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                      >
                        <option value="deviation">Deviation</option>
                        <option value="oos">OOS Result</option>
                        <option value="complaint">Complaint</option>
                        <option value="incident">Incident</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="severity">Severity</Label>
                      <select
                        id="severity"
                        value={formData.severity}
                        onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                        className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                      >
                        <option value="critical">Critical</option>
                        <option value="major">Major</option>
                        <option value="minor">Minor</option>
                        <option value="observation">Observation</option>
                      </select>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={createEvent.isPending}>
                    {createEvent.isPending ? "Submitting..." : "Submit Event"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </Suspense>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search events..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading…" : `${totalItems} events`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Event #</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Severity</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Department</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden md:table-cell">Reported</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">
                    {Array.from({ length: 6 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-24" /></td>))}
                  </tr>
                )) : paginated.map((ev) => {
                  const cfg = STATUS_CONFIG[ev.status] ?? { label: ev.status, color: "" };
                  const sevColor = SEVERITY_CONFIG[ev.severity] ?? "";
                  return (
                    <tr key={ev.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer">
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{ev.event_number}</td>
                      <td className="py-3 pr-4 font-medium max-w-[200px] truncate">{ev.title}</td>
                      <td className="py-3 pr-4 hidden sm:table-cell"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${sevColor}`}>{ev.severity}</span></td>
                      <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">{ev.department ?? "—"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{cfg.label}</span></td>
                      <td className="py-3 text-muted-foreground text-xs hidden md:table-cell">{new Date(ev.reported_at).toLocaleDateString()}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {!loading && totalItems > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}><ChevronLeft className="h-4 w-4" /></Button>
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}><ChevronRight className="h-4 w-4" /></Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
