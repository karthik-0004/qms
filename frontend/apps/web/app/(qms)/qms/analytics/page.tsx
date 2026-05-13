"use client";

import { useRouter } from "next/navigation";
import { BarChart3, TrendingUp, AlertTriangle, CheckCircle2, Clock, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePlatformKPIs } from "@/lib/hooks/queries/analytics";
import { useDashboard } from "@/lib/hooks/queries/analytics";

type ChartRow = { label: string; count: number; pct: number; color: string };

function buildDocStatusRows(metrics: Record<string, unknown>): ChartRow[] {
  const draft = Number(metrics.documents_draft ?? 0);
  const review = Number(metrics.documents_pending_review ?? 0);
  const approved = Number(metrics.documents_approved ?? 0);
  const obsolete = Number(metrics.documents_obsolete ?? 0);
  const total = draft + review + approved + obsolete;
  if (total === 0) return [];
  const pct = (n: number) => Math.round((n / total) * 100);
  return [
    { label: "Draft", count: draft, pct: pct(draft), color: "bg-slate-400" },
    { label: "Under Review", count: review, pct: pct(review), color: "bg-amber-400" },
    { label: "Approved", count: approved, pct: pct(approved), color: "bg-green-500" },
    { label: "Obsolete", count: obsolete, pct: pct(obsolete), color: "bg-red-400" },
  ];
}

function buildCapaAgingRows(metrics: Record<string, unknown>): ChartRow[] {
  const b0 = Number(metrics.capas_0_30_days ?? 0);
  const b30 = Number(metrics.capas_31_60_days ?? 0);
  const b60 = Number(metrics.capas_61_90_days ?? 0);
  const b90 = Number(metrics.capas_over_90_days ?? 0);
  const total = b0 + b30 + b60 + b90;
  if (total === 0) return [];
  const pct = (n: number) => Math.round((n / total) * 100);
  return [
    { label: "0–30 days", count: b0, pct: pct(b0), color: "bg-green-500" },
    { label: "31–60 days", count: b30, pct: pct(b30), color: "bg-amber-400" },
    { label: "61–90 days", count: b60, pct: pct(b60), color: "bg-orange-500" },
    { label: "90+ days", count: b90, pct: pct(b90), color: "bg-red-500" },
  ];
}

export default function QMSAnalyticsPage() {
  const router = useRouter();
  const { data: kpiData, isLoading: kpiLoading } = usePlatformKPIs();
  const { data: dashData, isLoading: dashLoading } = useDashboard("qms_overview");
  const loading = kpiLoading || dashLoading;
  const kpis = kpiData?.kpis;

  const summaryMetrics = (dashData?.summary_metrics ?? {}) as Record<string, unknown>;
  const docStatusRows = buildDocStatusRows(summaryMetrics);
  const capaAgingRows = buildCapaAgingRows(summaryMetrics);

  const KPI_CARDS = [
    { title: "Open CAPAs", value: kpis?.open_capas ?? 0, icon: AlertTriangle, color: "text-amber-600" },
    { title: "Documents Total", value: kpis?.documents_total ?? 0, icon: CheckCircle2, color: "text-green-600" },
    { title: "Upcoming Trainings", value: kpis?.upcoming_trainings ?? 0, icon: Clock, color: "text-red-600" },
    { title: "Equipment Cal Due", value: kpis?.equipment_due_calibration ?? 0, icon: TrendingUp, color: "text-blue-600" },
  ];

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-sm">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <Home className="h-4 w-4 mr-1" />
          Home
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">QMS Analytics</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-6 w-6" />
          QMS Analytics
        </h1>
        <p className="text-muted-foreground text-sm mt-1">Quality metrics, trends, and compliance dashboards</p>
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
          <CardHeader><CardTitle className="text-base">Document Status Distribution</CardTitle></CardHeader>
          <CardContent>
            {dashLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-4 w-full" />)}
              </div>
            ) : docStatusRows.length === 0 ? (
              <p className="text-sm text-muted-foreground">No document status data available.</p>
            ) : (
              <div className="space-y-3">
                {docStatusRows.map((row) => (
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
          <CardHeader><CardTitle className="text-base">CAPA Aging Summary</CardTitle></CardHeader>
          <CardContent>
            {dashLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-4 w-full" />)}
              </div>
            ) : capaAgingRows.length === 0 ? (
              <p className="text-sm text-muted-foreground">No CAPA aging data available.</p>
            ) : (
              <div className="space-y-3">
                {capaAgingRows.map((row) => (
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
      </div>
    </div>
  );
}
