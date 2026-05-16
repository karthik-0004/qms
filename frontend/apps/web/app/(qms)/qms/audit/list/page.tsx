"use client";

import { useState } from "react";
import Link from "next/link";
import { useAudits, useCreateAudit } from "@/lib/hooks/queries/qms";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Plus, Search, ClipboardCheck, ChevronLeft } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

const STATUS_COLOR: Record<string, string> = {
  planned: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-gray-100 text-gray-600",
};

const TYPE_COLOR: Record<string, string> = {
  internal: "bg-purple-100 text-purple-700",
  external: "bg-orange-100 text-orange-700",
  supplier: "bg-cyan-100 text-cyan-700",
  regulatory: "bg-red-100 text-red-700",
};

export default function AuditListPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [showCreate, setShowCreate] = useState(false);

  const { data: page, isLoading } = useAudits({
    status: statusFilter !== "all" ? statusFilter : undefined,
    audit_type: typeFilter !== "all" ? typeFilter : undefined,
    page: 1,
    page_size: 100,
  });

  const createAudit = useCreateAudit();

  const audits = (page?.items ?? []).filter((a) =>
    search ? a.title.toLowerCase().includes(search.toLowerCase()) || a.audit_number.toLowerCase().includes(search.toLowerCase()) : true,
  );

  const [form, setForm] = useState({
    audit_number: `AUD-${Date.now().toString().slice(-6)}`,
    title: "",
    audit_type: "internal",
    scope: "",
    criteria: "",
    scheduled_start: "",
    scheduled_end: "",
  });

  async function handleCreate() {
    if (!form.title.trim() || !form.audit_number.trim()) {
      toast.error("Title and audit number are required");
      return;
    }
    try {
      await createAudit.mutateAsync({
        audit_number: form.audit_number,
        title: form.title,
        audit_type: form.audit_type,
        scope: form.scope || null,
        criteria: form.criteria || null,
        scheduled_start: form.scheduled_start || null,
        scheduled_end: form.scheduled_end || null,
      });
      toast.success("Audit created");
      setShowCreate(false);
      setForm({ audit_number: `AUD-${Date.now().toString().slice(-6)}`, title: "", audit_type: "internal", scope: "", criteria: "", scheduled_start: "", scheduled_end: "" });
    } catch {
      toast.error("Failed to create audit");
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/qms/audit">
          <Button variant="ghost" size="sm">
            <ChevronLeft className="w-4 h-4 mr-1" />
            Dashboard
          </Button>
        </Link>
        <div>
          <h1 className="text-xl font-semibold text-gray-900">All Audits</h1>
          <p className="text-sm text-gray-500">{page?.total ?? 0} total records</p>
        </div>
        <div className="ml-auto">
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-2" />
            New Audit
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input
            className="pl-9 h-9 text-sm"
            placeholder="Search audits…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="h-9 text-sm w-36">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="planned">Planned</SelectItem>
            <SelectItem value="in_progress">In Progress</SelectItem>
            <SelectItem value="completed">Completed</SelectItem>
            <SelectItem value="cancelled">Cancelled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={typeFilter} onValueChange={setTypeFilter}>
          <SelectTrigger className="h-9 text-sm w-36">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            <SelectItem value="internal">Internal</SelectItem>
            <SelectItem value="external">External</SelectItem>
            <SelectItem value="supplier">Supplier</SelectItem>
            <SelectItem value="regulatory">Regulatory</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Audit #</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Title</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Type</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Scheduled</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Findings</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Major NCs</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center text-gray-400">Loading…</td>
              </tr>
            ) : audits.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-4 py-10 text-center">
                  <ClipboardCheck className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No audits found</p>
                </td>
              </tr>
            ) : (
              audits.map((audit) => (
                <tr key={audit.id} className="hover:bg-gray-50 cursor-pointer">
                  <td className="px-4 py-3">
                    <Link href={`/qms/audit/${audit.id}`} className="text-blue-600 hover:underline font-medium">
                      {audit.audit_number}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <Link href={`/qms/audit/${audit.id}`} className="text-gray-900 hover:text-blue-600">
                      {audit.title}
                    </Link>
                  </td>
                  <td className="px-4 py-3">
                    <Badge className={`text-xs ${TYPE_COLOR[audit.audit_type] ?? "bg-gray-100 text-gray-600"}`}>
                      {audit.audit_type}
                    </Badge>
                  </td>
                  <td className="px-4 py-3">
                    <Badge className={`text-xs ${STATUS_COLOR[audit.status] ?? "bg-gray-100 text-gray-600"}`}>
                      {audit.status.replace("_", " ")}
                    </Badge>
                  </td>
                  <td className="px-4 py-3 text-gray-600">
                    {audit.scheduled_start ? format(new Date(audit.scheduled_start), "MMM d, yyyy") : "—"}
                  </td>
                  <td className="px-4 py-3 text-gray-700 font-medium">{audit.finding_count}</td>
                  <td className="px-4 py-3">
                    {audit.major_nc_count > 0 ? (
                      <span className="text-red-600 font-medium">{audit.major_nc_count}</span>
                    ) : (
                      <span className="text-gray-400">0</span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Create Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Create New Audit</DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Audit Number *</Label>
                <Input
                  className="h-9 text-sm"
                  value={form.audit_number}
                  onChange={(e) => setForm((f) => ({ ...f, audit_number: e.target.value }))}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Type *</Label>
                <Select value={form.audit_type} onValueChange={(v) => setForm((f) => ({ ...f, audit_type: v }))}>
                  <SelectTrigger className="h-9 text-sm">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="internal">Internal</SelectItem>
                    <SelectItem value="external">External</SelectItem>
                    <SelectItem value="supplier">Supplier</SelectItem>
                    <SelectItem value="regulatory">Regulatory</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Title *</Label>
              <Input
                className="h-9 text-sm"
                placeholder="e.g. Q2 Internal Quality Audit"
                value={form.title}
                onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Scope</Label>
              <Textarea
                className="text-sm resize-none"
                rows={2}
                placeholder="Departments / processes in scope"
                value={form.scope}
                onChange={(e) => setForm((f) => ({ ...f, scope: e.target.value }))}
              />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Criteria / Standards</Label>
              <Input
                className="h-9 text-sm"
                placeholder="e.g. ISO 9001:2015, SOP-QMS-001"
                value={form.criteria}
                onChange={(e) => setForm((f) => ({ ...f, criteria: e.target.value }))}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Scheduled Start</Label>
                <Input
                  type="date"
                  className="h-9 text-sm"
                  value={form.scheduled_start}
                  onChange={(e) => setForm((f) => ({ ...f, scheduled_start: e.target.value }))}
                />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Scheduled End</Label>
                <Input
                  type="date"
                  className="h-9 text-sm"
                  value={form.scheduled_end}
                  onChange={(e) => setForm((f) => ({ ...f, scheduled_end: e.target.value }))}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>
              Cancel
            </Button>
            <Button
              size="sm"
              className="bg-blue-600 hover:bg-blue-700 text-white"
              disabled={createAudit.isPending}
              onClick={handleCreate}
            >
              {createAudit.isPending ? "Creating…" : "Create Audit"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
