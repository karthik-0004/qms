"use client";

import { BarChart3, DollarSign, Briefcase, ClipboardList, Users } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePlatformKPIs, useDashboard } from "@/lib/hooks/queries/analytics";

export default function CCVAnalyticsPage() {
  const { data: kpiData, isLoading: kpiLoading } = usePlatformKPIs();
  const { data: dashData, isLoading: dashLoading } = useDashboard("ccv_overview");
  const loading = kpiLoading || dashLoading;
  const kpis = kpiData?.kpis;

  const KPI_CARDS = [
    { title: "Total Users", value: kpis?.total_users ?? 0, icon: Briefcase, color: "text-blue-600" },
    { title: "Work Orders (MTD)", value: kpis?.workorders_this_month ?? 0, icon: ClipboardList, color: "text-amber-600" },
    { title: "Certs Issued YTD", value: kpis?.certificates_issued_ytd ?? 0, icon: DollarSign, color: "text-green-600" },
    { title: "Active Users (30d)", value: kpis?.active_users_30d ?? 0, icon: Users, color: "text-purple-600" },
  ];

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-6 w-6" />
          CCV Analytics
        </h1>
        <p className="text-muted-foreground text-sm mt-1">Revenue, operations, and field service metrics</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {KPI_CARDS.map((kpi) => (
          <Card key={kpi.title}>
            <CardContent className="pt-6">
              {loading ? (
                <div className="space-y-2">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-8 w-16" />
                  <Skeleton className="h-3 w-20" />
                </div>
              ) : (
                <>
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-muted-foreground">{kpi.title}</p>
                    <kpi.icon className={`h-5 w-5 ${kpi.color}`} />
                  </div>
                  <p className="text-3xl font-bold mt-2">{kpi.value}</p>
                </>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader><CardTitle className="text-base">Work Order Status</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { label: "Scheduled", count: 8, pct: 35, color: "bg-blue-400" },
                { label: "In Progress", count: 10, pct: 43, color: "bg-amber-400" },
                { label: "Completed", count: 156, pct: 85, color: "bg-green-500" },
                { label: "On Hold", count: 5, pct: 22, color: "bg-slate-400" },
              ].map((row) => (
                <div key={row.label} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-28">{row.label}</span>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div className={`h-full ${row.color} rounded-full`} style={{ width: `${row.pct}%` }} />
                  </div>
                  <span className="text-sm font-medium w-8 text-right">{row.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Invoice Aging</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { label: "Current", count: "$45,200", pct: 55, color: "bg-green-500" },
                { label: "1–30 days", count: "$18,400", pct: 22, color: "bg-amber-400" },
                { label: "31–60 days", count: "$12,100", pct: 15, color: "bg-orange-500" },
                { label: "60+ days", count: "$6,800", pct: 8, color: "bg-red-500" },
              ].map((row) => (
                <div key={row.label} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-28">{row.label}</span>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div className={`h-full ${row.color} rounded-full`} style={{ width: `${row.pct}%` }} />
                  </div>
                  <span className="text-sm font-medium w-16 text-right">{row.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
