import {
  qmsApiClient,
  qmsCapaApiClient,
  qmsEquipmentApiClient,
  qmsQualityEventApiClient,
  qmsTrainingApiClient,
} from "../qms-client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Document {
  id: string;
  doc_number: string;
  title: string;
  doc_type: string;
  status: string;
  current_version: string;
  created_at: string;
  updated_at: string;
}

type SuccessEnvelope<T> = { success: boolean; data: T };
type PaginatedEnvelope<T> = {
  success: boolean;
  data: T[];
  pagination: { page: number; page_size: number; total: number };
};

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
  tenant_id: string;
  course_code: string;
  title: string;
  description: string | null;
  course_type: string;
  department: string | null;
  document_id: string | null;
  duration_hours: number | null;
  passing_score: number;
  requires_certification: boolean;
  recurrence_days: number | null;
  is_mandatory: boolean;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
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
    doc_number: dto.doc_number,
    title: dto.title,
    doc_type: dto.doc_type,
    status: dto.status,
    current_version: dto.current_version,
    created_at: dto.created_at,
    updated_at: dto.updated_at,
  };
}

function normalizePaginated<T>(raw: unknown, mapper?: (v: unknown) => T): PaginatedResponse<T> {
  const value = raw as any;

  if (value && typeof value === "object" && Array.isArray(value.items)) {
    return {
      items: (mapper ? value.items.map(mapper) : value.items) as T[],
      total: Number(value.total ?? value.items.length ?? 0),
      page: Number(value.page ?? 1),
      page_size: Number(value.page_size ?? value.items.length ?? 0),
    };
  }

  if (value && typeof value === "object" && Array.isArray(value.data) && value.pagination) {
    return {
      items: (mapper ? value.data.map(mapper) : value.data) as T[],
      total: Number(value.pagination.total ?? value.data.length ?? 0),
      page: Number(value.pagination.page ?? 1),
      page_size: Number(value.pagination.page_size ?? value.data.length ?? 0),
    };
  }

  return { items: [], total: 0, page: 1, page_size: 0 };
}

// ─── Documents ──────────────────────────────────────────────────────────────

export const documentsApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    qmsApiClient
      .get<PaginatedResponse<DocumentDto> | PaginatedEnvelope<DocumentDto>>("/documents", { params })
      .then((r) => normalizePaginated<Document>(r.data, (v) => mapDocument(v as DocumentDto))),

  get: (id: string) =>
    qmsApiClient
      .get<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}`)
      .then((r) => ("data" in (r.data as any) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  create: (data: {
    doc_number: string;
    title: string;
    doc_type: string;
    description?: string;
    department?: string;
    tags?: string[];
    regulatory_frameworks?: string[];
    file_id?: string;
  }) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>("/documents", {
        doc_number: data.doc_number,
        title: data.title,
        doc_type: data.doc_type,
        description: data.description,
        department: data.department,
        tags: data.tags,
        regulatory_frameworks: data.regulatory_frameworks,
        file_id: data.file_id,
      })
      .then((r) => ("data" in (r.data as any) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  submitForReview: (id: string, data?: { approver_id?: string; comment?: string }) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/submit-for-review`, data ?? {})
      .then((r) => ("data" in (r.data as any) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  approve: (id: string, data: { signature: string; comments?: string }) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/approve`, {
        signature: data.signature,
        comment: data.comments,
      })
      .then((r) => ("data" in (r.data as any) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),
};

// ─── Quality Events ─────────────────────────────────────────────────────────

export const qualityEventsApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    qmsQualityEventApiClient.get<PaginatedResponse<QualityEvent>>("/quality-events/events", { params }).then((r) => r.data),

  get: (id: string) =>
    qmsQualityEventApiClient.get<QualityEvent>(`/quality-events/events/${id}`).then((r) => r.data),

  create: (data: { title: string; event_type: string; severity: string; description?: string }) =>
    qmsQualityEventApiClient.post<QualityEvent>("/quality-events/events", data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    qmsQualityEventApiClient.post<QualityEvent>(`/quality-events/events/${id}/transition`, data).then((r) => r.data),
};

// ─── CAPA ───────────────────────────────────────────────────────────────────

export const capaApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    qmsCapaApiClient.get<PaginatedResponse<CAPA>>("/capa/capas", { params }).then((r) => r.data),

  get: (id: string) =>
    qmsCapaApiClient.get<CAPA>(`/capa/capas/${id}`).then((r) => r.data),

  create: (data: { title: string; capa_type: string; priority: string; description?: string }) =>
    qmsCapaApiClient.post<CAPA>("/capa/capas", data).then((r) => r.data),

  transition: (id: string, data: { action: string; comments?: string }) =>
    qmsCapaApiClient.post<CAPA>(`/capa/capas/${id}/transition`, data).then((r) => r.data),
};

// ─── Training ───────────────────────────────────────────────────────────────

export const trainingApi = {
  list: (params?: { page?: number; page_size?: number; department?: string; is_mandatory?: boolean }) =>
    qmsTrainingApiClient
      .get<PaginatedEnvelope<Course>>("/training/courses", { params })
      .then((r) => ({
        items: r.data.data,
        total: r.data.pagination.total,
        page: r.data.pagination.page,
        page_size: r.data.pagination.page_size,
      })),

  get: (id: string) =>
    qmsTrainingApiClient.get<SuccessEnvelope<Course>>(`/training/courses/${id}`).then((r) => r.data.data),

  create: (data: {
    course_code: string;
    title: string;
    course_type?: string;
    description?: string;
    department?: string;
    document_id?: string | null;
    duration_hours?: number | null;
    passing_score?: number;
    requires_certification?: boolean;
    recurrence_days?: number | null;
    is_mandatory?: boolean;
  }) =>
    qmsTrainingApiClient
      .post<SuccessEnvelope<Course>>("/training/courses", {
        course_code: data.course_code,
        title: data.title,
        course_type: data.course_type ?? "online",
        description: data.description ?? null,
        department: data.department ?? null,
        document_id: data.document_id ?? null,
        duration_hours: data.duration_hours ?? null,
        passing_score: data.passing_score ?? 80,
        requires_certification: data.requires_certification ?? false,
        recurrence_days: data.recurrence_days ?? null,
        is_mandatory: data.is_mandatory ?? false,
      })
      .then((r) => r.data.data),
};

// ─── Equipment ──────────────────────────────────────────────────────────────

export const equipmentApi = {
  list: (params?: { search?: string; status?: string; page?: number; page_size?: number }) =>
    qmsEquipmentApiClient.get<PaginatedResponse<Equipment>>("/equipment/assets", { params }).then((r) => r.data),

  get: (id: string) =>
    qmsEquipmentApiClient.get<Equipment>(`/equipment/assets/${id}`).then((r) => r.data),

  create: (data: { name: string; equipment_type: string; manufacturer: string; model: string; serial_number: string }) =>
    qmsEquipmentApiClient.post<Equipment>("/equipment/assets", data).then((r) => r.data),
};
