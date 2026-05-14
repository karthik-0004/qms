import { apiClient } from "../client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface User {
  id: string;
  platform_user_id: string;
  tenant_id: string;
  company_id: string | null;
  first_name: string;
  last_name: string;
  display_name: string | null;
  phone: string | null;
  department: string | null;
  job_title: string | null;
  avatar_url: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  // Augmented client-side from session/auth — not in UserResponse spec
  email?: string;
  role?: string;
  last_login?: string | null;
}

export interface AuditEntry {
  id: string;
  tenant_id: string | null;
  user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  ip_address: string | null;
  user_agent: string | null;
  metadata: Record<string, unknown>;
  severity: string;
  source_service: string | null;
  event_id: string | null;
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

  create: (data: {
    email?: string;
    platform_user_id?: string;
    first_name: string;
    last_name: string;
    display_name?: string;
    phone?: string;
    department?: string;
    job_title?: string;
  }) =>
    apiClient.post<BackendItem<User>>("/users", data).then((r) => r.data.data),

  update: (id: string, data: {
    first_name?: string;
    last_name?: string;
    display_name?: string;
    phone?: string;
    department?: string;
    job_title?: string;
  }) =>
    apiClient.patch<BackendItem<User>>(`/users/${id}`, data).then((r) => r.data.data),

  deactivate: (id: string) => apiClient.delete(`/users/${id}`).then((r) => r.data),
};

// ─── Companies ───────────────────────────────────────────────────────────────

