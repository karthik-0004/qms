"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useRisk, useUpdateRisk, useDeleteRisk } from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
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
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { ChevronLeft, Trash2 } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

function riskColor(score: number) {
  if (score >= 15) return { bg: "bg-red-500", text: "text-red-700", label: "Critical" };
  if (score >= 10) return { bg: "bg-orange-400", text: "text-orange-700", label: "High" };
  if (score >= 5) return { bg: "bg-yellow-400", text: "text-yellow-700", label: "Medium" };
  return { bg: "bg-green-400", text: "text-green-700", label: "Low" };
}

const STATUS_COLOR: Record<string, string> = {
  identified: "bg-blue-100 text-blue-700",
  assessed: "bg-purple-100 text-purple-700",
  mitigating: "bg-yellow-100 text-yellow-700",
  mitigated: "bg-green-100 text-green-700",
  accepted: "bg-gray-100 text-gray-600",
  closed: "bg-gray-100 text-gray-500",
};

export default function RiskDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [showDelete, setShowDelete] = useState(false);

  const { data: risk, isLoading } = useRisk(id);
  const updateRisk = useUpdateRisk();
  const deleteRisk = useDeleteRisk();

  if (isLoading) return <div className="p-6 flex items-center justify-center h-64"><div className="text-gray-400 text-sm">Loading…</div></div>;
  if (!risk) return <div className="p-6 text-red-500">Risk not found.</div>;

  async function patch(data: Record<string, unknown>) {
    try { await updateRisk.mutateAsync({ id, data }); }
    catch { toast.error("Failed to save"); }
  }

  async function handleDelete() {
    try {
      await deleteRisk.mutateAsync(id);
      toast.success("Risk deleted");
      router.push("/qms/risk");
    } catch { toast.error("Failed to delete"); }
  }

  const { bg, label } = riskColor(risk.risk_score);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Link href="/qms/risk">
          <Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />Risks</Button>
        </Link>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-lg font-semibold text-gray-900">{risk.risk_id}</h1>
            <Badge className={`text-xs ${STATUS_COLOR[risk.status] ?? "bg-gray-100 text-gray-600"}`}>{risk.status}</Badge>
            <div className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-white text-xs font-semibold ${bg}`}>
              Score: {risk.risk_score} — {label}
            </div>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">Category: {risk.category} · Created {format(new Date(risk.created_at), "PPP")}</p>
        </div>
        <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50" onClick={() => setShowDelete(true)}>
          <Trash2 className="w-3.5 h-3.5" />
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
        {/* Risk Details */}
        <Card className="border border-gray-200">
          <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Risk Details</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <Label className="text-xs text-gray-500">Description</Label>
              <Textarea rows={4} className="text-sm resize-none" defaultValue={risk.description} onBlur={(e) => patch({ description: e.target.value })} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs text-gray-500">Category</Label>
              <Select value={risk.category} onValueChange={(v) => patch({ category: v })}>
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
            <div className="space-y-1">
              <Label className="text-xs text-gray-500">Status</Label>
              <Select value={risk.status} onValueChange={(v) => patch({ status: v })}>
                <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="identified">Identified</SelectItem>
                  <SelectItem value="assessed">Assessed</SelectItem>
                  <SelectItem value="mitigating">Mitigating</SelectItem>
                  <SelectItem value="mitigated">Mitigated</SelectItem>
                  <SelectItem value="accepted">Accepted</SelectItem>
                  <SelectItem value="closed">Closed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Risk Scoring */}
        <Card className="border border-gray-200">
          <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Risk Assessment</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs text-gray-500">Severity (1–5)</Label>
                <Select value={String(risk.severity)} onValueChange={(v) => patch({ severity: Number(v) })}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>{[1, 2, 3, 4, 5].map((n) => <SelectItem key={n} value={String(n)}>{n}</SelectItem>)}</SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs text-gray-500">Likelihood (1–5)</Label>
                <Select value={String(risk.likelihood)} onValueChange={(v) => patch({ likelihood: Number(v) })}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>{[1, 2, 3, 4, 5].map((n) => <SelectItem key={n} value={String(n)}>{n}</SelectItem>)}</SelectContent>
                </Select>
              </div>
            </div>
            <div className={`rounded p-4 text-center ${bg}`}>
              <div className="text-4xl font-bold text-white">{risk.risk_score}</div>
              <div className="text-white text-sm font-medium mt-1">{label} Risk</div>
              <div className="text-white/80 text-xs mt-0.5">S{risk.severity} × L{risk.likelihood}</div>
            </div>
          </CardContent>
        </Card>

        {/* Mitigation Plan */}
        <Card className="border border-gray-200 lg:col-span-2">
          <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Mitigation Plan</CardTitle></CardHeader>
          <CardContent>
            <Textarea rows={5} className="text-sm resize-none" placeholder="Describe the mitigation plan, controls, and actions to reduce this risk…" defaultValue={risk.mitigation_plan ?? ""} onBlur={(e) => patch({ mitigation_plan: e.target.value || null })} />
          </CardContent>
        </Card>
      </div>

      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Risk?</AlertDialogTitle>
            <AlertDialogDescription>This will permanently delete risk <strong>{risk.risk_id}</strong>.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction className="bg-red-600 hover:bg-red-700" onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
