"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { usePTProgram, usePTRounds, useCreatePTRound } from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { ChevronLeft, Plus, CheckCircle2, XCircle, Clock } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import type { PTRound } from "@/lib/api/services/qms";

const STATUS_COLOR: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600",
  sample_received: "bg-blue-100 text-blue-700",
  result_submitted: "bg-yellow-100 text-yellow-700",
  scored: "bg-purple-100 text-purple-700",
  satisfactory: "bg-green-100 text-green-700",
  unsatisfactory: "bg-red-100 text-red-700",
};

function ZScoreBadge({ z }: { z: number | null }) {
  if (z === null) return <span className="text-gray-400">—</span>;
  const abs = Math.abs(z);
  const color = abs <= 2 ? "text-green-600" : abs <= 3 ? "text-yellow-600" : "text-red-600";
  return <span className={`font-mono font-semibold ${color}`}>{z.toFixed(3)}</span>;
}

export default function PTProgramDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({
    round_id: `R-${Date.now().toString().slice(-5)}`,
    sample_received_date: "",
    result_due_date: "",
    notes: "",
  });

  const { data: program, isLoading: progLoading } = usePTProgram(id);
  const { data: rounds, isLoading: roundsLoading } = usePTRounds(id);
  const createRound = useCreatePTRound();

  if (progLoading) return <div className="p-6 flex items-center justify-center h-64 text-gray-400 text-sm">Loading…</div>;
  if (!program) return <div className="p-6 text-red-500">Program not found.</div>;

  const roundsList: PTRound[] = rounds ?? [];
  const satisfactory = roundsList.filter((r) => r.status === "satisfactory" || (r.z_score !== null && Math.abs(r.z_score) <= 2)).length;
  const unsatisfactory = roundsList.filter((r) => r.status === "unsatisfactory" || (r.z_score !== null && Math.abs(r.z_score) > 2)).length;

  async function handleCreateRound() {
    try {
      const created = await createRound.mutateAsync({
        programId: id,
        data: {
          round_id: form.round_id,
          sample_received_date: form.sample_received_date ? new Date(form.sample_received_date).toISOString() : null,
          result_due_date: form.result_due_date ? new Date(form.result_due_date).toISOString() : null,
          notes: form.notes || null,
        },
      });
      toast.success("PT Round created");
      setShowCreate(false);
      router.push(`/qms/pt/rounds/${created.id}`);
    } catch { toast.error("Failed to create round"); }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-gray-200 bg-white">
        <div className="flex items-start gap-4">
          <Link href="/qms/pt"><Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />PT</Button></Link>
          <div className="flex-1">
            <h1 className="text-lg font-semibold text-gray-900">{program.scheme_name}</h1>
            <p className="text-xs text-gray-500 mt-0.5">{program.provider} · {program.parameter} · Every {program.frequency_months} months</p>
          </div>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
            <Plus className="w-3.5 h-3.5 mr-1.5" />New Round
          </Button>
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6 space-y-6">
        {/* Summary cards */}
        <div className="grid grid-cols-3 gap-4 max-w-xl">
          {[
            { label: "Total Rounds", value: roundsList.length, icon: Clock, color: "text-blue-600", bg: "bg-blue-50" },
            { label: "Satisfactory", value: satisfactory, icon: CheckCircle2, color: "text-green-600", bg: "bg-green-50" },
            { label: "Unsatisfactory", value: unsatisfactory, icon: XCircle, color: "text-red-600", bg: "bg-red-50" },
          ].map(({ label, value, icon: Icon, color, bg }) => (
            <Card key={label} className="border border-gray-200">
              <CardContent className="p-4">
                <div className={`inline-flex p-1.5 rounded-lg ${bg} mb-2`}><Icon className={`w-4 h-4 ${color}`} /></div>
                <div className="text-xl font-bold text-gray-900">{value}</div>
                <div className="text-xs text-gray-500">{label}</div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* z-score trend (last 10 rounds) */}
        {roundsList.filter((r) => r.z_score !== null).length >= 2 && (
          <Card className="border border-gray-200 max-w-2xl">
            <CardContent className="p-4">
              <p className="text-sm font-semibold mb-3">z-Score Trend</p>
              <div className="flex items-end gap-2 h-24 border-b border-l border-gray-200">
                {roundsList.filter((r) => r.z_score !== null).slice(-10).map((r) => {
                  const z = r.z_score!;
                  const pct = Math.min(Math.abs(z) / 4 * 100, 100);
                  const color = Math.abs(z) <= 2 ? "bg-green-400" : Math.abs(z) <= 3 ? "bg-yellow-400" : "bg-red-500";
                  return (
                    <div key={r.id} className="flex-1 flex flex-col justify-end items-center gap-1" title={`z=${z.toFixed(2)} (${r.round_id})`}>
                      <span className="text-xs text-gray-500">{z.toFixed(1)}</span>
                      <div className={`w-full rounded-t ${color}`} style={{ height: `${Math.max(pct, 4)}%` }} />
                    </div>
                  );
                })}
              </div>
              <div className="flex justify-between mt-1 text-xs text-gray-400">
                <span>Oldest</span>
                <span className="text-gray-600">|z| ≤ 2 = Satisfactory · |z| &gt; 3 = Unsatisfactory</span>
                <span>Latest</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Rounds table */}
        <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Round ID</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Reported</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Reference</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">z-Score</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">En</th>
                <th className="text-left px-4 py-3 font-medium text-gray-600">Due Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {roundsLoading ? (
                <tr><td colSpan={7} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
              ) : roundsList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-10 text-center text-gray-400">No rounds yet. Click "New Round" to add one.</td>
                </tr>
              ) : roundsList.map((r) => (
                <tr key={r.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <Link href={`/qms/pt/rounds/${r.id}`} className="text-blue-600 hover:underline font-medium">{r.round_id}</Link>
                  </td>
                  <td className="px-4 py-3">
                    <Badge className={`text-xs ${STATUS_COLOR[r.status] ?? "bg-gray-100 text-gray-600"}`}>{r.status.replace(/_/g, " ")}</Badge>
                  </td>
                  <td className="px-4 py-3 font-mono text-gray-700">{r.reported_result ?? "—"}</td>
                  <td className="px-4 py-3 font-mono text-gray-700">{r.reference_value ?? "—"}</td>
                  <td className="px-4 py-3"><ZScoreBadge z={r.z_score} /></td>
                  <td className="px-4 py-3 font-mono text-gray-700">{r.en_number != null ? r.en_number.toFixed(3) : "—"}</td>
                  <td className="px-4 py-3 text-gray-500">{r.result_due_date ? format(new Date(r.result_due_date), "MMM d, yyyy") : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create Round Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>New PT Round — {program.scheme_name}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs">Round ID *</Label>
              <Input className="h-9 text-sm" value={form.round_id} onChange={(e) => setForm((f) => ({ ...f, round_id: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Sample Received Date</Label>
                <Input type="date" className="h-9 text-sm" value={form.sample_received_date} onChange={(e) => setForm((f) => ({ ...f, sample_received_date: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Result Due Date</Label>
                <Input type="date" className="h-9 text-sm" value={form.result_due_date} onChange={(e) => setForm((f) => ({ ...f, result_due_date: e.target.value }))} />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes</Label>
              <Input className="h-9 text-sm" placeholder="Optional notes…" value={form.notes} onChange={(e) => setForm((f) => ({ ...f, notes: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={createRound.isPending} onClick={handleCreateRound}>
              {createRound.isPending ? "Creating…" : "Create Round"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
