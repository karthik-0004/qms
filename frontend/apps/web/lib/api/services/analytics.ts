import { apiClient } from "../client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface PlatformKPIs {
  tenant_id: string;
  as_of: string;
  kpis: {
    total_users: number;
    active_users_30d: number;
    documents_total: number;
    documents_pending_review: number;
    open_capas: number;
    overdue_capas: number;
    upcoming_trainings: number;
    equipment_due_calibration: number;
    open_quality_events: number;
    workorders_this_month: number;
    certificates_issued_ytd: number;
  };
}

export interface DashboardMeta {
  id: string;
  name: string;
  product: string | null;
}

export interface DashboardData {
  dashboard_id: string;
  tenant_id: string;
  period: { start: string; end: string };
  charts: Array<Record<string, unknown>>;
  summary_metrics: Record<string, unknown>;
}

export interface TimeSeriesData {
  metric: string;
  interval: string;
  data_points: Array<{ timestamp: string; value: number }>;
  tenant_id: string;
}

// ─── API ────────────────────────────────────────────────────────────────────

export const analyticsApi = {
  getKPIs: () =>
    apiClient.get<{ data: PlatformKPIs }>("/analytics/kpis").then((r) => r.data.data),

  listDashboards: (product?: string) =>
    apiClient
      .get<{ data: DashboardMeta[] }>("/analytics/dashboards", { params: product ? { product } : undefined })
      .then((r) => r.data.data),

  getDashboard: (dashboardId: string, dateRangeDays?: number) =>
    apiClient
      .get<{ data: DashboardData }>(`/analytics/dashboards/${dashboardId}`, {
        params: dateRangeDays ? { date_range_days: dateRangeDays } : undefined,
      })
      .then((r) => r.data.data),

  getTimeSeries: (params: { metric: string; interval?: string; days?: number }) =>
    apiClient
      .get<{ data: TimeSeriesData }>("/analytics/time-series", { params })
      .then((r) => r.data.data),
};
