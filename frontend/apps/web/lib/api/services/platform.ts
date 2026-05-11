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

export interface Tenant {
  id: string;
  tenant_name: string;
  slug: string;
  db_name: string;
  status: string;
  tier: string;
  products: string[];
  region: string;
  created_at: string;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// Backend envelope shape for paginated responses
interface BackendPage<T> {
  data: T[];
  pagination: { total: number; page: number; page_size: number };
}

// Backend envelope shape for single-item responses
interface BackendItem<T> {
  data: T;
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

// ─── Tenants ─────────────────────────────────────────────────────────────────

export const tenantsApi = {
  list: (params?: { status_filter?: string; page?: number; page_size?: number }) =>
    apiClient
      .get<BackendPage<Tenant>>("/tenants", { params })
      .then((r) => ({
        items: r.data.data,
        total: r.data.pagination.total,
        page: r.data.pagination.page,
        page_size: r.data.pagination.page_size,
      })),

  get: (id: string) =>
    apiClient.get<BackendItem<Tenant>>(`/tenants/${id}`).then((r) => r.data.data),

  getBySlug: (slug: string) =>
    apiClient
      .get<BackendItem<Tenant>>(`/tenants/by-slug/${encodeURIComponent(slug)}`)
      .then((r) => r.data.data),

  create: (data: { tenant_name: string; products: string[]; tier: string; region: string }) =>
    apiClient.post<BackendItem<Tenant>>("/tenants", data).then((r) => r.data.data),

  update: (id: string, data: { tenant_name?: string; tier?: string; products?: string[] }) =>
    apiClient.patch<BackendItem<Tenant>>(`/tenants/${id}`, data).then((r) => r.data.data),

  suspend: (id: string) =>
    apiClient.post(`/tenants/${id}/suspend`).then((r) => r.data),

  activate: (id: string) =>
    apiClient.post(`/tenants/${id}/activate`).then((r) => r.data),
};
