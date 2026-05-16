"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  useMonitoringPoint, useMonitoringReadings, useMonitoringExcursions, useAddMonitoringReading,
} from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import { ChevronLeft, Plus, AlertTriangle, CheckCircle2, Activity } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

type Tab = "info" | "chart" | "excursions";

const STATUS_COLOR: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  inactive: "bg-gray-100 text-gray-500",
  alert_limit_exceeded: "bg-yellow-100 text-yellow-700",
  action_limit_exceeded: "bg-red-100 text-red-700",
};

const READING_STATUS_COLOR: Record<string, string> = {
  within_limits: "bg-green-100 text-green-700",
  alert_limit_exceeded: "bg-yellow-100 text-yellow-700",
  action_limit_exceeded: "bg-red-100 text-red-700",
};

export default function MonitoringPointDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState<Tab>("info");
  const [showAddReading, setShowAddReading] = useState(false);
  const [readingForm, setReadingForm] = useState({ value: "", recorded_at: new Date().toISOString().slice(0, 16), notes: "" });

  const { data: point, isLoading } = useMonitoringPoint(id);
  const { data: readings } = useMonitoringReadings(id);
  const { data: excursions } = useMonitoringExcursions(id);
  const addReading = useAddMonitoringReading();

  if (isLoading) return <div className="p-6 flex items-center justify-center h-64 text-gray-400 text-sm">Loading…</div>;
  if (!point) return <div className="p-6 text-red-500">Monitoring point not found.</div>;

  async function handleAddReading() {
    if (!readingForm.value) { toast.error("Value is required"); return; }
    try {
      await addReading.mutateAsync({
        pointId: id,
        data: {
          value: Number(readingForm.value),
          recorded_at: new Date(readingForm.recorded_at).toISOString(),
          notes: readingForm.notes || undefined,
        },
      });
      toast.success("Reading recorded");
      setShowAddReading(false);
      setReadingForm({ value: "", recorded_at: new Date().toISOString().slice(0, 16), notes: "" });
    } catch { toast.error("Failed to record reading"); }
  }

  const readingsList = readings ?? [];
  const excursionsList = excursions ?? [];

  // Simple sparkline data for the chart tab
  const last20 = readingsList.slice(-20);

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-gray-200 bg-white">
        <div className="flex items-start gap-4">
          <Link href="/qms/em">
            <Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />EM</Button>
          </Link>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-lg font-semibold text-gray-900">{point.point_id}</h1>
              <Badge className={`text-xs ${STATUS_COLOR[point.status] ?? "bg-gray-100 text-gray-600"}`}>{point.status.replace(/_/g, " ")}</Badge>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{point.location} · {point.parameter}</p>
          </div>
          <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowAddReading(true)}>
            <Plus className="w-3.5 h-3.5 mr-1.5" />
            Record Reading
          </Button>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white px-6">
        <div className="flex">
          {([["info", "Information"], ["chart", "Readings Chart"], ["excursions", "Excursions"]] as [Tab, string][]).map(([key, label]) => (
            <button
              key={key}
              onClick={() => setActiveTab(key)}
              className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === key ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
            >
              {label}
              {key === "excursions" && excursionsList.length > 0 && (
                <span className="ml-1.5 rounded-full bg-red-100 px-1.5 py-0.5 text-xs text-red-700">{excursionsList.length}</span>
              )}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-auto p-6">
        {activeTab === "info" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Point Details</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                {[
                  ["Point ID", point.point_id],
                  ["Location", point.location],
                  ["Parameter", point.parameter],
                  ["Frequency", `${point.frequency_value ?? 1} × ${point.frequency_type}`],
                  ["Alert Limit", point.alert_limit != null ? String(point.alert_limit) : "—"],
                  ["Action Limit", point.action_limit != null ? String(point.action_limit) : "—"],
                  ["Last Reading", point.last_reading_value != null ? `${point.last_reading_value}` : "—"],
                  ["Last Reading At", point.last_reading_at ? format(new Date(point.last_reading_at), "PPpp") : "—"],
                ].map(([k, v]) => (
                  <div key={k} className="flex items-center gap-2 py-1.5 border-b border-gray-100 last:border-0">
                    <span className="text-xs text-gray-500 w-36 shrink-0">{k}</span>
                    <span className="text-sm">{v}</span>
                  </div>
                ))}
              </CardContent>
            </Card>

            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Recent Readings ({readingsList.length})</CardTitle></CardHeader>
              <CardContent className="p-0">
                <div className="max-h-80 overflow-y-auto">
                  {readingsList.length === 0 ? (
                    <p className="p-4 text-sm text-gray-400 text-center">No readings yet</p>
                  ) : (
                    <table className="w-full text-xs">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Value</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Status</th>
                          <th className="px-3 py-2 text-left font-medium text-gray-500">Recorded At</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-100">
                        {readingsList.slice().reverse().slice(0, 20).map((r) => (
                          <tr key={r.id}>
                            <td className="px-3 py-2 font-mono font-medium">{r.value}</td>
                            <td className="px-3 py-2">
                              <Badge className={`text-xs ${READING_STATUS_COLOR[r.status] ?? "bg-gray-100 text-gray-600"}`}>{r.status.replace(/_/g, " ")}</Badge>
                            </td>
                            <td className="px-3 py-2 text-gray-500">{format(new Date(r.recorded_at), "MMM d HH:mm")}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "chart" && (
          <div className="max-w-4xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-semibold">Readings Over Time — {point.parameter}</CardTitle>
              </CardHeader>
              <CardContent>
                {last20.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <Activity className="w-8 h-8 text-gray-300 mb-2" />
                    <p className="text-sm text-gray-400">No readings to display</p>
                    <Button size="sm" variant="outline" className="mt-3" onClick={() => setShowAddReading(true)}>Record First Reading</Button>
                  </div>
                ) : (
                  <div>
                    {/* Simple bar chart visualization */}
                    <div className="relative h-48 flex items-end gap-1 border-b border-l border-gray-200 pl-8 pb-1">
                      {last20.map((r, i) => {
                        const max = Math.max(...last20.map((x) => x.value), point.action_limit ?? 0, point.alert_limit ?? 0);
                        const pct = max > 0 ? (r.value / max) * 100 : 50;
                        const isAction = point.action_limit != null && r.value > point.action_limit;
                        const isAlert = point.alert_limit != null && r.value > point.alert_limit;
                        return (
                          <div key={r.id} className="relative flex-1 flex flex-col justify-end group" title={`${r.value} @ ${format(new Date(r.recorded_at), "MMM d HH:mm")}`}>
                            <div
                              className={`rounded-t transition-all ${isAction ? "bg-red-400" : isAlert ? "bg-yellow-400" : "bg-blue-400"}`}
                              style={{ height: `${Math.max(pct, 2)}%` }}
                            />
                          </div>
                        );
                      })}
                      {/* Limit lines */}
                      {point.alert_limit != null && (() => {
                        const max = Math.max(...last20.map((x) => x.value), point.action_limit ?? 0, point.alert_limit ?? 0);
                        const pct = max > 0 ? (point.alert_limit / max) * 100 : 50;
                        return (
                          <div className="absolute left-8 right-0 border-t border-dashed border-yellow-400" style={{ bottom: `${pct}%` }}>
                            <span className="absolute right-0 text-xs text-yellow-600 bg-white px-1 -top-3">Alert: {point.alert_limit}</span>
                          </div>
                        );
                      })()}
                      {point.action_limit != null && (() => {
                        const max = Math.max(...last20.map((x) => x.value), point.action_limit ?? 0, point.alert_limit ?? 0);
                        const pct = max > 0 ? (point.action_limit / max) * 100 : 70;
                        return (
                          <div className="absolute left-8 right-0 border-t border-dashed border-red-400" style={{ bottom: `${pct}%` }}>
                            <span className="absolute right-0 text-xs text-red-600 bg-white px-1 -top-3">Action: {point.action_limit}</span>
                          </div>
                        );
                      })()}
                    </div>
                    <div className="mt-2 flex justify-between text-xs text-gray-400">
                      <span>{last20[0] ? format(new Date(last20[0].recorded_at), "MMM d") : ""}</span>
                      <span className="text-gray-600 font-medium">Last {last20.length} readings</span>
                      <span>{last20[last20.length - 1] ? format(new Date(last20[last20.length - 1].recorded_at), "MMM d") : ""}</span>
                    </div>
                    <div className="mt-3 flex items-center gap-4 text-xs text-gray-500">
                      <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-blue-400 inline-block" />Normal</span>
                      <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-yellow-400 inline-block" />Alert</span>
                      <span className="flex items-center gap-1"><span className="w-3 h-3 rounded bg-red-400 inline-block" />Action</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "excursions" && (
          <div className="max-w-3xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Excursions ({excursionsList.length})</CardTitle></CardHeader>
              <CardContent className="p-0">
                {excursionsList.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12 text-center">
                    <CheckCircle2 className="w-8 h-8 text-green-400 mb-2" />
                    <p className="text-sm text-gray-400">No excursions recorded — all clear!</p>
                  </div>
                ) : (
                  <table className="w-full text-sm">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-4 py-3 text-left font-medium text-gray-600">Value</th>
                        <th className="px-4 py-3 text-left font-medium text-gray-600">Type</th>
                        <th className="px-4 py-3 text-left font-medium text-gray-600">Recorded At</th>
                        <th className="px-4 py-3 text-left font-medium text-gray-600">Notes</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {excursionsList.map((ex) => (
                        <tr key={ex.id}>
                          <td className="px-4 py-3 font-mono font-semibold text-red-700">{ex.value}</td>
                          <td className="px-4 py-3">
                            <Badge className={`text-xs ${READING_STATUS_COLOR[ex.status] ?? ""}`}>{ex.status.replace(/_/g, " ")}</Badge>
                          </td>
                          <td className="px-4 py-3 text-gray-600">{format(new Date(ex.recorded_at), "PPp")}</td>
                          <td className="px-4 py-3 text-gray-500">{ex.notes ?? "—"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Add Reading Dialog */}
      <Dialog open={showAddReading} onOpenChange={setShowAddReading}>
        <DialogContent className="max-w-sm">
          <DialogHeader><DialogTitle>Record Reading — {point.point_id}</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="space-y-1">
              <Label className="text-xs">Value ({point.parameter}) *</Label>
              <Input type="number" step="0.01" className="h-9 text-sm" placeholder="e.g. 22.5" value={readingForm.value} onChange={(e) => setReadingForm((f) => ({ ...f, value: e.target.value }))} autoFocus />
              {point.alert_limit != null && <p className="text-xs text-yellow-600">Alert limit: {point.alert_limit}</p>}
              {point.action_limit != null && <p className="text-xs text-red-600">Action limit: {point.action_limit}</p>}
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Recorded At</Label>
              <Input type="datetime-local" className="h-9 text-sm" value={readingForm.recorded_at} onChange={(e) => setReadingForm((f) => ({ ...f, recorded_at: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Notes</Label>
              <Textarea className="text-sm resize-none" rows={2} placeholder="Optional notes…" value={readingForm.notes} onChange={(e) => setReadingForm((f) => ({ ...f, notes: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowAddReading(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={addReading.isPending} onClick={handleAddReading}>
              {addReading.isPending ? "Saving…" : "Save Reading"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
