"use client";

import { useState } from "react";
import Link from "next/link";
import { usePTPrograms, useCreatePTProgram } from "@/lib/hooks/queries/qms";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { FlaskConical, Plus, CheckCircle2, Clock, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import type { PTProgram } from "@/lib/api/services/qms";

export default function PTDashboardPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data: page, isLoading } = usePTPrograms({ page: 1, page_size: 50 });
  const create = useCreatePTProgram();

  const programs: PTProgram[] = page?.items ?? [];

  const [form, setForm] = useState({
    provider: "",
    scheme_name: "",
    parameter: "",
    frequency_months: "12",
  });

  async function handleCreate() {
    if (!form.provider.trim() || !form.scheme_name.trim() || !form.parameter.trim()) {
      toast.error("Provider, scheme name, and parameter are required");
      return;
    }
    try {
      await create.mutateAsync({
        provider: form.provider,
        scheme_name: form.scheme_name,
        parameter: form.parameter,
        frequency_months: Number(form.frequency_months),
      });
      toast.success("PT Program created");
      setShowCreate(false);
      setForm({ provider: "", scheme_name: "", parameter: "", frequency_months: "12" });
    } catch { toast.error("Failed to create program"); }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Proficiency Testing</h1>
          <p className="text-sm text-gray-500 mt-1">Track PT programs, rounds, and z-scores for ISO 17025 compliance</p>
        </div>
        <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Program
        </Button>
      </div>

      {/* KPI tiles */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { label: "Active Programs", value: programs.length, icon: FlaskConical, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Annual Frequency", value: programs.filter((p) => p.frequency_months <= 12).length, icon: Clock, color: "text-green-600", bg: "bg-green-50" },
          { label: "Parameters Covered", value: new Set(programs.map((p) => p.parameter)).size, icon: CheckCircle2, color: "text-purple-600", bg: "bg-purple-50" },
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

      {/* Programs table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700">PT Programs</h2>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Scheme Name</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Provider</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Parameter</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Frequency</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Created</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={5} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
            ) : programs.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-12 text-center">
                  <FlaskConical className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No PT programs yet</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={() => setShowCreate(true)}>Add First Program</Button>
                </td>
              </tr>
            ) : programs.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link href={`/qms/pt/programs/${p.id}`} className="text-blue-600 hover:underline font-medium">{p.scheme_name}</Link>
                </td>
                <td className="px-4 py-3 text-gray-600">{p.provider}</td>
                <td className="px-4 py-3">
                  <Badge variant="outline" className="text-xs">{p.parameter}</Badge>
                </td>
                <td className="px-4 py-3 text-gray-600">Every {p.frequency_months} month{p.frequency_months !== 1 ? "s" : ""}</td>
                <td className="px-4 py-3 text-gray-500">{format(new Date(p.created_at), "MMM d, yyyy")}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>New PT Program</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs">Provider / PT Organization *</Label>
              <Input className="h-9 text-sm" placeholder="e.g. FAPAS, LGC, NEQAS" value={form.provider} onChange={(e) => setForm((f) => ({ ...f, provider: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Scheme Name *</Label>
              <Input className="h-9 text-sm" placeholder="e.g. Microbiology Water PT" value={form.scheme_name} onChange={(e) => setForm((f) => ({ ...f, scheme_name: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Parameter *</Label>
              <Input className="h-9 text-sm" placeholder="e.g. E. coli, pH, Heavy Metals" value={form.parameter} onChange={(e) => setForm((f) => ({ ...f, parameter: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Frequency (months)</Label>
              <Input type="number" min="1" max="60" className="h-9 text-sm" value={form.frequency_months} onChange={(e) => setForm((f) => ({ ...f, frequency_months: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={create.isPending} onClick={handleCreate}>
              {create.isPending ? "Creating…" : "Create Program"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
