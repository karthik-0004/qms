import { apiClient } from "../client";

function tempRef(prefix: string): string {
  try {
    return `${prefix}-${crypto.randomUUID().slice(0, 8)}`;
  } catch {
    return `${prefix}-${Date.now().toString(36)}`;
  }
}

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Customer {
  id: string;
  company_name: string;
  status: string;
  industry: string | null;
  website: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  city: string | null;
  state: string | null;
  country: string | null;
  postal_code: string | null;
  notes: string | null;
  tags: string[];
  contact_count: number;
  created_at: string;
  updated_at: string;
}

export interface Contract {
  id: string;
  contract_number: string;
  title: string;
  customer_id: string;
  contract_type: string;
  status: string;
  description: string | null;
  start_date: string | null;
  end_date: string | null;
  total_value: number | null;
  currency: string;
  payment_terms: string | null;
  notes: string | null;
  approved_at: string | null;
  approved_by: string | null;
  signed_at: string | null;
  signed_by: string | null;
  terminated_at: string | null;
  termination_reason: string | null;
  created_at: string;
  updated_at: string;
  customer?: Customer;
}

export interface WorkOrder {
  id: string;
  work_order_number: string;
  title: string;
  customer_id: string;
  contract_id: string | null;
  status: string;
  priority: string;
  work_type: string;
  description: string | null;
  assigned_technician_id: string | null;
  scheduled_start: string | null;
  scheduled_end: string | null;
  actual_start: string | null;
  actual_end: string | null;
  estimated_hours: number | null;
  actual_hours: number | null;
  site_address: string | null;
  site_city: string | null;
  site_state: string | null;
  site_postal_code: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
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
  tenant_id: string;
  customer_id: string;
  contract_id: string | null;
  work_order_id: string | null;
  invoice_number: string;
  status: string;
  subtotal: number;
  tax_amount: number;
  total_amount: number;
  amount_paid: number;
  amount_due: number;
  currency: string;
  tax_rate: number;
  due_date: string | null;
  paid_at: string | null;
  notes: string | null;
  payment_terms: string | null;
  created_at: string;
  updated_at: string;
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

export interface ContractLineItem {
  id: string;
  contract_id: string;
  description: string;
  unit_price: number;
  quantity: number;
  unit: string | null;
  total_price: number;
  sort_order: number;
  created_at: string;
}

export interface CreateLineItemRequest {
  description: string;
  unit_price: number;
  quantity: number;
  unit?: string | null;
  sort_order?: number;
}

export interface ContractHistoryEntry {
  id: string;
  contract_id: string;
  from_status: string | null;
  to_status: string;
  changed_by: string;
  comment: string | null;
  created_at: string;
}

export interface CustomerContact {
  id: string;
  tenant_id: string;
  customer_id: string;
  first_name: string;
  last_name: string;
  title: string | null;
  email: string | null;
  phone: string | null;
  mobile: string | null;
  is_primary: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateContactRequest {
  first_name: string;
  last_name: string;
  email?: string | null;
  phone?: string | null;
  mobile?: string | null;
  title?: string | null;
  is_primary?: boolean;
}

export interface CustomerInteraction {
  id: string;
  tenant_id: string;
  customer_id: string;
  interaction_type: string;
  subject: string;
  body: string | null;
  contact_id: string | null;
  created_by: string;
  created_at: string;
}

export interface CreateInteractionRequest {
  interaction_type: string;
  subject: string;
  body?: string | null;
  contact_id?: string | null;
  scheduled_at?: string | null;
  duration_minutes?: number | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

/** CCV list handlers return arrays; coerce to PaginatedResponse for TanStack Query. */
function listPaging(params?: { page?: number; page_size?: number }) {
  const page_size = params?.page_size ?? 50;
  const page = params?.page ?? 1;
  return { skip: (page - 1) * page_size, limit: page_size, page, page_size };
}

function coerceListPage<T>(rows: unknown, page: number, page_size: number): PaginatedResponse<T> {
  if (
    typeof rows === "object" &&
    rows !== null &&
    Array.isArray((rows as PaginatedResponse<T>).items) &&
    typeof (rows as PaginatedResponse<T>).total === "number"
  ) {
    return rows as PaginatedResponse<T>;
  }
  const items = Array.isArray(rows) ? (rows as T[]) : [];
  const hasMore = items.length === page_size;
  const total =
    hasMore ? page * page_size + 1 : (page - 1) * page_size + items.length;
  return { items, total, page, page_size };
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

  // Contacts
  listContacts: (customerId: string) =>
    apiClient.get<CustomerContact[]>(`/crm/customers/${customerId}/contacts`).then((r) => r.data),

  addContact: (customerId: string, data: CreateContactRequest) =>
    apiClient.post<CustomerContact>(`/crm/customers/${customerId}/contacts`, data).then((r) => r.data),

  // Interactions
  listInteractions: (customerId: string) =>
    apiClient.get<CustomerInteraction[]>(`/crm/customers/${customerId}/interactions`).then((r) => r.data),

  logInteraction: (customerId: string, data: CreateInteractionRequest) =>
    apiClient.post<CustomerInteraction>(`/crm/customers/${customerId}/interactions`, data).then((r) => r.data),

  // Status transition
  transitionStatus: (customerId: string, data: { new_status: string }) =>
    apiClient.post<Customer>(`/crm/customers/${customerId}/status`, data).then((r) => r.data),
};

// ─── Contracts ──────────────────────────────────────────────────────────────

export const contractsApi = {
  list: async (
    params?: {
      search?: string;
      status?: string;
      contract_type?: string;
      customer_id?: string;
      page?: number;
      page_size?: number;
    },
  ) => {
    const { skip, limit, page, page_size } = listPaging(params);
    const { data } = await apiClient.get<unknown>("/contracts", {
      params: {
        skip,
        limit,
        status: params?.status ?? undefined,
        customer_id: params?.customer_id ?? undefined,
      },
    });
    return coerceListPage<Contract>(data, page, page_size);
  },

  get: (id: string) =>
    apiClient.get<Contract>(`/contracts/${id}`).then((r) => r.data),

  create: (data: {
    title: string;
    customer_id: string;
    contract_type: string;
    contract_number?: string;
    description?: string | null;
    start_date?: string | null;
    end_date?: string | null;
    total_value?: number | null;
    currency?: string;
    payment_terms?: string | null;
    notes?: string | null;
  }) =>
    apiClient.post<Contract>("/contracts", {
      ...data,
      contract_number: data.contract_number ?? tempRef("CNT"),
      currency: data.currency ?? "USD",
    }).then((r) => r.data),

  /** Maps UI `action` to API `new_status`. */
  transition: (id: string, data: { action: string; comments?: string }) =>
    apiClient
      .post<Contract>(`/contracts/${id}/status`, {
        new_status: data.action,
        comment: data.comments,
      })
      .then((r) => r.data),

  // Line Items
  listLineItems: (contractId: string) =>
    apiClient.get<ContractLineItem[]>(`/contracts/${contractId}/line-items`).then((r) => r.data),

  addLineItem: (contractId: string, data: CreateLineItemRequest) =>
    apiClient.post<ContractLineItem>(`/contracts/${contractId}/line-items`, data).then((r) => r.data),

  // History
  getHistory: (contractId: string) =>
    apiClient.get<ContractHistoryEntry[]>(`/contracts/${contractId}/history`).then((r) => r.data),
};

// ─── Work Orders ────────────────────────────────────────────────────────────

export const workOrdersApi = {
  list: async (
    params?: {
      search?: string;
      status?: string;
      priority?: string;
      customer_id?: string;
      technician_id?: string;
      page?: number;
      page_size?: number;
    },
  ) => {
    const { skip, limit, page, page_size } = listPaging(params);
    const { data } = await apiClient.get<unknown>("/workorders", {
      params: {
        skip,
        limit,
        status: params?.status ?? undefined,
        customer_id: params?.customer_id ?? undefined,
        technician_id: params?.technician_id ?? undefined,
      },
    });
    return coerceListPage<WorkOrder>(data, page, page_size);
  },

  get: (id: string) =>
    apiClient.get<WorkOrder>(`/workorders/${id}`).then((r) => r.data),

  create: (data: {
    title: string;
    customer_id: string;
    work_order_number?: string;
    work_type?: string;
    description?: string | null;
    priority?: string;
    contract_id?: string | null;
    site_address?: string | null;
    site_city?: string | null;
    site_state?: string | null;
    site_postal_code?: string | null;
    scheduled_start?: string | null;
    scheduled_end?: string | null;
    estimated_hours?: number | null;
    notes?: string | null;
  }) =>
    apiClient.post<WorkOrder>("/workorders", {
      work_order_number: data.work_order_number ?? tempRef("WO"),
      title: data.title,
      customer_id: data.customer_id,
      priority: data.priority ?? "normal",
      work_type: data.work_type ?? "other",
      scheduled_start: data.scheduled_start,
      scheduled_end: data.scheduled_end,
      contract_id: data.contract_id,
      description: data.description,
      site_address: data.site_address,
      site_city: data.site_city,
      site_state: data.site_state,
      site_postal_code: data.site_postal_code,
      estimated_hours: data.estimated_hours,
      notes: data.notes,
    }).then((r) => r.data),

  assign: (id: string, data: { technician_id: string }) =>
    apiClient.post<WorkOrder>(`/workorders/${id}/assign`, data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    apiClient
      .post<WorkOrder>(`/workorders/${id}/status`, {
        new_status: data.action,
        comment: data.comments,
      })
      .then((r) => r.data),
};

// ─── Technicians ────────────────────────────────────────────────────────────

export const techniciansApi = {
  list: async (params?: { search?: string; status?: string; page?: number; page_size?: number }) => {
    const { skip, limit, page, page_size } = listPaging(params);
    const { data } = await apiClient.get<unknown>("/technicians", {
      params: {
        skip,
        limit,
        status: params?.status ?? undefined,
      },
    });
    return coerceListPage<Technician>(data, page, page_size);
  },

  get: (id: string) =>
    apiClient.get<Technician>(`/technicians/${id}`).then((r) => r.data),

  create: (data: {
    user_id: string;
    first_name: string;
    last_name: string;
    email: string;
    specializations: string[];
    employee_number?: string;
    phone?: string;
    service_area?: string;
  }) =>
    apiClient.post<Technician>("/technicians", {
      ...data,
      employee_number: data.employee_number ?? tempRef("EMP"),
    }).then((r) => r.data),

  updateAvailability: (id: string, data: { is_available: boolean }) =>
    apiClient.post<Technician>(`/technicians/${id}/availability`, data).then((r) => r.data),
};

// ─── Billing (Invoices) ─────────────────────────────────────────────────────

export const invoicesApi = {
  list: async (
    params?: {
      search?: string;
      status?: string;
      customer_id?: string;
      page?: number;
      page_size?: number;
    },
  ) => {
    const { skip, limit, page, page_size } = listPaging(params);
    const { data } = await apiClient.get<unknown>("/invoices", {
      params: {
        skip,
        limit,
        status: params?.status ?? undefined,
        customer_id: params?.customer_id ?? undefined,
      },
    });
    return coerceListPage<Invoice>(data, page, page_size);
  },

  get: (id: string) =>
    apiClient.get<Invoice>(`/invoices/${id}`).then((r) => r.data),

  create: (data: {
    customer_id: string;
    contract_id?: string | null;
    work_order_id?: string | null;
    invoice_number?: string;
    due_date?: string | null;
    currency?: string;
    tax_rate?: number;
    notes?: string | null;
    payment_terms?: string | null;
  }) =>
    apiClient.post<Invoice>("/invoices", {
      ...data,
      invoice_number: data.invoice_number ?? tempRef("INV"),
      currency: data.currency ?? "USD",
      tax_rate: data.tax_rate ?? 0,
    }).then((r) => r.data),

  recordPayment: (id: string, data: { amount: number; payment_method: string; reference?: string }) =>
    apiClient
      .post<Invoice>(`/invoices/${id}/payments`, {
        amount: data.amount,
        payment_method: data.payment_method,
        reference_number: data.reference,
      })
      .then((r) => r.data),

  transition: (id: string, data: { action: string }) =>
    apiClient
      .post<Invoice>(`/invoices/${id}/status`, { new_status: data.action })
      .then((r) => r.data),
};

// ─── Certificates ───────────────────────────────────────────────────────────
// No certificate-service deployment in compose yet — paths unchanged for future upstream.

export const certificatesApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Certificate>>("/certificates/certificates", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Certificate>(`/certificates/certificates/${id}`).then((r) => r.data),

  create: (data: { 
    title: string; 
    certificate_number: string; 
    certificate_type: string; 
    customer_id: string; 
    issue_date: string; 
    expiry_date?: string; 
    description?: string; 
  }) =>
    apiClient.post<Certificate>("/certificates/certificates", data).then((r) => r.data),

  issue: (id: string) =>
    apiClient.post<Certificate>(`/certificates/certificates/${id}/issue`).then((r) => r.data),
};
