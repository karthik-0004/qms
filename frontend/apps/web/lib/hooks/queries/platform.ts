"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { usersApi, auditApi, tenantsApi } from "@/lib/api/services/platform";

// ─── Users ──────────────────────────────────────────────────────────────────

export function useUsers(params?: Parameters<typeof usersApi.list>[0]) {
  return useQuery({
    queryKey: ["users", params],
    queryFn: () => usersApi.list(params),
    staleTime: 30_000,
  });
}

export function useUser(id: string) {
  return useQuery({
    queryKey: ["users", id],
    queryFn: () => usersApi.get(id),
    enabled: !!id,
  });
}

export function useCreateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: usersApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });
}

export function useUpdateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof usersApi.update>[1] }) =>
      usersApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["users"] }),
  });
}

// ─── Audit ──────────────────────────────────────────────────────────────────

export function useAuditLog(params?: Parameters<typeof auditApi.list>[0]) {
  return useQuery({
    queryKey: ["audit", params],
    queryFn: () => auditApi.list(params),
    staleTime: 60_000,
  });
}

/** Summaries for super-admin dashboard KPIs — only fetched when enabled to avoid forbidden calls for tenant roles. */
export function useSuperAdminDashboardMetrics(enabled: boolean) {
  const tenantsCount = useQuery({
    queryKey: ["super-admin-dash", "tenants-total"],
    queryFn: () => tenantsApi.list({ page: 1, page_size: 1 }),
    enabled,
    staleTime: 30_000,
  });
  const activeTenantsCount = useQuery({
    queryKey: ["super-admin-dash", "tenants-active"],
    queryFn: () => tenantsApi.list({ page: 1, page_size: 1, status_filter: "active" }),
    enabled,
    staleTime: 30_000,
  });
  const usersCount = useQuery({
    queryKey: ["super-admin-dash", "users-total"],
    queryFn: () => usersApi.list({ page: 1, page_size: 1 }),
    enabled,
    staleTime: 30_000,
  });
  const auditCount = useQuery({
    queryKey: ["super-admin-dash", "audit-total"],
    queryFn: () => auditApi.list({ page: 1, page_size: 1 }),
    enabled,
    staleTime: 60_000,
  });

  return {
    tenantTotal: tenantsCount.data?.total ?? 0,
    activeTenantTotal: activeTenantsCount.data?.total ?? 0,
    userTotal: usersCount.data?.total ?? 0,
    auditTotal: auditCount.data?.total ?? 0,
    isLoading:
      tenantsCount.isLoading ||
      activeTenantsCount.isLoading ||
      usersCount.isLoading ||
      auditCount.isLoading,
  };
}

// ─── Tenants ─────────────────────────────────────────────────────────────────

export function useTenants(params?: Parameters<typeof tenantsApi.list>[0]) {
  return useQuery({
    queryKey: ["tenants", params],
    queryFn: () => tenantsApi.list(params),
    staleTime: 30_000,
  });
}

export function useTenantBySlug(slug: string) {
  return useQuery({
    queryKey: ["tenants", "by-slug", slug],
    queryFn: () => tenantsApi.getBySlug(slug),
    enabled: Boolean(slug),
    staleTime: 30_000,
  });
}

export function useCreateTenant() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: tenantsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenants"] }),
  });
}

export function useUpdateTenant() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof tenantsApi.update>[1] }) =>
      tenantsApi.update(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenants"] }),
  });
}

export function useSuspendTenant() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: tenantsApi.suspend,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenants"] }),
  });
}

export function useActivateTenant() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: tenantsApi.activate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenants"] }),
  });
}
