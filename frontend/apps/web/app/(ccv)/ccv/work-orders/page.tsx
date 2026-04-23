"use client";

import { useState, useCallback } from "react";
import {
  Wrench,
  Search,
  Plus,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useWorkOrders } from "@/lib/hooks/queries/ccv";
import type { WorkOrder } from "@/lib/api/services/ccv";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  pending: { label: "Pending", color: "bg-slate-100 text-slate-700" },
  assigned: { label: "Assigned", color: "bg-blue-100 text-blue-800" },
  in_progress: { label: "In Progress", color: "bg-amber-100 text-amber-800" },
  on_hold: { label: "On Hold", color: "bg-orange-100 text-orange-800" },
  completed: { label: "Completed", color: "bg-green-100 text-green-800" },
  cancelled: { label: "Cancelled", color: "bg-red-100 text-red-700" },
};

const PRIORITY_CONFIG: Record<string, { label: string; color: string }> = {
  low: { label: "Low", color: "bg-slate-100 text-slate-600" },
  normal: { label: "Normal", color: "bg-blue-50 text-blue-700" },
  high: { label: "High", color: "bg-orange-100 text-orange-800" },
  urgent: { label: "Urgent", color: "bg-red-100 text-red-800" },
};

const WO_TYPES = [
  "installation", "maintenance", "repair", "calibration",
  "inspection", "validation", "emergency", "other",
];

const PAGE_SIZE = 10;

export default function WorkOrdersPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [priorityFilter, setPriorityFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useWorkOrders({
    search: search || undefined,
    status: statusFilter || undefined,
    priority: priorityFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const workOrders: WorkOrder[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = workOrders;

  const handleSearch = useCallback((val: string) => {
    setSearch(val);
    setPage(1);
  }, []);

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Wrench className="h-6 w-6" />
            Work Orders
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Field service requests, technician dispatch, and completion tracking
          </p>
        </div>
        <Button size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" />
          New Work Order
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by WO#, title, customer, technician…"
                className="pl-8"
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
            <select
              value={priorityFilter}
              onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">All Priorities</option>
              {Object.entries(PRIORITY_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {loading ? "Loading\u2026" : `${totalItems} work orders`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">WO#</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Customer</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Type</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Technician</th>
                  <th className="pb-2 pr-4 font-medium">Priority</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden md:table-cell">Scheduled</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-28" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-40" /></td>
                      <td className="py-3 pr-4 hidden sm:table-cell"><Skeleton className="h-4 w-28" /></td>
                      <td className="py-3 pr-4 hidden md:table-cell"><Skeleton className="h-4 w-20" /></td>
                      <td className="py-3 pr-4 hidden lg:table-cell"><Skeleton className="h-4 w-24" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-5 w-16 rounded-full" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-5 w-20 rounded-full" /></td>
                      <td className="py-3 hidden md:table-cell"><Skeleton className="h-4 w-20" /></td>
                    </tr>
                  ))
                  : paginated.map((wo) => {
                    const scfg = STATUS_CONFIG[wo.status] ?? { label: wo.status, color: "" };
                    const pcfg = PRIORITY_CONFIG[wo.priority] ?? { label: wo.priority, color: "" };
                    return (
                      <tr
                        key={wo.id}
                        className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer"
                      >
                        <td className="py-3 pr-4 font-mono font-semibold text-xs">
                          {wo.work_order_number}
                        </td>
                        <td className="py-3 pr-4 font-medium max-w-[180px] truncate">
                          {wo.title}
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">
                          {wo.customer_name}
                        </td>
                        <td className="py-3 pr-4 capitalize text-muted-foreground hidden md:table-cell">
                          —
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden lg:table-cell">
                          {wo.assigned_technician_id ?? <span className="text-muted-foreground/50 italic">Unassigned</span>}
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded px-1.5 py-0.5 text-xs font-semibold ${pcfg.color}`}>
                            {pcfg.label}
                          </span>
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${scfg.color}`}>
                            {scfg.label}
                          </span>
                        </td>
                        <td className="py-3 text-muted-foreground text-xs hidden md:table-cell">
                          {wo.scheduled_date
                            ? new Date(wo.scheduled_date).toLocaleDateString()
                            : "—"}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!loading && totalItems > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">
                Page {page} of {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
