"use client";

import { useState } from "react";
import { AlertTriangle, Plus, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useQualityEvents } from "@/lib/hooks/queries/qms";
import type { QualityEvent } from "@/lib/api/services/qms";

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
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useQualityEvents({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const events: QualityEvent[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;

  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = events;

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <AlertTriangle className="h-6 w-6" />
            Quality Events
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Track deviations, OOS results, and quality incidents</p>
        </div>
        <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Report Event</Button>
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
