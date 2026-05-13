"use client";

import { useQuery } from "@tanstack/react-query";
import { analyticsApi } from "@/lib/api/services/analytics";

// ─── Platform KPIs ─────────────────────────────────────────────────────────

export function usePlatformKPIs(options?: { enabled?: boolean }) {
  return useQuery({
    queryKey: ["analytics", "kpis"],
    queryFn: () => analyticsApi.getKPIs(),
    staleTime: 60_000,
    enabled: options?.enabled !== false,
  });
}

// ─── Dashboards ────────────────────────────────────────────────────────────

export function useDashboards(product?: string) {
  return useQuery({
    queryKey: ["analytics", "dashboards", product],
    queryFn: () => analyticsApi.listDashboards(product),
    staleTime: 120_000,
  });
}

export function useDashboard(dashboardId: string, dateRangeDays?: number) {
  return useQuery({
    queryKey: ["analytics", "dashboard", dashboardId, dateRangeDays],
    queryFn: () => analyticsApi.getDashboard(dashboardId, dateRangeDays),
    enabled: !!dashboardId,
    staleTime: 10_000,
    refetchInterval: 30_000,
  });
}

// ─── Time Series ───────────────────────────────────────────────────────────

export function useTimeSeries(params: { metric: string; interval?: string; days?: number }) {
  return useQuery({
    queryKey: ["analytics", "time-series", params],
    queryFn: () => analyticsApi.getTimeSeries(params),
    enabled: !!params.metric,
    staleTime: 60_000,
  });
}
