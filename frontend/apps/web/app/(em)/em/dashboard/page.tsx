"use client";

import { useRouter } from "next/navigation";
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  Clock,
  FlaskConical,
  ImageIcon,
  Layers,
  RefreshCw,
  ArrowLeft,
  Home,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { usePlates } from "@/lib/hooks/queries/em";
import { usePlatformKPIs } from "@/lib/hooks/queries/analytics";

interface EMStat {
  label: string;
  value: number | string;
  delta?: string;
  deltaPositive?: boolean;
  icon: React.ElementType;
  color: string;
}

const STATUS_CONFIG: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
  registered: { label: "Registered", variant: "secondary" },
  sampling_in_progress: { label: "Sampling", variant: "secondary" },
  sampled: { label: "Sampled", variant: "secondary" },
  incubation_started: { label: "Incubating", variant: "default" },
  incubation_complete: { label: "Incubation Done", variant: "default" },
  imaging_pending: { label: "Imaging Pending", variant: "outline" },
  imaging_in_progress: { label: "Imaging", variant: "default" },
  imaging_complete: { label: "Imaged", variant: "default" },
  ai_analysis_pending: { label: "AI Queued", variant: "outline" },
  ai_analysis_running: { label: "AI Running", variant: "default" },
  ai_analysis_complete: { label: "AI Done", variant: "default" },
  ai_analysis_failed: { label: "AI Failed", variant: "destructive" },
  qa_review_pending: { label: "QA Pending", variant: "outline" },
  qa_review_in_progress: { label: "In QA Review", variant: "default" },
  approved: { label: "Approved", variant: "default" },
  rejected: { label: "Rejected", variant: "destructive" },
  cancelled: { label: "Cancelled", variant: "destructive" },
};

export default function EMDashboardPage() {
  const router = useRouter();
  const { data: platesData, isLoading: platesLoading } = usePlates({ page: 1, page_size: 5 });
  const { data: kpiData, isLoading: kpiLoading } = usePlatformKPIs();
  const recentPlates = platesData?.items ?? [];
  const loading = platesLoading || kpiLoading;
  const kpis = kpiData?.kpis;

  const emStats: EMStat[] = [
    { label: "Quality Events", value: kpis?.open_quality_events ?? 0, icon: Layers, color: "text-blue-500" },
    { label: "Documents Pending", value: kpis?.documents_pending_review ?? 0, icon: Clock, color: "text-amber-500" },
    { label: "Active Users (30d)", value: kpis?.active_users_30d ?? 0, icon: Activity, color: "text-purple-500" },
    { label: "Equipment Cal Due", value: kpis?.equipment_due_calibration ?? 0, icon: ImageIcon, color: "text-cyan-500" },
    { label: "Open CAPAs", value: kpis?.open_capas ?? 0, icon: CheckCircle2, color: "text-green-500" },
    { label: "Overdue CAPAs", value: kpis?.overdue_capas ?? 0, deltaPositive: false, icon: AlertTriangle, color: "text-red-500" },
  ];

  return (
    <div className="space-y-6 p-6">
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
        <span className="text-foreground font-medium">EM Dashboard</span>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">EndGame Biotech — EM Dashboard</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Environmental monitoring plate tracking and AI colony detection
          </p>
        </div>
        <Button variant="outline" size="sm">
          <RefreshCw className="mr-2 h-4 w-4" />
          Refresh
        </Button>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="p-6">
                <Skeleton className="h-4 w-24 mb-3" />
                <Skeleton className="h-8 w-16 mb-2" />
                <Skeleton className="h-3 w-20" />
              </CardContent>
            </Card>
          ))
          : emStats.map((stat) => (
            <Card key={stat.label}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.label}
                </CardTitle>
                <stat.icon className={`h-5 w-5 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <p className="text-3xl font-bold">{stat.value}</p>
                {stat.delta && (
                  <p className={`text-xs mt-1 ${stat.deltaPositive ? "text-green-600" : "text-amber-600"}`}>
                    {stat.delta}
                  </p>
                )}
              </CardContent>
            </Card>
          ))}
      </div>

      {/* Recent Plates */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <FlaskConical className="h-5 w-5 text-muted-foreground" />
            <CardTitle className="text-base">Recent Plates</CardTitle>
          </div>
          <Button variant="ghost" size="sm" asChild>
            <a href="/em/plates">View all</a>
          </Button>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-muted-foreground">
                    <th className="text-left py-2 pr-4 font-medium">Barcode</th>
                    <th className="text-left py-2 pr-4 font-medium">Type</th>
                    <th className="text-left py-2 pr-4 font-medium">Status</th>
                    <th className="text-left py-2 font-medium">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {recentPlates.map((plate) => {
                    const cfg = STATUS_CONFIG[plate.status] ?? { label: plate.status, variant: "outline" as const };
                    return (
                      <tr key={plate.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="py-3 pr-4 font-mono font-medium">{plate.barcode}</td>
                        <td className="py-3 pr-4 capitalize text-muted-foreground">
                          {plate.plate_type.replace(/_/g, " ")}
                        </td>
                        <td className="py-3 pr-4">
                          <Badge variant={cfg.variant} className="whitespace-nowrap">
                            {cfg.label}
                          </Badge>
                        </td>
                        <td className="py-3 text-muted-foreground">
                          {new Date(plate.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
