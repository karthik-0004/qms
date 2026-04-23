"use client";

import { useState, useCallback } from "react";
import {
  FileText,
  Search,
  Plus,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useContracts } from "@/lib/hooks/queries/ccv";
import type { Contract } from "@/lib/api/services/ccv";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-slate-100 text-slate-700" },
  under_review: { label: "Under Review", color: "bg-amber-100 text-amber-800" },
  approved: { label: "Approved", color: "bg-blue-100 text-blue-800" },
  active: { label: "Active", color: "bg-green-100 text-green-800" },
  expired: { label: "Expired", color: "bg-slate-100 text-slate-500" },
  terminated: { label: "Terminated", color: "bg-red-100 text-red-700" },
  cancelled: { label: "Cancelled", color: "bg-red-50 text-red-600" },
};

const CONTRACT_TYPES = [
  "service_agreement",
  "maintenance_contract",
  "calibration_contract",
  "validation_contract",
  "supply_agreement",
  "nda",
  "other",
];

const PAGE_SIZE = 10;

export default function ContractsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useContracts({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const contracts: Contract[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = contracts;

  const handleSearch = useCallback((val: string) => {
    setSearch(val);
    setPage(1);
  }, []);

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Contracts
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage service agreements, maintenance contracts, and NDAs
          </p>
        </div>
        <Button size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" />
          New Contract
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by number, title, customer…"
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
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm capitalize"
            >
              <option value="">All Types</option>
              {CONTRACT_TYPES.map((t) => (
                <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {loading ? "Loading…" : `${totalItems} contracts`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Number</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Customer</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Type</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Value</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden md:table-cell">End Date</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-28" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-40" /></td>
                      <td className="py-3 pr-4 hidden sm:table-cell"><Skeleton className="h-4 w-32" /></td>
                      <td className="py-3 pr-4 hidden md:table-cell"><Skeleton className="h-4 w-24" /></td>
                      <td className="py-3 pr-4 hidden lg:table-cell"><Skeleton className="h-4 w-16" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-5 w-20 rounded-full" /></td>
                      <td className="py-3 hidden md:table-cell"><Skeleton className="h-4 w-20" /></td>
                    </tr>
                  ))
                  : paginated.map((c) => {
                    const cfg = STATUS_CONFIG[c.status] ?? { label: c.status, color: "" };
                    return (
                      <tr
                        key={c.id}
                        className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer"
                      >
                        <td className="py-3 pr-4 font-mono font-semibold text-xs">
                          {c.contract_number}
                        </td>
                        <td className="py-3 pr-4 font-medium max-w-[200px] truncate">
                          {c.title}
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">
                          {c.customer_name}
                        </td>
                        <td className="py-3 pr-4 capitalize text-muted-foreground hidden md:table-cell">
                          {c.contract_type.replace(/_/g, " ")}
                        </td>
                        <td className="py-3 pr-4 font-medium hidden lg:table-cell">
                          {c.total_value > 0 ? `$${c.total_value.toLocaleString()}` : "—"}
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>
                            {cfg.label}
                          </span>
                        </td>
                        <td className="py-3 text-muted-foreground text-xs hidden md:table-cell">
                          {c.end_date ? new Date(c.end_date).toLocaleDateString() : "—"}
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
