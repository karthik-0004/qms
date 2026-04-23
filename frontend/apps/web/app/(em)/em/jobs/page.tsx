"use client";

import { useState } from "react";
import { ClipboardList, Plus, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useJobs } from "@/lib/hooks/queries/em";
import type { Job } from "@/lib/api/services/em";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  pending: { label: "Pending", color: "bg-slate-100 text-slate-700" },
  claimed: { label: "Claimed", color: "bg-blue-100 text-blue-700" },
  running: { label: "Running", color: "bg-cyan-100 text-cyan-700" },
  completed: { label: "Completed", color: "bg-green-100 text-green-700" },
  failed: { label: "Failed", color: "bg-red-100 text-red-700" },
  cancelled: { label: "Cancelled", color: "bg-slate-100 text-slate-500" },
  retrying: { label: "Retrying", color: "bg-amber-100 text-amber-700" },
};

const PAGE_SIZE = 10;

export default function JobsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useJobs({
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const jobs: Job[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = jobs;

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <ClipboardList className="h-6 w-6" />
            Job Queue
          </h1>
          <p className="text-muted-foreground text-sm mt-1">AI analysis job queue and worker status</p>
        </div>
        <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Enqueue Job</Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by plate barcode or job type..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading…" : `${totalItems} jobs`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Plate</th>
                  <th className="pb-2 pr-4 font-medium">Job Type</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Priority</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Attempts</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Worker</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden lg:table-cell">Created</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">{Array.from({ length: 7 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-20" /></td>))}</tr>
                )) : paginated.map((j) => {
                  const cfg = STATUS_CONFIG[j.status] ?? { label: j.status, color: "" };
                  return (
                    <tr key={j.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer">
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{j.plate_barcode}</td>
                      <td className="py-3 pr-4 capitalize text-muted-foreground">{j.job_type.replace(/_/g, " ")}</td>
                      <td className="py-3 pr-4 hidden sm:table-cell">{j.priority}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">{j.attempts}/{j.max_attempts}</td>
                      <td className="py-3 pr-4 text-muted-foreground text-xs hidden md:table-cell">{j.worker_id ?? "—"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{cfg.label}</span></td>
                      <td className="py-3 text-muted-foreground text-xs hidden lg:table-cell">{new Date(j.created_at).toLocaleString()}</td>
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
