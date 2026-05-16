"use client";

import Link from "next/link";
import { useAudits } from "@/lib/hooks/queries/qms";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  ClipboardCheck,
  Plus,
  Calendar,
  AlertTriangle,
  CheckCircle2,
  Clock,
  List,
  BookOpen,
} from "lucide-react";
import { format } from "date-fns";

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

export default function AuditDashboardPage() {
  const { data: auditsPage, isLoading } = useAudits({ page: 1, page_size: 100 });
  const audits = auditsPage?.items ?? [];

  const totalAudits = audits.length;
  const planned = audits.filter((a) => a.status === "planned").length;
  const inProgress = audits.filter((a) => a.status === "in_progress").length;
  const completed = audits.filter((a) => a.status === "completed").length;
  const totalFindings = audits.reduce((s, a) => s + a.finding_count, 0);
  const majorNCs = audits.reduce((s, a) => s + a.major_nc_count, 0);

  const recent = audits
    .slice()
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5);

  const upcoming = audits
    .filter((a) => a.status === "planned" && a.scheduled_start)
    .sort((a, b) => new Date(a.scheduled_start!).getTime() - new Date(b.scheduled_start!).getTime())
    .slice(0, 5);

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Audit Management</h1>
          <p className="text-sm text-gray-500 mt-1">Plan, schedule, and track internal and external audits</p>
        </div>
        <div className="flex gap-2">
          <Link href="/qms/audit/list">
            <Button variant="outline" size="sm">
              <List className="w-4 h-4 mr-2" />
              All Audits
            </Button>
          </Link>
          <Link href="/qms/audit/checklists">
            <Button variant="outline" size="sm">
              <BookOpen className="w-4 h-4 mr-2" />
              Checklists
            </Button>
          </Link>
          <Link href="/qms/audit/list?new=1">
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
              <Plus className="w-4 h-4 mr-2" />
              New Audit
            </Button>
          </Link>
        </div>
      </div>

      {/* KPI Tiles */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: "Total Audits", value: totalAudits, icon: ClipboardCheck, color: "text-blue-600", bg: "bg-blue-50" },
          { label: "Planned", value: planned, icon: Calendar, color: "text-purple-600", bg: "bg-purple-50" },
          { label: "In Progress", value: inProgress, icon: Clock, color: "text-yellow-600", bg: "bg-yellow-50" },
          { label: "Completed", value: completed, icon: CheckCircle2, color: "text-green-600", bg: "bg-green-50" },
          { label: "Total Findings", value: totalFindings, icon: AlertTriangle, color: "text-orange-600", bg: "bg-orange-50" },
          { label: "Major NCs", value: majorNCs, icon: AlertTriangle, color: "text-red-600", bg: "bg-red-50" },
        ].map(({ label, value, icon: Icon, color, bg }) => (
          <Card key={label} className="border border-gray-200">
            <CardContent className="p-4">
              <div className={`inline-flex p-2 rounded-lg ${bg} mb-3`}>
                <Icon className={`w-5 h-5 ${color}`} />
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {isLoading ? "—" : value}
              </div>
              <div className="text-xs text-gray-500 mt-1">{label}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Audits */}
        <Card className="border border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-gray-700">Recent Audits</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="px-6 py-8 text-center text-gray-400 text-sm">Loading…</div>
            ) : recent.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-400 text-sm">No audits yet</div>
            ) : (
              <div className="divide-y divide-gray-100">
                {recent.map((audit) => (
                  <Link key={audit.id} href={`/qms/audit/${audit.id}`} className="block px-6 py-3 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{audit.title}</p>
                        <p className="text-xs text-gray-500">{audit.audit_number}</p>
                      </div>
                      <div className="flex items-center gap-2 ml-4 shrink-0">
                        <Badge className={`text-xs ${TYPE_COLOR[audit.audit_type] ?? "bg-gray-100 text-gray-600"}`}>
                          {audit.audit_type}
                        </Badge>
                        <Badge className={`text-xs ${STATUS_COLOR[audit.status] ?? "bg-gray-100 text-gray-600"}`}>
                          {audit.status.replace("_", " ")}
                        </Badge>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
            <div className="px-6 py-3 border-t border-gray-100">
              <Link href="/qms/audit/list" className="text-xs text-blue-600 hover:underline">
                View all audits →
              </Link>
            </div>
          </CardContent>
        </Card>

        {/* Upcoming Audits */}
        <Card className="border border-gray-200">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-semibold text-gray-700">Upcoming Scheduled Audits</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {isLoading ? (
              <div className="px-6 py-8 text-center text-gray-400 text-sm">Loading…</div>
            ) : upcoming.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-400 text-sm">No upcoming audits scheduled</div>
            ) : (
              <div className="divide-y divide-gray-100">
                {upcoming.map((audit) => (
                  <Link key={audit.id} href={`/qms/audit/${audit.id}`} className="block px-6 py-3 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{audit.title}</p>
                        <p className="text-xs text-gray-500">
                          {audit.scheduled_start
                            ? format(new Date(audit.scheduled_start), "MMM d, yyyy")
                            : "—"}
                        </p>
                      </div>
                      <Badge className={`text-xs ${TYPE_COLOR[audit.audit_type] ?? "bg-gray-100 text-gray-600"}`}>
                        {audit.audit_type}
                      </Badge>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
