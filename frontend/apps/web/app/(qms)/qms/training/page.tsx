"use client";

import { useState } from "react";
import { GraduationCap, Plus, Search, ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useCourses } from "@/lib/hooks/queries/qms";
import type { Course } from "@/lib/api/services/qms";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-green-100 text-green-700" },
  draft: { label: "Draft", color: "bg-slate-100 text-slate-600" },
  archived: { label: "Archived", color: "bg-slate-100 text-slate-500" },
  under_review: { label: "Under Review", color: "bg-amber-100 text-amber-700" },
};

const PAGE_SIZE = 10;

export default function TrainingPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading: loading } = useCourses({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const courses: Course[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = courses;

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <GraduationCap className="h-6 w-6" />
            Training Management
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Courses, assignments, and compliance tracking</p>
        </div>
        <Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />New Course</Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search courses..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading…" : `${totalItems} courses`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Code</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Category</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Format</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Duration</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Progress</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">{Array.from({ length: 7 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-20" /></td>))}</tr>
                )) : paginated.map((c) => {
                  const cfg = STATUS_CONFIG[c.status] ?? { label: c.status, color: "" };
                  const pct = c.enrolled > 0 ? Math.round((c.completed / c.enrolled) * 100) : 0;
                  return (
                    <tr key={c.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer">
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{c.course_code}</td>
                      <td className="py-3 pr-4 font-medium max-w-[200px] truncate">{c.title}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{c.category}</td>
                      <td className="py-3 pr-4 capitalize text-muted-foreground hidden md:table-cell">{c.format.replace(/_/g, " ")}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden lg:table-cell">{c.duration_hours}h</td>
                      <td className="py-3 pr-4 hidden md:table-cell">
                        <div className="flex items-center gap-2">
                          <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden max-w-[80px]">
                            <div className="h-full bg-blue-500 rounded-full" style={{ width: `${pct}%` }} />
                          </div>
                          <span className="text-xs text-muted-foreground">{c.completed}/{c.enrolled}</span>
                        </div>
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
