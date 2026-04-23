import { apiClient } from "../client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  status: string;
  tenant_id: string;
  last_login: string | null;
  created_at: string;
}

export interface AuditEntry {
  id: string;
  action: string;
  entity_type: string;
  entity_id: string;
  user_id: string;
  tenant_id: string;
  details: Record<string, unknown> | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Users ──────────────────────────────────────────────────────────────────

export const usersApi = {
  list: (params?: { search?: string; role?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<User>>("/users/users", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<User>(`/users/users/${id}`).then((r) => r.data),

  create: (data: { email: string; first_name: string; last_name: string; role: string; password: string }) =>
    apiClient.post<User>("/users/users", data).then((r) => r.data),

  update: (id: string, data: Partial<User>) =>
    apiClient.patch<User>(`/users/users/${id}`, data).then((r) => r.data),

  deactivate: (id: string) =>
    apiClient.post<User>(`/users/users/${id}/deactivate`).then((r) => r.data),
};

// ─── Audit ──────────────────────────────────────────────────────────────────

export const auditApi = {
  list: (params?: { entity_type?: string; entity_id?: string; user_id?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<AuditEntry>>("/audit/entries", { params }).then((r) => r.data),
};
