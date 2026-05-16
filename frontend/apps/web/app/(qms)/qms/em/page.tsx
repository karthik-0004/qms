"use client";

import { useState } from "react";
import Link from "next/link";
import { useMonitoringPoints, useCreateMonitoringPoint } from "@/lib/hooks/queries/qms";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue,
} from "@/components/ui/select";
import { Thermometer, Plus, AlertTriangle, CheckCircle2, Activity, XCircle } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";
import type { MonitoringPoint } from "@/lib/api/services/qms";

const STATUS_COLOR: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  inactive: "bg-gray-100 text-gray-500",
  alert_limit_exceeded: "bg-yellow-100 text-yellow-700",
  action_limit_exceeded: "bg-red-100 text-red-700",
};

const STATUS_ICON: Record<string, React.ReactNode> = {
  active: <CheckCircle2 className="h-4 w-4 text-green-500" />,
  inactive: <XCircle className="h-4 w-4 text-gray-400" />,
  alert_limit_exceeded: <AlertTriangle className="h-4 w-4 text-yellow-500" />,
  action_limit_exceeded: <AlertTriangle className="h-4 w-4 text-red-500" />,
};

export default function EMDashboardPage() {
  const [showCreate, setShowCreate] = useState(false);
  const { data: page, isLoading } = useMonitoringPoints({ page: 1, page_size: 100 });
  const create = useCreateMonitoringPoint();

  const points: MonitoringPoint[] = page?.items ?? [];
  const active = points.filter((p) => p.status === "active").length;
  const alerting = points.filter((p) => p.status === "alert_limit_exceeded").length;
  const excursion = points.filter((p) => p.status === "action_limit_exceeded").length;

  const [form, setForm] = useState({
    point_id: `MP-${Date.now().toString().slice(-5)}`,
    location: "",
    parameter: "temperature",
    frequency_type: "daily",
    alert_limit: "",
    action_limit: "",
    frequency_value: "1",
  });

  async function handleCreate() {
    if (!form.location.trim()) { toast.error("Location is required"); return; }
    try {
      await create.mutateAsync({
        point_id: form.point_id,
        location: form.location,
        parameter: form.parameter,
        frequency_type: form.frequency_type,
        alert_limit: form.alert_limit ? Number(form.alert_limit) : null,
        action_limit: form.action_limit ? Number(form.action_limit) : null,
        frequency_value: form.frequency_value ? Number(form.frequency_value) : null,
      });
      toast.success("Monitoring point created");
      setShowCreate(false);
    } catch { toast.error("Failed to create monitoring point"); }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Environmental Monitoring</h1>
          <p className="text-sm text-gray-500 mt-1">Monitor environmental parameters and track excursions</p>
        </div>
        <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          New Point
        </Button>
      </div>

      {/* KPI tiles */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "Total Points", value: points.length, icon: Thermometer, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Active", value: active, icon: CheckCircle2, color: "text-green-600", bg: "bg-green-50" },
          { label: "Alert Limit", value: alerting, icon: AlertTriangle, color: "text-yellow-600", bg: "bg-yellow-50" },
          { label: "Action Limit", value: excursion, icon: Activity, color: "text-red-600", bg: "bg-red-50" },
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

      {/* Points table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-4 py-3 border-b border-gray-200 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">Monitoring Points</h2>
          <Link href="/qms/em/excursions" className="text-xs text-blue-600 hover:underline">View all excursions →</Link>
        </div>
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Point ID</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Location</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Parameter</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Last Reading</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Alert / Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
            ) : points.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center">
                  <Thermometer className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No monitoring points yet</p>
                </td>
              </tr>
            ) : points.map((p) => (
              <tr key={p.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link href={`/qms/em/points/${p.id}`} className="text-blue-600 hover:underline font-medium">{p.point_id}</Link>
                </td>
                <td className="px-4 py-3 text-gray-900">{p.location}</td>
                <td className="px-4 py-3 text-gray-600 capitalize">{p.parameter}</td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-1.5">
                    {STATUS_ICON[p.status] ?? <CheckCircle2 className="h-4 w-4 text-gray-400" />}
                    <Badge className={`text-xs ${STATUS_COLOR[p.status] ?? "bg-gray-100 text-gray-600"}`}>{p.status.replace(/_/g, " ")}</Badge>
                  </div>
                </td>
                <td className="px-4 py-3 text-gray-600">
                  {p.last_reading_value != null ? (
                    <span className="font-mono">{p.last_reading_value}</span>
                  ) : "—"}
                  {p.last_reading_at && <span className="text-xs text-gray-400 ml-1">({format(new Date(p.last_reading_at), "MMM d HH:mm")})</span>}
                </td>
                <td className="px-4 py-3 text-gray-500 text-xs">
                  {p.alert_limit != null ? `A: ${p.alert_limit}` : "—"} / {p.action_limit != null ? `AL: ${p.action_limit}` : "—"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Create Dialog */}
      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>New Monitoring Point</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Point ID *</Label>
                <Input className="h-9 text-sm" value={form.point_id} onChange={(e) => setForm((f) => ({ ...f, point_id: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Parameter *</Label>
                <Select value={form.parameter} onValueChange={(v) => setForm((f) => ({ ...f, parameter: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="temperature">Temperature</SelectItem>
                    <SelectItem value="humidity">Humidity</SelectItem>
                    <SelectItem value="pressure">Pressure</SelectItem>
                    <SelectItem value="co2">CO₂</SelectItem>
                    <SelectItem value="particles">Particles</SelectItem>
                    <SelectItem value="uv">UV</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Location *</Label>
              <Input className="h-9 text-sm" placeholder="e.g. Lab Room 101, Cold Storage A" value={form.location} onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Alert Limit</Label>
                <Input type="number" className="h-9 text-sm" placeholder="e.g. 25" value={form.alert_limit} onChange={(e) => setForm((f) => ({ ...f, alert_limit: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Action Limit</Label>
                <Input type="number" className="h-9 text-sm" placeholder="e.g. 30" value={form.action_limit} onChange={(e) => setForm((f) => ({ ...f, action_limit: e.target.value }))} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Frequency Type</Label>
                <Select value={form.frequency_type} onValueChange={(v) => setForm((f) => ({ ...f, frequency_type: v }))}>
                  <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="hourly">Hourly</SelectItem>
                    <SelectItem value="daily">Daily</SelectItem>
                    <SelectItem value="weekly">Weekly</SelectItem>
                    <SelectItem value="continuous">Continuous</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Frequency Value</Label>
                <Input type="number" className="h-9 text-sm" placeholder="1" value={form.frequency_value} onChange={(e) => setForm((f) => ({ ...f, frequency_value: e.target.value }))} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={create.isPending} onClick={handleCreate}>
              {create.isPending ? "Creating…" : "Create Point"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
