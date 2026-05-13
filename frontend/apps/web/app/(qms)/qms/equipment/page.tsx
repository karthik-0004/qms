"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { Route } from "next";
import { Wrench, Plus, Search, ChevronLeft, ChevronRight, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useEquipment } from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import type { Equipment } from "@/lib/api/services/qms";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-green-100 text-green-700" },
  calibration_due: { label: "Cal Due", color: "bg-amber-100 text-amber-700" },
  calibration_overdue: { label: "Cal Overdue", color: "bg-red-100 text-red-700" },
  under_maintenance: { label: "Maintenance", color: "bg-blue-100 text-blue-700" },
  out_of_service: { label: "Out of Service", color: "bg-slate-100 text-slate-500" },
  decommissioned: { label: "Decommissioned", color: "bg-slate-100 text-slate-400" },
};

const PAGE_SIZE = 10;

export default function EquipmentPage() {
  const router = useRouter();
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canWriteEq = hasPermission("equipment:write");
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useEquipment({
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const equipment: Equipment[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = equipment;

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
        <span className="text-foreground font-medium">Equipment Management</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Wrench className="h-6 w-6" />
            Equipment Management
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Asset tracking, calibration, and maintenance scheduling</p>
        </div>
        {!permLoading && canWriteEq && (
        <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Add Equipment</Button>
        )}
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search by tag, name, serial..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading…" : `${totalItems} assets`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Asset Tag</th>
                  <th className="pb-2 pr-4 font-medium">Name</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Manufacturer</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Location</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden lg:table-cell">Next Calibration</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">{Array.from({ length: 6 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-24" /></td>))}</tr>
                )) : paginated.map((eq) => {
                  const cfg = STATUS_CONFIG[eq.status] ?? { label: eq.status, color: "" };
                  return (
                    <tr
                      key={eq.id}
                      role="link"
                      tabIndex={0}
                      onClick={() => router.push(`/qms/equipment/${eq.id}` as Route)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter" || e.key === " ") {
                          e.preventDefault();
                          router.push(`/qms/equipment/${eq.id}` as Route);
                        }
                      }}
                      className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer"
                    >
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{eq.asset_tag}</td>
                      <td className="py-3 pr-4 font-medium">{eq.name}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{eq.manufacturer}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">{eq.location ?? "—"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{cfg.label}</span></td>
                      <td className="py-3 text-muted-foreground text-xs hidden lg:table-cell">
                        {eq.next_calibration_date || eq.next_calibration
                          ? new Date(String(eq.next_calibration_date ?? eq.next_calibration)).toLocaleDateString()
                          : "—"}
                      </td>
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
