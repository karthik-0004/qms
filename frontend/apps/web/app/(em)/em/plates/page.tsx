"use client";

import { useState } from "react";
import {
  ChevronLeft,
  ChevronRight,
  FlaskConical,
  Plus,
  Search,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { usePlates } from "@/lib/hooks/queries/em";
import type { Plate } from "@/lib/api/services/em";

const STATUS_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline"; color: string }> = {
  registered: { label: "Registered", variant: "secondary", color: "bg-slate-100 text-slate-700" },
  sampling_in_progress: { label: "Sampling", variant: "secondary", color: "bg-blue-50 text-blue-700" },
  sampled: { label: "Sampled", variant: "secondary", color: "bg-blue-100 text-blue-800" },
  incubation_started: { label: "Incubating", variant: "default", color: "bg-amber-50 text-amber-700" },
  incubation_complete: { label: "Incubation Done", variant: "default", color: "bg-amber-100 text-amber-800" },
  imaging_pending: { label: "Imaging Pending", variant: "outline", color: "bg-purple-50 text-purple-700" },
  imaging_in_progress: { label: "Imaging", variant: "default", color: "bg-purple-100 text-purple-800" },
  imaging_complete: { label: "Imaged", variant: "default", color: "bg-purple-200 text-purple-900" },
  ai_analysis_pending: { label: "AI Queued", variant: "outline", color: "bg-cyan-50 text-cyan-700" },
  ai_analysis_running: { label: "AI Running", variant: "default", color: "bg-cyan-100 text-cyan-800" },
  ai_analysis_complete: { label: "AI Done", variant: "default", color: "bg-cyan-200 text-cyan-900" },
  ai_analysis_failed: { label: "AI Failed", variant: "destructive", color: "bg-red-50 text-red-700" },
  qa_review_pending: { label: "QA Pending", variant: "outline", color: "bg-orange-50 text-orange-700" },
  qa_review_in_progress: { label: "In QA Review", variant: "default", color: "bg-orange-100 text-orange-800" },
  approved: { label: "Approved", variant: "default", color: "bg-green-100 text-green-800" },
  rejected: { label: "Rejected", variant: "destructive", color: "bg-red-100 text-red-800" },
  cancelled: { label: "Cancelled", variant: "destructive", color: "bg-slate-100 text-slate-500" },
};

const SAMPLE_TYPES = ["settle_plate", "contact_plate", "air_sample", "surface_sample", "water_sample"];
const PAGE_SIZE = 10;

export default function PlatesPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sampleTypeFilter, setSampleTypeFilter] = useState("all");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = usePlates({
    search: search || undefined,
    status: statusFilter !== "all" ? statusFilter : undefined,
    plate_type: sampleTypeFilter !== "all" ? sampleTypeFilter : undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const plates: Plate[] = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FlaskConical className="h-6 w-6 text-muted-foreground" />
          <div>
            <h1 className="text-2xl font-bold tracking-tight">Plates</h1>
            <p className="text-sm text-muted-foreground">
              EM plate registry and tracking
            </p>
          </div>
        </div>
        <Button>
          <Plus className="mr-2 h-4 w-4" />
          Register Plate
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4 pb-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by barcode..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="pl-9"
              />
            </div>
            <Select value={statusFilter} onValueChange={(v) => { setStatusFilter(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-52">
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
                  <SelectItem key={key} value={key}>{cfg.label}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={sampleTypeFilter} onValueChange={(v) => { setSampleTypeFilter(v); setPage(1); }}>
              <SelectTrigger className="w-full sm:w-44">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                {SAMPLE_TYPES.map((t) => (
                  <SelectItem key={t} value={t}>{t.replace(/_/g, " ")}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">
            {loading ? <Skeleton className="h-4 w-32" /> : `${total} plates found`}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-muted-foreground">
                  <th className="text-left py-3 pr-4 font-medium">Barcode</th>
                  <th className="text-left py-3 pr-4 font-medium hidden sm:table-cell">Type</th>
                  <th className="text-left py-3 pr-4 font-medium hidden md:table-cell">Media</th>
                  <th className="text-left py-3 pr-4 font-medium hidden lg:table-cell">Location</th>
                  <th className="text-left py-3 pr-4 font-medium">Status</th>
                  <th className="text-left py-3 font-medium hidden md:table-cell">Created</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-36" /></td>
                      <td className="py-3 pr-4 hidden sm:table-cell"><Skeleton className="h-4 w-24" /></td>
                      <td className="py-3 pr-4 hidden md:table-cell"><Skeleton className="h-4 w-16" /></td>
                      <td className="py-3 pr-4 hidden lg:table-cell"><Skeleton className="h-4 w-24" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-5 w-24 rounded-full" /></td>
                      <td className="py-3 hidden md:table-cell"><Skeleton className="h-4 w-24" /></td>
                    </tr>
                  ))
                  : plates.map((plate) => {
                    const cfg = STATUS_CONFIG[plate.status] ?? { label: plate.status, variant: "outline" as const, color: "" };
                    return (
                      <tr
                        key={plate.id}
                        className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer"
                      >
                        <td className="py-3 pr-4 font-mono font-semibold text-xs">
                          {plate.barcode}
                        </td>
                        <td className="py-3 pr-4 capitalize text-muted-foreground hidden sm:table-cell">
                          {plate.plate_type.replace(/_/g, " ")}
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">
                          {plate.media_type}
                        </td>
                        <td className="py-3 pr-4 font-mono text-xs text-muted-foreground hidden lg:table-cell">
                          {plate.location ?? "—"}
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>
                            {cfg.label}
                          </span>
                        </td>
                        <td className="py-3 text-muted-foreground text-xs hidden md:table-cell">
                          {new Date(plate.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!loading && totalPages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t mt-4">
              <p className="text-sm text-muted-foreground">
                Page {page} of {totalPages} · {total} results
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
