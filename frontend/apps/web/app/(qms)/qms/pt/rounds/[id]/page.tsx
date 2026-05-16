"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { usePTRound, usePTProgram, useUpdatePTRound, useCalculatePTScores } from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { ChevronLeft, CheckCircle2, XCircle, Calculator, AlertTriangle } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

const STATUS_COLOR: Record<string, string> = {
  pending: "bg-gray-100 text-gray-600",
  sample_received: "bg-blue-100 text-blue-700",
  result_submitted: "bg-yellow-100 text-yellow-700",
  scored: "bg-purple-100 text-purple-700",
  satisfactory: "bg-green-100 text-green-700",
  unsatisfactory: "bg-red-100 text-red-700",
};

export default function PTRoundDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();

  const { data: round, isLoading } = usePTRound(id);
  const { data: program } = usePTProgram(round?.program_id ?? "");
  const updateRound = useUpdatePTRound();
  const calculateScores = useCalculatePTScores();

  const [reportedResult, setReportedResult] = useState("");
  const [referenceValue, setReferenceValue] = useState("");
  const [notes, setNotes] = useState("");
  const [scoreResult, setScoreResult] = useState<{
    z_score: number; en_number: number; z_score_pass: boolean; en_number_pass: boolean;
  } | null>(null);

  if (isLoading) return <div className="p-6 flex items-center justify-center h-64 text-gray-400 text-sm">Loading…</div>;
  if (!round) return <div className="p-6 text-red-500">Round not found.</div>;

  const zScore = round.z_score;
  const zPass = zScore !== null && Math.abs(zScore) <= 2;
  const zWarn = zScore !== null && Math.abs(zScore) > 2 && Math.abs(zScore) <= 3;
  const zFail = zScore !== null && Math.abs(zScore) > 3;

  async function handleSubmitResult() {
    if (!reportedResult) { toast.error("Reported result is required"); return; }
    try {
      await updateRound.mutateAsync({
        id,
        data: { reported_result: Number(reportedResult), status: "result_submitted", notes: notes || undefined },
      });
      toast.success("Result submitted");
    } catch { toast.error("Failed to submit result"); }
  }

  async function handleRevealAndScore() {
    if (!referenceValue) { toast.error("Reference value is required"); return; }
    try {
      await updateRound.mutateAsync({ id, data: { reference_value: Number(referenceValue) } });
      const result = await calculateScores.mutateAsync(id);
      setScoreResult(result);
      toast.success("Scores calculated!");
    } catch { toast.error("Failed to calculate scores"); }
  }

  const canSubmitResult = round.status === "pending" || round.status === "sample_received";
  const canReveal = round.status === "result_submitted";
  const isScored = round.status === "scored" || round.status === "satisfactory" || round.status === "unsatisfactory";

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Link href={round.program_id ? `/qms/pt/programs/${round.program_id}` : "/qms/pt"}>
          <Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />Program</Button>
        </Link>
        <div className="flex-1">
          <div className="flex items-center gap-3">
            <h1 className="text-lg font-semibold text-gray-900">Round: {round.round_id}</h1>
            <Badge className={`text-xs ${STATUS_COLOR[round.status] ?? "bg-gray-100 text-gray-600"}`}>{round.status.replace(/_/g, " ")}</Badge>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            {program ? `${program.scheme_name} — ${program.parameter}` : "Loading program…"}
            {round.result_due_date && ` · Due ${format(new Date(round.result_due_date), "MMM d, yyyy")}`}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
        {/* Round Details */}
        <Card className="border border-gray-200">
          <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Round Details</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            {[
              ["Round ID", round.round_id],
              ["Status", <Badge key="s" className={`text-xs ${STATUS_COLOR[round.status] ?? ""}`}>{round.status.replace(/_/g, " ")}</Badge>],
              ["Sample Received", round.sample_received_date ? format(new Date(round.sample_received_date), "PPP") : "—"],
              ["Result Due", round.result_due_date ? format(new Date(round.result_due_date), "PPP") : "—"],
              ["Reported Result", round.reported_result != null ? <span key="rr" className="font-mono font-semibold">{round.reported_result}</span> : "—"],
              ["Reference Value", round.reference_value != null ? <span key="rv" className="font-mono font-semibold">{round.reference_value}</span> : "Not revealed"],
              ["CAPA Linked", round.capa_id ? <Link key="c" href={`/qms/capa/${round.capa_id}`} className="text-blue-600 hover:underline">{round.capa_id.slice(0, 8)}…</Link> : "—"],
            ].map(([k, v]) => (
              <div key={String(k)} className="flex items-center gap-2 py-1.5 border-b border-gray-100 last:border-0">
                <span className="text-xs text-gray-500 w-36 shrink-0">{k}</span>
                <span className="text-sm">{v as React.ReactNode}</span>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Scoring Panel */}
        <Card className="border border-gray-200">
          <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Scoring</CardTitle></CardHeader>
          <CardContent className="space-y-4">
            {isScored || round.z_score !== null ? (
              <>
                {/* z-score display */}
                <div className={`rounded-lg p-5 text-center ${zFail ? "bg-red-50 border border-red-200" : zWarn ? "bg-yellow-50 border border-yellow-200" : "bg-green-50 border border-green-200"}`}>
                  <div className="text-4xl font-bold mb-1" style={{ color: zFail ? "#dc2626" : zWarn ? "#d97706" : "#16a34a" }}>
                    z = {round.z_score?.toFixed(3) ?? "—"}
                  </div>
                  <div className={`font-semibold text-sm ${zFail ? "text-red-700" : zWarn ? "text-yellow-700" : "text-green-700"}`}>
                    {zFail ? "Unsatisfactory (|z| > 3)" : zWarn ? "Questionable (2 < |z| ≤ 3)" : "Satisfactory (|z| ≤ 2)"}
                  </div>
                  {round.en_number !== null && (
                    <div className="mt-2 text-xs text-gray-500">En = {round.en_number.toFixed(3)} {round.en_number <= 1 ? "✓ Pass" : "✗ Fail"}</div>
                  )}
                </div>
                <div className="grid grid-cols-2 gap-3 text-sm">
                  <div className="flex items-center gap-2 rounded bg-gray-50 p-2">
                    {zFail ? <XCircle className="text-red-500 h-4 w-4" /> : <CheckCircle2 className="text-green-500 h-4 w-4" />}
                    <span>z-Score: {zFail ? "Fail" : "Pass"}</span>
                  </div>
                  {round.en_number !== null && (
                    <div className="flex items-center gap-2 rounded bg-gray-50 p-2">
                      {round.en_number > 1 ? <XCircle className="text-red-500 h-4 w-4" /> : <CheckCircle2 className="text-green-500 h-4 w-4" />}
                      <span>En: {round.en_number > 1 ? "Fail" : "Pass"}</span>
                    </div>
                  )}
                </div>
                {zFail && !round.capa_id && (
                  <div className="flex items-start gap-2 rounded bg-red-50 border border-red-200 p-3">
                    <AlertTriangle className="text-red-500 h-4 w-4 mt-0.5 shrink-0" />
                    <p className="text-xs text-red-700">Unsatisfactory result — a CAPA should be initiated. Contact the PT coordinator.</p>
                  </div>
                )}
              </>
            ) : canSubmitResult ? (
              <div className="space-y-3">
                <p className="text-xs text-gray-500">Submit your result before the reference value is revealed.</p>
                <div className="space-y-1">
                  <Label className="text-xs">Reported Result *</Label>
                  <Input type="number" step="any" className="h-9 text-sm" placeholder="Enter your result" value={reportedResult} onChange={(e) => setReportedResult(e.target.value)} />
                </div>
                <div className="space-y-1">
                  <Label className="text-xs">Notes</Label>
                  <Input className="h-9 text-sm" placeholder="Optional notes…" value={notes} onChange={(e) => setNotes(e.target.value)} />
                </div>
                <Button size="sm" className="w-full bg-blue-600 hover:bg-blue-700 text-white" disabled={updateRound.isPending} onClick={handleSubmitResult}>
                  {updateRound.isPending ? "Submitting…" : "Submit Result (blind)"}
                </Button>
              </div>
            ) : canReveal ? (
              <div className="space-y-3">
                <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded p-2">Your result has been submitted. Now enter the reference value to calculate your z-score.</p>
                <div className="space-y-1">
                  <Label className="text-xs">Reference Value (from PT provider) *</Label>
                  <Input type="number" step="any" className="h-9 text-sm" placeholder="Enter reference value" value={referenceValue} onChange={(e) => setReferenceValue(e.target.value)} />
                </div>
                <Button size="sm" className="w-full bg-purple-600 hover:bg-purple-700 text-white" disabled={calculateScores.isPending} onClick={handleRevealAndScore}>
                  <Calculator className="w-4 h-4 mr-2" />
                  {calculateScores.isPending ? "Calculating…" : "Reveal & Calculate Score"}
                </Button>
              </div>
            ) : (
              <p className="text-sm text-gray-400 text-center py-4">Round not yet in progress.</p>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
