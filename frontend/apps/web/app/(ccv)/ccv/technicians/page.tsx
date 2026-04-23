"use client";

import { useState } from "react";
import { HardHat, Plus, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useTechnicians } from "@/lib/hooks/queries/ccv";
import type { Technician } from "@/lib/api/services/ccv";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-green-100 text-green-700" },
  on_leave: { label: "On Leave", color: "bg-amber-100 text-amber-700" },
  suspended: { label: "Suspended", color: "bg-red-100 text-red-600" },
  terminated: { label: "Terminated", color: "bg-slate-100 text-slate-500" },
};

const PAGE_SIZE = 10;

export default function TechniciansPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useTechnicians({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const technicians: Technician[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = technicians;

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <HardHat className="h-6 w-6" />
            Technicians
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Field technician profiles, certifications, and availability</p>
        </div>
        <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Register Technician</Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by name or email..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading…" : `${totalItems} technicians`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Name</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Specializations</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Service Area</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Certs</th>
                  <th className="pb-2 pr-4 font-medium">Available</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">{Array.from({ length: 6 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-24" /></td>))}</tr>
                )) : paginated.map((t) => {
                  const cfg = STATUS_CONFIG[t.status] ?? { label: t.status, color: "" };
                  return (
                    <tr key={t.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer">
                      <td className="py-3 pr-4">
                        <div>
                          <p className="font-medium">{t.first_name} {t.last_name}</p>
                          <p className="text-xs text-muted-foreground">{t.email}</p>
                        </div>
                      </td>
                      <td className="py-3 pr-4 hidden sm:table-cell">
                        <div className="flex flex-wrap gap-1">
                          {t.specializations.map((s) => (
                            <span key={s} className="inline-flex items-center rounded px-1.5 py-0.5 text-xs bg-slate-100 text-slate-600 capitalize">{s}</span>
                          ))}
                        </div>
                      </td>
                      <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">{t.service_area ?? "—"}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden lg:table-cell">{t.certifications_count}</td>
                      <td className="py-3 pr-4">
                        <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${t.is_available ? "bg-green-100 text-green-700" : "bg-red-100 text-red-600"}`}>
                          {t.is_available ? "Yes" : "No"}
                        </span>
                      </td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{cfg.label}</span></td>
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
