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
  const summaryMetrics = dashData?.summary_metrics ?? {};

  const KPI_CARDS = [
    { title: "Total Users", value: kpis?.total_users ?? 0, icon: Briefcase, color: "text-blue-600" },
    { title: "Work Orders (MTD)", value: kpis?.workorders_this_month ?? 0, icon: ClipboardList, color: "text-amber-600" },
    { title: "Certs Issued YTD", value: kpis?.certificates_issued_ytd ?? 0, icon: DollarSign, color: "text-green-600" },
    { title: "Active Users (30d)", value: kpis?.active_users_30d ?? 0, icon: Users, color: "text-purple-600" },
  ];

  const buildWorkOrderStatusRows = () => {
    const pending = (summaryMetrics.work_orders_pending as number) ?? 0;
    const assigned = (summaryMetrics.work_orders_assigned as number) ?? 0;
    const inProgress = (summaryMetrics.work_orders_in_progress as number) ?? 0;
    const onHold = (summaryMetrics.work_orders_on_hold as number) ?? 0;
    const completed = (summaryMetrics.work_orders_completed as number) ?? 0;
    const total = pending + assigned + inProgress + onHold + completed;
    if (total === 0) return [];
    return [
      { label: "Pending", count: pending, pct: (pending / total) * 100, color: "bg-slate-400" },
      { label: "Assigned", count: assigned, pct: (assigned / total) * 100, color: "bg-blue-400" },
      { label: "In Progress", count: inProgress, pct: (inProgress / total) * 100, color: "bg-amber-400" },
      { label: "On Hold", count: onHold, pct: (onHold / total) * 100, color: "bg-slate-400" },
      { label: "Completed", count: completed, pct: (completed / total) * 100, color: "bg-green-500" },
    ];
  };

  const buildInvoiceAgingRows = () => {
    const current = (summaryMetrics.invoices_current as number) ?? 0;
    const days1_30 = (summaryMetrics.invoices_1_30_days as number) ?? 0;
    const days31_60 = (summaryMetrics.invoices_31_60_days as number) ?? 0;
    const days61Plus = (summaryMetrics.invoices_61_plus_days as number) ?? 0;
    const total = current + days1_30 + days31_60 + days61Plus;
    if (total === 0) return [];
    return [
      { label: "Current", count: current, pct: (current / total) * 100, color: "bg-green-500" },
      { label: "1–30 days", count: days1_30, pct: (days1_30 / total) * 100, color: "bg-amber-400" },
      { label: "31–60 days", count: days31_60, pct: (days31_60 / total) * 100, color: "bg-orange-500" },
      { label: "60+ days", count: days61Plus, pct: (days61Plus / total) * 100, color: "bg-red-500" },
    ];
  };

  const workOrderRows = buildWorkOrderStatusRows();
  const invoiceRows = buildInvoiceAgingRows();

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
            {dashLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            ) : workOrderRows.length === 0 ? (
              <p className="text-sm text-muted-foreground">No work order data available</p>
            ) : (
              <div className="space-y-3">
                {workOrderRows.map((row) => (
                  <div key={row.label} className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground w-28">{row.label}</span>
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div className={`h-full ${row.color} rounded-full`} style={{ width: `${row.pct}%` }} />
                    </div>
                    <span className="text-sm font-medium w-8 text-right">{row.count}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><CardTitle className="text-base">Invoice Aging</CardTitle></CardHeader>
          <CardContent>
            {dashLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
                <Skeleton className="h-8 w-full" />
              </div>
            ) : invoiceRows.length === 0 ? (
              <p className="text-sm text-muted-foreground">No invoice aging data available</p>
            ) : (
              <div className="space-y-3">
                {invoiceRows.map((row) => (
                  <div key={row.label} className="flex items-center gap-3">
                    <span className="text-sm text-muted-foreground w-28">{row.label}</span>
                    <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                      <div className={`h-full ${row.color} rounded-full`} style={{ width: `${row.pct}%` }} />
                    </div>
                    <span className="text-sm font-medium w-16 text-right">{row.count}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
