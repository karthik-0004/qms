"use client";

import { useRouter } from "next/navigation";
import { BarChart3, FlaskConical, Cpu, CheckCircle2, XCircle, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { usePlatformKPIs, useDashboard } from "@/lib/hooks/queries/analytics";

export default function EMAnalyticsPage() {
  const router = useRouter();
  const { data: kpiData, isLoading: kpiLoading } = usePlatformKPIs();
  const { data: dashData, isLoading: dashLoading } = useDashboard("em_overview");
  const loading = kpiLoading || dashLoading;
  const kpis = kpiData?.kpis;

  const KPI_CARDS = [
    { title: "Open Quality Events", value: kpis?.open_quality_events ?? 0, icon: FlaskConical, color: "text-blue-600" },
    { title: "Active Users (30d)", value: kpis?.active_users_30d ?? 0, icon: Cpu, color: "text-cyan-600" },
    { title: "Open CAPAs", value: kpis?.open_capas ?? 0, icon: CheckCircle2, color: "text-green-600" },
    { title: "Overdue CAPAs", value: kpis?.overdue_capas ?? 0, icon: XCircle, color: "text-red-600" },
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
        <span className="text-foreground font-medium">EM Analytics</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <BarChart3 className="h-6 w-6" />
          EM Analytics
        </h1>
        <p className="text-muted-foreground text-sm mt-1">Environmental monitoring metrics and AI analysis trends</p>
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
          <CardHeader><CardTitle className="text-base">Plate Status Pipeline</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { label: "Registered", count: 12, pct: 4, color: "bg-slate-400" },
                { label: "Incubation", count: 28, pct: 8, color: "bg-amber-400" },
                { label: "Imaging", count: 15, pct: 4, color: "bg-purple-500" },
                { label: "AI Analysis", count: 23, pct: 7, color: "bg-cyan-500" },
                { label: "QA Review", count: 18, pct: 5, color: "bg-orange-400" },
                { label: "Approved", count: 264, pct: 77, color: "bg-green-500" },
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
          <CardHeader><CardTitle className="text-base">AI Detection Accuracy</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { label: "True Positive", count: 1847, pct: 85, color: "bg-green-500" },
                { label: "False Positive", count: 89, pct: 4, color: "bg-amber-400" },
                { label: "True Negative", count: 198, pct: 9, color: "bg-blue-400" },
                { label: "False Negative", count: 42, pct: 2, color: "bg-red-500" },
              ].map((row) => (
                <div key={row.label} className="flex items-center gap-3">
                  <span className="text-sm text-muted-foreground w-28">{row.label}</span>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div className={`h-full ${row.color} rounded-full`} style={{ width: `${row.pct}%` }} />
                  </div>
                  <span className="text-sm font-medium w-12 text-right">{row.count}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
