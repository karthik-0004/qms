import { apiClient } from "../client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Document {
  id: string;
  document_number: string;
  title: string;
  doc_type: string;
  status: string;
  version: string;
  author_id: string;
  created_at: string;
  updated_at: string;
}

export interface QualityEvent {
  id: string;
  event_number: string;
  title: string;
  event_type: string;
  severity: string;
  status: string;
  reported_by: string;
  reported_at: string;
  department: string | null;
}

export interface CAPA {
  id: string;
  capa_number: string;
  title: string;
  capa_type: string;
  priority: string;
  status: string;
  source_event_id: string | null;
  assigned_to: string | null;
  due_date: string | null;
  created_at: string;
}

export interface Course {
  id: string;
  course_code: string;
  title: string;
  category: string;
  format: string;
  duration_hours: number;
  status: string;
  enrolled: number;
  completed: number;
  created_at: string;
}

export interface Equipment {
  id: string;
  asset_tag: string;
  name: string;
  equipment_type: string;
  manufacturer: string;
  model: string;
  serial_number: string;
  status: string;
  location: string | null;
  next_calibration: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

type ApiMeta = {
  request_id: string;
  timestamp: string;
  service?: string | null;
  version?: string | null;
};

type ApiSuccess<T> = {
  success: true;
  data: T;
  meta: ApiMeta;
};

type ApiPaginated<T> = {
  success: true;
  data: T[];
  pagination: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
    has_next: boolean;
    has_prev: boolean;
  };
  meta: ApiMeta;
};

type DocumentDto = {
  id: string;
  doc_number: string;
  title: string;
  doc_type: string;
  status: string;
  current_version: string;
  created_by: string;
  created_at: string;
  updated_at: string;
};

function mapDocument(dto: DocumentDto): Document {
  return {
    id: dto.id,
    document_number: dto.doc_number,
    title: dto.title,
    doc_type: dto.doc_type,
    status: dto.status,
    version: dto.current_version,
    author_id: dto.created_by,
    created_at: dto.created_at,
    updated_at: dto.updated_at,
  };
}

// ─── Documents ──────────────────────────────────────────────────────────────

export const documentsApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient
      .get<ApiPaginated<DocumentDto>>("/documents", { params })
      .then((r) => ({
        items: r.data.data.map(mapDocument),
        total: r.data.pagination.total,
        page: r.data.pagination.page,
        page_size: r.data.pagination.page_size,
      })),

  get: (id: string) =>
    apiClient.get<ApiSuccess<DocumentDto>>(`/documents/${id}`).then((r) => mapDocument(r.data.data)),

  create: (data: { title: string; doc_type: string; content?: string }) =>
    apiClient
      .post<ApiSuccess<DocumentDto>>("/documents", {
        title: data.title,
        doc_type: data.doc_type,
        description: data.content,
      })
      .then((r) => mapDocument(r.data.data)),

  submit: (id: string) =>
    apiClient
      .post<ApiSuccess<DocumentDto>>(`/documents/${id}/submit-for-review`, {})
      .then((r) => mapDocument(r.data.data)),

  approve: (id: string, data: { signature: string; comments?: string }) =>
    apiClient
      .post<ApiSuccess<DocumentDto>>(`/documents/${id}/approve`, {
        signature: data.signature,
        comment: data.comments,
      })
      .then((r) => mapDocument(r.data.data)),
};

// ─── Quality Events ─────────────────────────────────────────────────────────

export const qualityEventsApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<QualityEvent>>("/quality-events/events", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<QualityEvent>(`/quality-events/events/${id}`).then((r) => r.data),

  create: (data: { title: string; event_type: string; severity: string; description?: string }) =>
    apiClient.post<QualityEvent>("/quality-events/events", data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    apiClient.post<QualityEvent>(`/quality-events/events/${id}/transition`, data).then((r) => r.data),
};

// ─── CAPA ───────────────────────────────────────────────────────────────────

export const capaApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<CAPA>>("/capa/capas", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<CAPA>(`/capa/capas/${id}`).then((r) => r.data),

  create: (data: { title: string; capa_type: string; priority: string; description?: string }) =>
    apiClient.post<CAPA>("/capa/capas", data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    apiClient.post<CAPA>(`/capa/capas/${id}/transition`, data).then((r) => r.data),
};

// ─── Training ───────────────────────────────────────────────────────────────

export const trainingApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Course>>("/training/courses", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Course>(`/training/courses/${id}`).then((r) => r.data),

  create: (data: { title: string; category: string; format: string; duration_hours: number }) =>
    apiClient.post<Course>("/training/courses", data).then((r) => r.data),
};

// ─── Equipment ──────────────────────────────────────────────────────────────

export const equipmentApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Equipment>>("/equipment/assets", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Equipment>(`/equipment/assets/${id}`).then((r) => r.data),

  create: (data: { name: string; equipment_type: string; manufacturer: string; model: string; serial_number: string }) =>
    apiClient.post<Equipment>("/equipment/assets", data).then((r) => r.data),
};
