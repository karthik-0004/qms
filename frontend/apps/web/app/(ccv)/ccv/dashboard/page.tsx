"use client";

import {
  Building2,
  FileText,
  Wrench,
  Users,
  DollarSign,
  TrendingUp,
} from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useContracts, useWorkOrders } from "@/lib/hooks/queries/ccv";
import { usePlatformKPIs } from "@/lib/hooks/queries/analytics";

interface KPI {
  label: string;
  value: string | number;
  icon: React.ReactNode;
  color: string;
}

const CONTRACT_STATUS: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-slate-100 text-slate-700" },
  under_review: { label: "Under Review", color: "bg-amber-100 text-amber-800" },
  approved: { label: "Approved", color: "bg-blue-100 text-blue-800" },
  active: { label: "Active", color: "bg-green-100 text-green-800" },
  expired: { label: "Expired", color: "bg-slate-100 text-slate-500" },
  terminated: { label: "Terminated", color: "bg-red-100 text-red-700" },
};

const WO_STATUS: Record<string, { label: string; color: string }> = {
  pending: { label: "Pending", color: "bg-slate-100 text-slate-700" },
  assigned: { label: "Assigned", color: "bg-blue-100 text-blue-800" },
  in_progress: { label: "In Progress", color: "bg-amber-100 text-amber-800" },
  on_hold: { label: "On Hold", color: "bg-orange-100 text-orange-800" },
  completed: { label: "Completed", color: "bg-green-100 text-green-800" },
  cancelled: { label: "Cancelled", color: "bg-red-100 text-red-700" },
};

const PRIORITY_BADGE: Record<string, string> = {
  low: "bg-slate-100 text-slate-600",
  normal: "bg-blue-50 text-blue-700",
  high: "bg-orange-100 text-orange-800",
  urgent: "bg-red-100 text-red-800",
};

export default function CCVDashboardPage() {
  const { data: contractsData, isLoading: contractsLoading } = useContracts({ page: 1, page_size: 4 });
  const { data: woData, isLoading: woLoading } = useWorkOrders({ page: 1, page_size: 4 });
  const { data: kpiData, isLoading: kpiLoading } = usePlatformKPIs();
  const recentContracts = contractsData?.items ?? [];
  const recentWorkOrders = woData?.items ?? [];
  const loading = contractsLoading || woLoading || kpiLoading;
  const kpis = kpiData?.kpis;

  const ccvKPIs: KPI[] = [
    { label: "Total Users", value: kpis?.total_users ?? 0, icon: <Building2 className="h-5 w-5" />, color: "text-blue-600" },
    { label: "Documents Total", value: kpis?.documents_total ?? 0, icon: <FileText className="h-5 w-5" />, color: "text-violet-600" },
    { label: "Work Orders (MTD)", value: kpis?.workorders_this_month ?? 0, icon: <Wrench className="h-5 w-5" />, color: "text-amber-600" },
    { label: "Active Users (30d)", value: kpis?.active_users_30d ?? 0, icon: <Users className="h-5 w-5" />, color: "text-green-600" },
    { label: "Certs Issued YTD", value: kpis?.certificates_issued_ytd ?? 0, icon: <DollarSign className="h-5 w-5" />, color: "text-emerald-600" },
    { label: "Open Quality Events", value: kpis?.open_quality_events ?? 0, icon: <TrendingUp className="h-5 w-5" />, color: "text-red-600" },
  ];

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold tracking-tight">CCV Operations Dashboard</h1>
        <p className="text-muted-foreground text-sm mt-1">
          RainerCCV — Customer, Contract & Field Service Overview
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        {loading
          ? Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardContent className="pt-4">
                <Skeleton className="h-4 w-24 mb-2" />
                <Skeleton className="h-8 w-16 mb-1" />
                <Skeleton className="h-3 w-28" />
              </CardContent>
            </Card>
          ))
          : ccvKPIs.map((kpi) => (
            <Card key={kpi.label}>
              <CardContent className="pt-4">
                <div className={`mb-2 ${kpi.color}`}>{kpi.icon}</div>
                <p className="text-xs text-muted-foreground">{kpi.label}</p>
                <p className="text-2xl font-bold mt-1">{kpi.value}</p>
              </CardContent>
            </Card>
          ))
        }
      </div>

      {/* Recent Contracts + Work Orders */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Contracts */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4" />
              Recent Contracts
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loading
                ? Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                    <div className="space-y-1">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-5 w-16 rounded-full" />
                  </div>
                ))
                : recentContracts.map((c) => {
                  const cfg = CONTRACT_STATUS[c.status] ?? { label: c.status, color: "" };
                  return (
                    <div key={c.id} className="flex items-start justify-between py-2 border-b last:border-0">
                      <div>
                        <p className="font-mono text-xs font-semibold">{c.contract_number}</p>
                        <p className="text-sm font-medium">{c.customer_name}</p>
                        <p className="text-xs text-muted-foreground truncate max-w-[200px]">{c.title}</p>
                        <p className="text-xs text-muted-foreground font-medium mt-0.5">
                          ${c.total_value.toLocaleString()}
                        </p>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${cfg.color}`}>
                        {cfg.label}
                      </span>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>

        {/* Recent Work Orders */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Wrench className="h-4 w-4" />
              Recent Work Orders
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loading
                ? Array.from({ length: 4 }).map((_, i) => (
                  <div key={i} className="flex items-center justify-between py-2 border-b last:border-0">
                    <div className="space-y-1">
                      <Skeleton className="h-4 w-32" />
                      <Skeleton className="h-3 w-48" />
                    </div>
                    <Skeleton className="h-5 w-16 rounded-full" />
                  </div>
                ))
                : recentWorkOrders.map((wo) => {
                  const scfg = WO_STATUS[wo.status] ?? { label: wo.status, color: "" };
                  const pcfg = PRIORITY_BADGE[wo.priority] ?? "";
                  return (
                    <div key={wo.id} className="flex items-start justify-between py-2 border-b last:border-0">
                      <div>
                        <p className="font-mono text-xs font-semibold">{wo.work_order_number}</p>
                        <p className="text-sm font-medium">{wo.customer_name}</p>
                        <p className="text-xs text-muted-foreground truncate max-w-[200px]">{wo.title}</p>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <span className={`text-xs px-1.5 py-0.5 rounded font-medium ${pcfg}`}>
                            {wo.priority.toUpperCase()}
                          </span>
                          <span className="text-xs text-muted-foreground">{wo.assigned_technician_id ?? "Unassigned"}</span>
                        </div>
                      </div>
                      <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${scfg.color}`}>
                        {scfg.label}
                      </span>
                    </div>
                  );
                })}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
