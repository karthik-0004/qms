"use client";

import { useState } from "react";
import Link from "next/link";
import { useComplaints, useCreateComplaint } from "@/lib/hooks/queries/qms";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
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
import {
  MessageSquareWarning,
  Plus,
  Search,
  AlertTriangle,
  CheckCircle2,
  Clock,
} from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

const STATUS_COLOR: Record<string, string> = {
  open: "bg-blue-100 text-blue-700",
  investigating: "bg-yellow-100 text-yellow-700",
  responded: "bg-green-100 text-green-700",
  closed: "bg-gray-100 text-gray-600",
};

const SEVERITY_COLOR: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  major: "bg-orange-100 text-orange-700",
  minor: "bg-yellow-100 text-yellow-700",
  observation: "bg-blue-100 text-blue-700",
};

export default function ComplaintsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [showCreate, setShowCreate] = useState(false);

  const { data: page, isLoading } = useComplaints({
    status: statusFilter !== "all" ? statusFilter : undefined,
    page: 1,
    page_size: 100,
  });
  const createComplaint = useCreateComplaint();

  const complaints = (page?.items ?? []).filter((c) =>
    search
      ? c.complaint_number.toLowerCase().includes(search.toLowerCase()) ||
        (c.customer_name ?? "").toLowerCase().includes(search.toLowerCase()) ||
        c.description.toLowerCase().includes(search.toLowerCase())
      : true,
  );

  const total = page?.total ?? 0;
  const open = complaints.filter((c) => c.status === "open").length;
  const investigating = complaints.filter((c) => c.status === "investigating").length;
  const responded = complaints.filter((c) => ["responded", "closed"].includes(c.status)).length;

  const [form, setForm] = useState({
    complaint_number: `CMP-${Date.now().toString().slice(-6)}`,
    description: "",
    received_at: new Date().toISOString().slice(0, 10),
    customer_name: "",
    received_via: "email",
    severity: "minor",
    category: "",
  });

  async function handleCreate() {
    if (!form.description.trim()) { toast.error("Description is required"); return; }
    try {
      const created = await createComplaint.mutateAsync({
        complaint_number: form.complaint_number,
        description: form.description,
        received_at: new Date(form.received_at).toISOString(),
        customer_name: form.customer_name || null,
        received_via: form.received_via,
        severity: form.severity,
        category: form.category || null,
      });
      toast.success("Complaint created");
      setShowCreate(false);
      window.location.href = `/qms/complaints/${created.id}`;
    } catch { toast.error("Failed to create complaint"); }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Customer Complaints</h1>
          <p className="text-sm text-gray-500 mt-1">Track and resolve customer complaints end-to-end</p>
        </div>
        <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Complaint
        </Button>
      </div>

      {/* KPI tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total", value: total, icon: MessageSquareWarning, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Open", value: open, icon: Clock, color: "text-yellow-600", bg: "bg-yellow-50" },
          { label: "Investigating", value: investigating, icon: AlertTriangle, color: "text-orange-600", bg: "bg-orange-50" },
          { label: "Responded / Closed", value: responded, icon: CheckCircle2, color: "text-green-600", bg: "bg-green-50" },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <Card key={label} className="border border-gray-200">
            <CardContent className="p-4">
              <div className={`inline-flex p-2 rounded-lg ${bg} mb-3`}><Icon className={`w-5 h-5 ${color}`} /></div>
              <div className="text-2xl font-bold text-gray-900">{isLoading ? "—" : value}</div>
              <div className="text-xs text-gray-500 mt-1">{label}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <Input className="pl-9 h-9 text-sm" placeholder="Search complaints…" value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="h-9 text-sm w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="open">Open</SelectItem>
            <SelectItem value="investigating">Investigating</SelectItem>
            <SelectItem value="responded">Responded</SelectItem>
            <SelectItem value="closed">Closed</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Complaint #</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Description</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Severity</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Customer</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Received</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
            ) : complaints.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center">
                  <MessageSquareWarning className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No complaints found</p>
                </td>
              </tr>
            ) : complaints.map((c) => (
              <tr key={c.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link href={`/qms/complaints/${c.id}`} className="text-blue-600 hover:underline font-medium">{c.complaint_number}</Link>
                </td>
                <td className="px-4 py-3">
                  <Link href={`/qms/complaints/${c.id}`} className="text-gray-900 hover:text-blue-600 line-clamp-2 max-w-xs block">{c.description}</Link>
                </td>
                <td className="px-4 py-3">
                  <Badge className={`text-xs ${SEVERITY_COLOR[c.severity] ?? "bg-gray-100 text-gray-600"}`}>{c.severity}</Badge>
                </td>
                <td className="px-4 py-3">
                  <Badge className={`text-xs ${STATUS_COLOR[c.status] ?? "bg-gray-100 text-gray-600"}`}>{c.status}</Badge>
                </td>
                <td className="px-4 py-3 text-gray-600">{c.customer_name ?? "—"}</td>
                <td className="px-4 py-3 text-gray-500">{format(new Date(c.received_at), "MMM d, yyyy")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>New Complaint</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Complaint Number</Label>
                <Input className="h-9 text-sm" value={form.complaint_number} onChange={(e) => setForm((f) => ({ ...f, complaint_number: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Received Date *</Label>
                <Input type="date" className="h-9 text-sm" value={form.received_at} onChange={(e) => setForm((f) => ({ ...f, received_at: e.target.value }))} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Severity</Label>
                <Select value={form.severity} onValueChange={(v) => setForm((f) => ({ ...f, severity: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="critical">Critical</SelectItem>
                    <SelectItem value="major">Major</SelectItem>
                    <SelectItem value="minor">Minor</SelectItem>
                    <SelectItem value="observation">Observation</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Received Via</Label>
                <Select value={form.received_via} onValueChange={(v) => setForm((f) => ({ ...f, received_via: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="email">Email</SelectItem>
                    <SelectItem value="phone">Phone</SelectItem>
                    <SelectItem value="letter">Letter</SelectItem>
                    <SelectItem value="portal">Portal</SelectItem>
                    <SelectItem value="in_person">In Person</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Customer Name</Label>
                <Input className="h-9 text-sm" placeholder="Optional" value={form.customer_name} onChange={(e) => setForm((f) => ({ ...f, customer_name: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Category</Label>
                <Input className="h-9 text-sm" placeholder="e.g. Product, Service" value={form.category} onChange={(e) => setForm((f) => ({ ...f, category: e.target.value }))} />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Description *</Label>
              <Textarea className="text-sm resize-none" rows={3} placeholder="Describe the complaint…" value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={createComplaint.isPending} onClick={handleCreate}>
              {createComplaint.isPending ? "Creating…" : "Create Complaint"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
