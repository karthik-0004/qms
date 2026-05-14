"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  auditApi,
  authApi,
  companiesApi,
  rolesApi,
  tenantsApi,
  userPermissionsApi,
  type UpdateTenantSettingsPayload,
  usersApi,
} from "@/lib/api/services/platform";
import { toast } from "sonner";

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
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      toast.success("User created successfully");
    },
    onError: () => toast.error("Failed to create user"),
  });
}

export function useUpdateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof usersApi.update>[1] }) =>
      usersApi.update(id, data),
    onSuccess: (_res, vars) => {
      qc.invalidateQueries({ queryKey: ["users"] });
      qc.invalidateQueries({ queryKey: ["users", vars.id] });
      toast.success("User updated");
    },
    onError: () => toast.error("Failed to update user"),
  });
}

export function useDeactivateUser() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => usersApi.deactivate(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["users"] });
      toast.success("User deactivated");
    },
    onError: () => toast.error("Failed to deactivate user"),
  });
}

export function useReactivateUser() {
  const qc = useQueryClient();
  return useMutation({
    // Reactivate via PATCH with is_active — backend UpdateUserRequest doesn't have is_active.
    // The spec deactivate is DELETE /users/{id}. There is no separate reactivate endpoint in the spec.
    // We surface this as a TODO — the UI will show the state but the button is disabled.
    // TODO: Wire when a reactivate endpoint is implemented in user-service
    mutationFn: (_id: string) => Promise.reject(new Error("Reactivate endpoint not yet implemented")),
    onError: () => toast.error("Reactivate is not yet available"),
  });
}

// ─── Roles & Permissions ─────────────────────────────────────────────────────

export function useRoles(params?: Parameters<typeof rolesApi.list>[0]) {
  return useQuery({
    queryKey: ["roles", params],
    queryFn: () => rolesApi.list(params),
    staleTime: 60_000,
  });
}

export function useUserPermissions(userId: string) {
  return useQuery({
    queryKey: ["users", userId, "permissions"],
    queryFn: () => userPermissionsApi.get(userId),
    enabled: !!userId,
    staleTime: 30_000,
  });
}

export function useAssignRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      userPermissionsApi.assignRole(userId, { role_id: roleId }),
    onSuccess: (_res, vars) => {
      qc.invalidateQueries({ queryKey: ["users", vars.userId, "permissions"] });
      qc.invalidateQueries({ queryKey: ["users", vars.userId] });
      toast.success("Role assigned");
    },
    onError: () => toast.error("Failed to assign role"),
  });
}

export function useRemoveRole() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ userId, roleId }: { userId: string; roleId: string }) =>
      userPermissionsApi.removeRole(userId, roleId),
    onSuccess: (_res, vars) => {
      qc.invalidateQueries({ queryKey: ["users", vars.userId, "permissions"] });
      qc.invalidateQueries({ queryKey: ["users", vars.userId] });
      toast.success("Role removed");
    },
    onError: () => toast.error("Failed to remove role"),
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

export function useUserAuditLogs(userId: string, page = 1) {
  return useQuery({
    queryKey: ["audit-logs", "user", userId, page],
    queryFn: () =>
      auditApi.list({
        user_id: userId,
        page,
        page_size: 20,
      }),
    enabled: !!userId,
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
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["tenants"] });
      qc.invalidateQueries({ queryKey: ["users"] });
      qc.invalidateQueries({ queryKey: ["tenants", "by-slug", data.slug] });
    },
  });
}

export function useUpdateTenant() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof tenantsApi.update>[1] }) =>
      tenantsApi.update(id, data),
    onSuccess: (data) => {
      qc.invalidateQueries({ queryKey: ["tenants"] });
      qc.invalidateQueries({ queryKey: ["tenants", "by-slug", data.slug] });
    },
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

export function useResendTenantWelcomeEmail() {
  return useMutation({
    mutationFn: tenantsApi.resendWelcomeEmail,
  });
}

export function useTenantSettings(tenantId: string | undefined) {
  return useQuery({
    queryKey: ["tenants", "settings", tenantId],
    queryFn: () => tenantsApi.getSettings(tenantId!),
    enabled: Boolean(tenantId),
    staleTime: 30_000,
  });
}

export function useUpdateTenantSettings() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ tenantId, data }: { tenantId: string; data: UpdateTenantSettingsPayload }) =>
      tenantsApi.updateSettings(tenantId, data),
    onSuccess: (_res, vars) => {
      qc.invalidateQueries({ queryKey: ["tenants", "settings", vars.tenantId] });
      qc.invalidateQueries({ queryKey: ["tenants"] });
      toast.success("Settings saved");
    },
    onError: () => toast.error("Failed to save settings"),
  });
}

export function useDeleteTenant() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: tenantsApi.delete,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tenants"] });
      qc.invalidateQueries({ queryKey: ["users"] });
    },
  });
}

// ─── Auth (MFA / logout-all) ─────────────────────────────────────────────────

export function useSetupMFA() {
  return useMutation({
    mutationFn: authApi.setupMFA,
    onError: () => toast.error("Failed to start MFA setup"),
  });
}

export function useVerifyMFA() {
  return useMutation({
    mutationFn: (code: string) => authApi.verifyMFA(code),
    onSuccess: () => toast.success("MFA enabled successfully"),
    onError: () => toast.error("Invalid code — please try again"),
  });
}

export function useDisableMFA() {
  return useMutation({
    mutationFn: (password: string) => authApi.disableMFA(password),
    onSuccess: () => toast.success("MFA disabled"),
    onError: () => toast.error("Failed to disable MFA — check your password"),
  });
}

export function useLogoutAll() {
  return useMutation({
    mutationFn: authApi.logoutAll,
    onSuccess: () => toast.success("Signed out from all devices"),
    onError: () => toast.error("Failed to sign out all devices"),
  });
}

// ─── Companies ───────────────────────────────────────────────────────────────

export function useCompanies(params?: Parameters<typeof companiesApi.list>[0]) {
  return useQuery({
    queryKey: ["companies", params],
    queryFn: () => companiesApi.list(params),
    staleTime: 30_000,
  });
}

export function useCompany(id: string) {
  return useQuery({
    queryKey: ["companies", id],
    queryFn: () => companiesApi.get(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}

export function useCreateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: companiesApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies"] }),
  });
}

export function useUpdateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof companiesApi.update>[1] }) =>
      companiesApi.update(id, data),
    onSuccess: (_res, vars) => qc.invalidateQueries({ queryKey: ["companies", vars.id] }),
  });
}

export function useDeactivateCompany() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: companiesApi.deactivate,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies"] }),
  });
}

export function useCompanyUsers(
  companyId: string,
  params?: Parameters<typeof companiesApi.listUsers>[1],
) {
  return useQuery({
    queryKey: ["companies", companyId, "users", params],
    queryFn: () => companiesApi.listUsers(companyId, params),
    enabled: !!companyId,
    staleTime: 30_000,
  });
}

export function useCreateCompanyUser(companyId: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Parameters<typeof companiesApi.createUser>[1]) =>
      companiesApi.createUser(companyId, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["companies", companyId, "users"] }),
  });
}

export function useCompanyRoles(companyId: string) {
  return useQuery({
    queryKey: ["companies", companyId, "roles"],
    queryFn: () => companiesApi.listRoles(companyId),
    enabled: !!companyId,
    staleTime: 60_000,
  });
}
