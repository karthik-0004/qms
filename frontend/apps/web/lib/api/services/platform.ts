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

export interface TenantPrimaryContact {
  first_name: string | null;
  last_name: string | null;
  email: string | null;
  phone: string | null;
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
  company_profile: Record<string, unknown>;
  billing_profile: Record<string, unknown>;
  primary_contact: TenantPrimaryContact;
  created_at: string;
  updated_at: string;
}

export interface TenantSettingsDto {
  id: string;
  tenant_id: string;
  max_users: number;
  max_storage_gb: number;
  features: Record<string, unknown>;
  branding: Record<string, unknown>;
  webhook_urls: string[];
  timezone: string;
  locale: string;
  created_at: string;
  updated_at: string;
}

export interface AddressPayload {
  address_line1?: string;
  address_line2?: string;
  city?: string;
  state?: string;
  country?: string;
  postal_code?: string;
}

export interface CreateTenantPayload {
  tenant_name: string;
  products: string[];
  tier: string;
  region: string;
  primary_contact: {
    first_name: string;
    last_name: string;
    email: string;
    phone?: string;
  };
  company?: {
    website?: string;
    industry?: string;
    notes?: string;
  };
  address?: AddressPayload;
  billing?: {
    billing_email?: string;
    billing_phone?: string;
    tax_id?: string;
    billing_address_same_as_address: boolean;
    billing_address?: AddressPayload;
  };
  tenant_defaults?: {
    timezone: string;
    locale: string;
  };
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
    apiClient.get<BackendPage<User>>("/users", { params }).then((r) => ({
      items: r.data.data,
      total: r.data.pagination.total,
      page: r.data.pagination.page,
      page_size: r.data.pagination.page_size,
    })),

  get: (id: string) =>
    apiClient.get<BackendItem<User>>(`/users/${id}`).then((r) => r.data.data),

  create: (data: { email: string; first_name: string; last_name: string; role: string; password: string }) =>
    apiClient.post<BackendItem<User>>("/users", data).then((r) => r.data.data),

  update: (id: string, data: Partial<User>) =>
    apiClient.patch<BackendItem<User>>(`/users/${id}`, data).then((r) => r.data.data),

  deactivate: (id: string) => apiClient.delete(`/users/${id}`).then((r) => r.data),
};

// ─── Audit ──────────────────────────────────────────────────────────────────

export const auditApi = {
  list: (params?: { entity_type?: string; entity_id?: string; user_id?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<AuditEntry>>("/audit/entries", { params }).then((r) => r.data),
};

// ─── Tenants ─────────────────────────────────────────────────────────────────

export type UpdateTenantSettingsPayload = {
  max_users?: number;
  max_storage_gb?: number;
  features?: Record<string, unknown>;
  branding?: Record<string, unknown>;
  smtp_config?: Record<string, unknown> | null;
  webhook_urls?: string[];
  timezone?: string;
  locale?: string;
};

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

  create: (data: CreateTenantPayload) =>
    apiClient.post<BackendItem<Tenant>>("/tenants", data).then((r) => r.data.data),

  update: (id: string, data: { tenant_name?: string; tier?: string; products?: string[] }) =>
    apiClient.patch<BackendItem<Tenant>>(`/tenants/${id}`, data).then((r) => r.data.data),

  delete: (id: string) => apiClient.delete(`/tenants/${id}`).then((r) => r.data),

  getSettings: (tenantId: string) =>
    apiClient.get<BackendItem<TenantSettingsDto>>(`/tenants/${tenantId}/settings`).then((r) => r.data.data),

  updateSettings: (tenantId: string, data: UpdateTenantSettingsPayload) =>
    apiClient.patch(`/tenants/${tenantId}/settings`, data).then((r) => r.data),

  suspend: (id: string) =>
    apiClient.post(`/tenants/${id}/suspend`).then((r) => r.data),

  activate: (id: string) =>
    apiClient.post(`/tenants/${id}/activate`).then((r) => r.data),

  resendWelcomeEmail: (tenantId: string) =>
    apiClient
      .post<{ message: string }>(
        "/tenants/resend-welcome-email",
        { tenant_id: tenantId },
        { timeout: 120_000 },
      )
      .then((r) => r.data),
};
