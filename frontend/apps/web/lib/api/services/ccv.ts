import { apiClient } from "../client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Customer {
  id: string;
  company_name: string;
  status: string;
  industry: string | null;
  email: string | null;
  phone: string | null;
  city: string | null;
  state: string | null;
  contact_count: number;
  created_at: string;
}

export interface Contract {
  id: string;
  contract_number: string;
  title: string;
  customer_id: string;
  customer_name: string;
  contract_type: string;
  status: string;
  start_date: string;
  end_date: string | null;
  total_value: number;
  currency: string;
  created_at: string;
}

export interface WorkOrder {
  id: string;
  work_order_number: string;
  title: string;
  customer_name: string;
  contract_id: string | null;
  status: string;
  priority: string;
  assigned_technician_id: string | null;
  scheduled_date: string | null;
  completed_date: string | null;
  created_at: string;
}

export interface Technician {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  phone: string | null;
  status: string;
  specializations: string[];
  service_area: string | null;
  is_available: boolean;
  certifications_count: number;
  created_at: string;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_name: string;
  status: string;
  total_amount: number;
  amount_paid: number;
  amount_due: number;
  currency: string;
  due_date: string | null;
  created_at: string;
}

export interface Certificate {
  id: string;
  certificate_number: string;
  title: string;
  customer_name: string;
  certificate_type: string;
  status: string;
  issued_date: string | null;
  expiry_date: string | null;
  issued_by: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── CRM (Customers) ───────────────────────────────────────────────────────

export const customersApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Customer>>("/crm/customers", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Customer>(`/crm/customers/${id}`).then((r) => r.data),

  create: (data: { company_name: string; industry?: string; email?: string; phone?: string }) =>
    apiClient.post<Customer>("/crm/customers", data).then((r) => r.data),

  update: (id: string, data: Partial<Customer>) =>
    apiClient.patch<Customer>(`/crm/customers/${id}`, data).then((r) => r.data),
};

// ─── Contracts ──────────────────────────────────────────────────────────────

export const contractsApi = {
  list: (params?: { search?: string; status?: string; contract_type?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Contract>>("/contracts/contracts", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Contract>(`/contracts/contracts/${id}`).then((r) => r.data),

  create: (data: { title: string; customer_id: string; contract_type: string; start_date: string; total_value: number }) =>
    apiClient.post<Contract>("/contracts/contracts", data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    apiClient.post<Contract>(`/contracts/contracts/${id}/transition`, data).then((r) => r.data),
};

// ─── Work Orders ────────────────────────────────────────────────────────────

export const workOrdersApi = {
  list: (params?: { search?: string; status?: string; priority?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<WorkOrder>>("/work-orders/work-orders", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<WorkOrder>(`/work-orders/work-orders/${id}`).then((r) => r.data),

  create: (data: { title: string; customer_id: string; priority: string; scheduled_date?: string }) =>
    apiClient.post<WorkOrder>("/work-orders/work-orders", data).then((r) => r.data),

  assign: (id: string, data: { technician_id: string }) =>
    apiClient.post<WorkOrder>(`/work-orders/work-orders/${id}/assign`, data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    apiClient.post<WorkOrder>(`/work-orders/work-orders/${id}/transition`, data).then((r) => r.data),
};

// ─── Technicians ────────────────────────────────────────────────────────────

export const techniciansApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Technician>>("/technicians/technicians", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Technician>(`/technicians/technicians/${id}`).then((r) => r.data),

  create: (data: { first_name: string; last_name: string; email: string; specializations: string[] }) =>
    apiClient.post<Technician>("/technicians/technicians", data).then((r) => r.data),

  updateAvailability: (id: string, data: { is_available: boolean }) =>
    apiClient.patch<Technician>(`/technicians/technicians/${id}/availability`, data).then((r) => r.data),
};

// ─── Billing (Invoices) ─────────────────────────────────────────────────────

export const invoicesApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Invoice>>("/billing/invoices", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Invoice>(`/billing/invoices/${id}`).then((r) => r.data),

  create: (data: { customer_id: string; work_order_id?: string; due_date?: string }) =>
    apiClient.post<Invoice>("/billing/invoices", data).then((r) => r.data),

  recordPayment: (id: string, data: { amount: number; payment_method: string; reference?: string }) =>
    apiClient.post<Invoice>(`/billing/invoices/${id}/payments`, data).then((r) => r.data),

  transition: (id: string, data: { action: string }) =>
    apiClient.post<Invoice>(`/billing/invoices/${id}/transition`, data).then((r) => r.data),
};

// ─── Certificates ───────────────────────────────────────────────────────────

export const certificatesApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Certificate>>("/certificates/certificates", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Certificate>(`/certificates/certificates/${id}`).then((r) => r.data),

  create: (data: { title: string; customer_id: string; certificate_type: string }) =>
    apiClient.post<Certificate>("/certificates/certificates", data).then((r) => r.data),

  issue: (id: string) =>
    apiClient.post<Certificate>(`/certificates/certificates/${id}/issue`).then((r) => r.data),
};