export interface Company {
  id: string;
  tenant_id: string;
  name: string;
  email: string;
  phone: string | null;
  address: string | null;
  company_code: string;
  status: string;
  admin_id: string | null;
  employee_limit: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CompanyWithAdmin {
  company: Company;
  admin: User;
  temporary_password: string;
}

export interface CompanyUserCreated {
  user: CompanyUser;
  temporary_password: string;
}

export interface CompanyUser {
  id: string;
  platform_user_id: string;
  tenant_id: string;
  company_id: string;
  first_name: string;
  last_name: string;
  display_name: string | null;
  phone: string | null;
  department: string | null;
  job_title: string | null;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateCompanyPayload {
  name: string;
  email: string;
  phone?: string;
  address?: string;
  company_code?: string;
  employee_limit?: number;
  admin: {
    email: string;
    first_name: string;
    last_name: string;
    phone?: string;
  };
}

export interface CompanyRole {
  id: string;
  name: string;
  description: string | null;
  permissions: string[];
  is_system_role: boolean;
  scope: string;
  company_id: string | null;
  created_at: string;
  updated_at: string;
}

export const companiesApi = {
  list: (params?: { is_active?: boolean; page?: number; page_size?: number }) =>
    apiClient
      .get<BackendPage<Company>>("/companies", { params })
      .then((r) => ({
        items: r.data.data,
        total: r.data.pagination.total,
        page: r.data.pagination.page,
        page_size: r.data.pagination.page_size,
      })),

  get: (id: string) =>
    apiClient.get<BackendItem<Company>>(`/companies/${id}`).then((r) => r.data.data),

  create: (data: CreateCompanyPayload) =>
    apiClient.post<BackendItem<CompanyWithAdmin>>("/companies", data).then((r) => r.data.data as CompanyWithAdmin),

  update: (id: string, data: Partial<Pick<Company, "name" | "email" | "phone" | "address" | "employee_limit">>) =>
    apiClient.patch<BackendItem<Company>>(`/companies/${id}`, data).then((r) => r.data.data),

  deactivate: (id: string) => apiClient.delete(`/companies/${id}`).then((r) => r.data),

  listUsers: (companyId: string, params?: { is_active?: boolean; page?: number; page_size?: number }) =>
    apiClient
      .get<BackendPage<CompanyUser>>(`/companies/${companyId}/users`, { params })
      .then((r) => ({
        items: r.data.data,
        total: r.data.pagination.total,
        page: r.data.pagination.page,
        page_size: r.data.pagination.page_size,
      })),

  createUser: (
    companyId: string,
    data: { email: string; first_name: string; last_name: string; display_name?: string; phone?: string; department?: string; role_id?: string },
  ) =>
    apiClient.post<BackendItem<CompanyUserCreated>>(`/companies/${companyId}/users`, data).then((r) => r.data.data as CompanyUserCreated),

  listRoles: (companyId: string) =>
    apiClient.get<BackendItem<CompanyRole[]>>(`/companies/${companyId}/roles`).then((r) => r.data.data),

  createRole: (companyId: string, data: { name: string; permissions: string[]; description?: string }) =>
    apiClient.post<BackendItem<CompanyRole>>(`/companies/${companyId}/roles`, data).then((r) => r.data.data),

  assignUserRole: (companyId: string, userId: string, roleId: string) =>
    apiClient
      .post(`/companies/${companyId}/users/${userId}/roles`, { role_id: roleId })
      .then((r) => r.data),

  removeUserRole: (companyId: string, userId: string, roleId: string) =>
    apiClient.delete(`/companies/${companyId}/users/${userId}/roles/${roleId}`).then((r) => r.data),
};

export interface Role {
  id: string;
  name: string;
  description: string | null;
  permissions: string[];
  is_system_role: boolean;
  product: string | null;
  created_at: string;
  updated_at: string;
}

export interface UserPermissions {
  user_id: string;
  permissions: string[];
}

export interface MFASetupData {
  secret: string;
  provisioning_uri: string;
  qr_code_url: string;
}

// ─── Roles & Permissions ─────────────────────────────────────────────────────

export const rolesApi = {
  list: (params?: { product?: string }) =>
    apiClient
      .get<BackendItem<Role[]>>("/roles", { params })
      .then((r) => r.data.data),
};

export const userPermissionsApi = {
  get: (userId: string) =>
    apiClient
      .get<BackendItem<UserPermissions>>(`/users/${userId}/permissions`)
      .then((r) => r.data.data),

  assignRole: (userId: string, data: { role_id: string }) =>
    apiClient
      .post(`/users/${userId}/roles`, data)
      .then((r) => r.data),

  removeRole: (userId: string, roleId: string) =>
    apiClient
      .delete(`/users/${userId}/roles/${roleId}`)
      .then((r) => r.data),
};

// ─── Auth (MFA / logout-all) ─────────────────────────────────────────────────

export const authApi = {
  setupMFA: () =>
    apiClient
      .post<BackendItem<MFASetupData>>("/auth/mfa/setup")
      .then((r) => r.data.data),

  verifyMFA: (code: string) =>
    apiClient
      .post("/auth/mfa/verify", { code })
      .then((r) => r.data),

  disableMFA: (password: string) =>
    apiClient
      .post("/auth/mfa/disable", { password })
      .then((r) => r.data),

  logoutAll: () =>
    apiClient
      .post("/auth/logout-all")
      .then((r) => r.data),
};

export const auditApi = {
  list: (params?: {
    tenant_id?: string;
    user_id?: string;
    action?: string;
    resource_type?: string;
    resource_id?: string;
    severity?: string;
    from_date?: string;
    to_date?: string;
    page?: number;
    page_size?: number;
    sort?: string;
  }) =>
    apiClient
      .get<{ data: AuditEntry[]; pagination: { total: number; page: number; page_size: number; total_pages: number; has_next: boolean; has_prev: boolean } }>(
        "/audit/logs",
        { params },
      )
      .then((r) => ({
        items: r.data.data,
        total: r.data.pagination.total,
        page: r.data.pagination.page,
        page_size: r.data.pagination.page_size,
        total_pages: r.data.pagination.total_pages,
        has_next: r.data.pagination.has_next,
        has_prev: r.data.pagination.has_prev,
      })),
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
