"use client";

import { useState } from "react";
import Link from "next/link";
import { useRisks, useCreateRisk } from "@/lib/hooks/queries/qms";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ShieldAlert, Plus, Search } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import type { Risk } from "@/lib/api/services/qms";

// ── Risk helpers ──────────────────────────────────────────────────────────────

function riskColor(score: number) {
  if (score >= 15) return { bg: "bg-red-500", text: "text-red-700", label: "Critical" };
  if (score >= 10) return { bg: "bg-orange-400", text: "text-orange-700", label: "High" };
  if (score >= 5) return { bg: "bg-yellow-400", text: "text-yellow-700", label: "Medium" };
  return { bg: "bg-green-400", text: "text-green-700", label: "Low" };
}

function cellColor(s: number, l: number) {
  const score = s * l;
  if (score >= 15) return "bg-red-100 hover:bg-red-200 border-red-200";
  if (score >= 10) return "bg-orange-100 hover:bg-orange-200 border-orange-200";
  if (score >= 5) return "bg-yellow-100 hover:bg-yellow-200 border-yellow-200";
  return "bg-green-100 hover:bg-green-200 border-green-200";
}

// ── 5x5 Matrix ────────────────────────────────────────────────────────────────

function RiskMatrix({ risks }: { risks: Risk[] }) {
  const severities = [5, 4, 3, 2, 1];
  const likelihoods = [1, 2, 3, 4, 5];

  function risksAt(s: number, l: number) {
    return risks.filter((r) => r.severity === s && r.likelihood === l);
  }

  return (
    <div className="overflow-auto">
      <div className="flex items-start gap-3">
        {/* Y-axis label */}
        <div className="flex flex-col items-center justify-center w-6 shrink-0" style={{ height: 5 * 56 + 4 * 4 }}>
          <span className="text-xs text-gray-500 font-medium -rotate-90 whitespace-nowrap">Severity →</span>
        </div>
        <div>
          <div className="flex gap-1">
            {/* Empty corner */}
            <div className="w-24 shrink-0" />
            {/* Likelihood labels */}
            {likelihoods.map((l) => (
              <div key={l} className="w-14 text-center text-xs text-gray-500 font-medium pb-1">L{l}</div>
            ))}
          </div>
          <div className="space-y-1">
            {severities.map((s) => (
              <div key={s} className="flex items-center gap-1">
                <div className="w-24 shrink-0 text-xs text-gray-500 font-medium text-right pr-3">S{s}</div>
                {likelihoods.map((l) => {
                  const cellRisks = risksAt(s, l);
                  return (
                    <div
                      key={l}
                      className={`w-14 h-14 border rounded flex flex-col items-center justify-center text-xs font-semibold transition-colors ${cellColor(s, l)}`}
                    >
                      <span className="text-gray-500 text-[10px]">{s * l}</span>
                      {cellRisks.length > 0 && (
                        <span className="bg-white rounded-full w-5 h-5 flex items-center justify-center text-xs font-bold text-gray-700 shadow-sm mt-0.5">
                          {cellRisks.length}
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>
            ))}
          </div>
          <div className="flex gap-1 mt-2">
            <div className="w-24 shrink-0" />
            <div className="text-xs text-gray-500 font-medium text-center flex-1">← Likelihood →</div>
          </div>
        </div>
      </div>
      {/* Legend */}
      <div className="flex items-center gap-4 mt-4">
        {[
          { color: "bg-green-400", label: "Low (1–4)" },
          { color: "bg-yellow-400", label: "Medium (5–9)" },
          { color: "bg-orange-400", label: "High (10–14)" },
          { color: "bg-red-500", label: "Critical (15–25)" },
        ].map(({ color, label }) => (
          <div key={label} className="flex items-center gap-1.5">
            <div className={`w-3 h-3 rounded ${color}`} />
            <span className="text-xs text-gray-600">{label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────────

const STATUS_COLOR: Record<string, string> = {
  identified: "bg-blue-100 text-blue-700",
  assessed: "bg-purple-100 text-purple-700",
  mitigating: "bg-yellow-100 text-yellow-700",
  mitigated: "bg-green-100 text-green-700",
  accepted: "bg-gray-100 text-gray-600",
  closed: "bg-gray-100 text-gray-500",
};

export default function RiskPage() {
  const [search, setSearch] = useState("");
  const [showCreate, setShowCreate] = useState(false);
  const [view, setView] = useState<"list" | "matrix">("list");

  const { data: page, isLoading } = useRisks({ page: 1, page_size: 200 });
  const createRisk = useCreateRisk();

  const risks = (page?.items ?? []).filter((r) =>
    search ? r.description.toLowerCase().includes(search.toLowerCase()) || r.risk_id.toLowerCase().includes(search.toLowerCase()) : true,
  );

  const [form, setForm] = useState({
    risk_id: `RISK-${Date.now().toString().slice(-5)}`,
    category: "operational",
    description: "",
    severity: "3",
    likelihood: "3",
    mitigation_plan: "",
  });

  async function handleCreate() {
    if (!form.description.trim()) { toast.error("Description is required"); return; }
    try {
      const created = await createRisk.mutateAsync({
        risk_id: form.risk_id,
        category: form.category,
        description: form.description,
        severity: Number(form.severity),
        likelihood: Number(form.likelihood),
        mitigation_plan: form.mitigation_plan || null,
      });
      toast.success("Risk created");
      setShowCreate(false);
      window.location.href = `/qms/risk/${created.id}`;
    } catch { toast.error("Failed to create risk"); }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Risk Management</h1>
          <p className="text-sm text-gray-500 mt-1">Identify, assess, and mitigate organizational risks</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex border border-gray-200 rounded overflow-hidden text-sm">
            <button onClick={() => setView("list")} className={`px-3 py-1.5 ${view === "list" ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-50"}`}>List</button>
            <button onClick={() => setView("matrix")} className={`px-3 py-1.5 ${view === "matrix" ? "bg-blue-600 text-white" : "text-gray-600 hover:bg-gray-50"}`}>Matrix</button>
          </div>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
            <Plus className="w-4 h-4 mr-2" />
            Add Risk
          </Button>
        </div>
      </div>

      {view === "matrix" ? (
        <Card className="border border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold">Risk Matrix (Severity × Likelihood)</CardTitle>
          </CardHeader>
          <CardContent>
            <RiskMatrix risks={risks} />
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Filters */}
          <div className="relative max-w-sm">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
            <Input className="pl-9 h-9 text-sm" placeholder="Search risks…" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>

          {/* Table */}
          <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Risk ID</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Description</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Category</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Score</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                  <th className="text-left px-4 py-3 font-medium text-gray-600">Created</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {isLoading ? (
                  <tr><td colSpan={6} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
                ) : risks.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-12 text-center">
                      <ShieldAlert className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                      <p className="text-gray-400 text-sm">No risks registered</p>
                    </td>
                  </tr>
                ) : risks.map((r) => {
                  const { bg, label } = riskColor(r.risk_score);
                  return (
                    <tr key={r.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">
                        <Link href={`/qms/risk/${r.id}`} className="text-blue-600 hover:underline font-medium">{r.risk_id}</Link>
                      </td>
                      <td className="px-4 py-3">
                        <Link href={`/qms/risk/${r.id}`} className="text-gray-900 hover:text-blue-600 line-clamp-2">{r.description}</Link>
                      </td>
                      <td className="px-4 py-3 text-gray-600 capitalize">{r.category}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <div className={`w-6 h-6 rounded flex items-center justify-center text-white text-xs font-bold ${bg}`}>{r.risk_score}</div>
                          <span className="text-xs text-gray-500">{label}</span>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge className={`text-xs ${STATUS_COLOR[r.status] ?? "bg-gray-100 text-gray-600"}`}>{r.status}</Badge>
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{format(new Date(r.created_at), "MMM d, yyyy")}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}

      {/* Create Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Add Risk</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Risk ID *</Label>
                <Input className="h-9 text-sm" value={form.risk_id} onChange={(e) => setForm((f) => ({ ...f, risk_id: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Category *</Label>
                <Select value={form.category} onValueChange={(v) => setForm((f) => ({ ...f, category: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="operational">Operational</SelectItem>
                    <SelectItem value="quality">Quality</SelectItem>
                    <SelectItem value="regulatory">Regulatory</SelectItem>
                    <SelectItem value="safety">Safety</SelectItem>
                    <SelectItem value="financial">Financial</SelectItem>
                    <SelectItem value="strategic">Strategic</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Description *</Label>
              <Textarea className="text-sm resize-none" rows={3} placeholder="Describe the risk…" value={form.description} onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Severity (1–5)</Label>
                <Select value={form.severity} onValueChange={(v) => setForm((f) => ({ ...f, severity: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5].map((n) => <SelectItem key={n} value={String(n)}>{n}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Likelihood (1–5)</Label>
                <Select value={form.likelihood} onValueChange={(v) => setForm((f) => ({ ...f, likelihood: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    {[1, 2, 3, 4, 5].map((n) => <SelectItem key={n} value={String(n)}>{n}</SelectItem>)}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="text-xs text-gray-500 bg-gray-50 rounded p-2">
              Risk score: <strong>{Number(form.severity) * Number(form.likelihood)}</strong> — {riskColor(Number(form.severity) * Number(form.likelihood)).label}
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Mitigation Plan</Label>
              <Textarea className="text-sm resize-none" rows={2} placeholder="How will this risk be mitigated?" value={form.mitigation_plan} onChange={(e) => setForm((f) => ({ ...f, mitigation_plan: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={createRisk.isPending} onClick={handleCreate}>
              {createRisk.isPending ? "Creating…" : "Add Risk"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
