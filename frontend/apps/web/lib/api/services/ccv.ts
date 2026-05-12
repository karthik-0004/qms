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
    start_date: string;
    total_value: number;
    contract_number?: string;
    currency?: string;
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
    priority: string;
    scheduled_date?: string;
    work_order_number?: string;
    work_type?: string;
  }) =>
    apiClient.post<WorkOrder>("/workorders", {
      work_order_number: data.work_order_number ?? tempRef("WO"),
      title: data.title,
      customer_id: data.customer_id,
      priority: data.priority ?? "normal",
      work_type: data.work_type ?? "other",
      scheduled_start: data.scheduled_date,
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
    first_name: string;
    last_name: string;
    email: string;
    specializations: string[];
    employee_number?: string;
  }) =>
    apiClient.post<Technician>("/technicians", {
      ...data,
      employee_number: data.employee_number ?? tempRef("EMP"),
      /** Platform user link not plumbed through UI yet; random UUID satisfies API shape. */
      user_id:
        typeof crypto !== "undefined" && crypto.randomUUID
          ? crypto.randomUUID()
          : "00000000-0000-4000-8000-000000000001",
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
    work_order_id?: string;
    due_date?: string;
    invoice_number?: string;
  }) =>
    apiClient.post<Invoice>("/invoices", {
      ...data,
      invoice_number: data.invoice_number ?? tempRef("INV"),
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

  create: (data: { title: string; customer_id: string; certificate_type: string }) =>
    apiClient.post<Certificate>("/certificates/certificates", data).then((r) => r.data),

  issue: (id: string) =>
    apiClient.post<Certificate>(`/certificates/certificates/${id}/issue`).then((r) => r.data),
};
