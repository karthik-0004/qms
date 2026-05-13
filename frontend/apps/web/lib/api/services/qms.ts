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
  description?: string | null;
  department?: string | null;
  owner_id?: string | null;
  approver_id?: string | null;
  effective_date?: string | null;
  review_date?: string | null;
  expiry_date?: string | null;
  file_id?: string | null;
  tags?: string[];
  regulatory_frameworks?: string[];
  is_controlled?: boolean;
  created_by?: string;
  last_rejection_reason?: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentVersion {
  id: string;
  document_id: string;
  version: string;
  file_id: string | null;
  change_summary: string | null;
  approved_by: string | null;
  approved_at: string | null;
  signature_hash: string | null;
  created_by: string;
  created_at: string;
}

export interface DocumentDistribution {
  id: string;
  document_id: string;
  user_id: string;
  added_by: string;
  created_at: string;
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
  description?: string;
  status: string;
  severity: string;
  priority?: string;
  department: string | null;
  location?: string | null;
  detected_at: string;
  detected_by?: string | null;
  assigned_to?: string | null;
  root_cause?: string | null;
  immediate_action?: string | null;
  capa_required?: boolean;
  capa_id?: string | null;
  due_date?: string | null;
  closed_at?: string | null;
  tags?: unknown[];
  created_by?: string;
  created_at: string;
  updated_at?: string;
  /** Alias for list views when API used different field names */
  reported_by?: string;
  reported_at?: string;
}

export interface QualityEventSummary {
  by_status: Record<string, number>;
  tenant_id: string;
}

export interface CAPA {
  id: string;
  capa_number: string;
  title: string;
  capa_type: string;
  severity: string;
  description?: string;
  status: string;
  source_type?: string | null;
  source_id?: string | null;
  /** @deprecated use source_id for linked quality events */
  source_event_id?: string | null;
  owner_id?: string | null;
  department?: string | null;
  root_cause?: string | null;
  root_cause_method?: string | null;
  due_date: string | null;
  target_close_date?: string | null;
  actual_close_date?: string | null;
  effectiveness_verified?: boolean;
  effectiveness_check_date?: string | null;
  tags?: unknown[];
  created_by?: string;
  created_at: string;
  updated_at?: string;
}

export interface CAPAAction {
  id: string;
  capa_id: string;
  action_type: string;
  description: string;
  assigned_to: string | null;
  due_date: string | null;
  status: string;
  completed_at: string | null;
  evidence: string | null;
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

export interface TrainingAssignment {
  id: string;
  tenant_id: string;
  course_id: string;
  course_title?: string | null;
  user_id: string;
  assigned_by: string | null;
  due_date: string | null;
  status: string;
  score: number | null;
  passed: boolean | null;
  completed_at: string | null;
  cert_expiry_date: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface Equipment {
  id: string;
  tenant_id?: string;
  asset_tag: string;
  name: string;
  description?: string | null;
  equipment_type: string;
  manufacturer: string | null;
  model: string | null;
  serial_number: string | null;
  status: string;
  location: string | null;
  department?: string | null;
  requires_calibration?: boolean;
  calibration_frequency_days?: number | null;
  last_calibration_date?: string | null;
  next_calibration_date?: string | null;
  /** Some gateways normalize to this alias */
  next_calibration?: string | null;
  requires_pm?: boolean;
  pm_frequency_days?: number | null;
  last_pm_date?: string | null;
  next_pm_date?: string | null;
  assigned_to?: string | null;
  notes?: string | null;
  tags?: unknown[];
  created_by?: string;
  created_at: string;
  updated_at?: string;
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
  description?: string | null;
  department?: string | null;
  owner_id?: string | null;
  approver_id?: string | null;
  effective_date?: string | null;
  review_date?: string | null;
  expiry_date?: string | null;
  file_id?: string | null;
  tags?: string[];
  regulatory_frameworks?: string[];
  is_controlled?: boolean;
  created_by?: string;
  last_rejection_reason?: string | null;
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
    description: dto.description,
    department: dto.department,
    owner_id: dto.owner_id,
    approver_id: dto.approver_id,
    effective_date: dto.effective_date,
    review_date: dto.review_date,
    expiry_date: dto.expiry_date,
    file_id: dto.file_id,
    tags: dto.tags,
    regulatory_frameworks: dto.regulatory_frameworks,
    is_controlled: dto.is_controlled,
    created_by: dto.created_by,
    last_rejection_reason: dto.last_rejection_reason,
    created_at: dto.created_at,
    updated_at: dto.updated_at,
  };
}

function normalizePaginated<T>(raw: unknown, mapper?: (v: unknown) => T): PaginatedResponse<T> {
  const value = raw as Record<string, unknown>;

  if (value && typeof value === "object" && Array.isArray(value.items)) {
    return {
      items: (mapper ? value.items.map(mapper) : value.items) as T[],
      total: Number(value.total ?? (value.items as unknown[]).length ?? 0),
      page: Number(value.page ?? 1),
      page_size: Number(value.page_size ?? (value.items as unknown[]).length ?? 0),
    };
  }

  if (value && typeof value === "object" && Array.isArray(value.data) && value.pagination) {
    const p = value.pagination as Record<string, unknown>;
    return {
      items: (mapper ? (value.data as unknown[]).map(mapper) : (value.data as T[])) as T[],
      total: Number(p.total ?? (value.data as unknown[]).length ?? 0),
      page: Number(p.page ?? 1),
      page_size: Number(p.page_size ?? (value.data as unknown[]).length ?? 0),
    };
  }

  return { items: [], total: 0, page: 1, page_size: 0 };
}

function unwrapSuccessData<T>(raw: unknown): T {
  if (raw && typeof raw === "object" && "data" in raw && (raw as SuccessEnvelope<T>).data !== undefined) {
    return (raw as SuccessEnvelope<T>).data;
  }
  return raw as T;
}

function mapCapaDto(raw: unknown): CAPA {
  const c = raw as Record<string, unknown>;
  return {
    id: String(c.id ?? ""),
    capa_number: String(c.capa_number ?? ""),
    title: String(c.title ?? ""),
    capa_type: String(c.capa_type ?? ""),
    severity: String(c.severity ?? c.priority ?? "major"),
    description: c.description !== undefined ? String(c.description) : undefined,
    status: String(c.status ?? ""),
    source_type: (c.source_type as string | null | undefined) ?? null,
    source_id: (c.source_id as string | null | undefined) ?? null,
    source_event_id: (c.source_event_id as string | null | undefined) ?? (c.source_id as string | null | undefined) ?? null,
    owner_id: (c.owner_id as string | null | undefined) ?? null,
    department: (c.department as string | null | undefined) ?? null,
    due_date: (c.due_date as string | null | undefined) ?? null,
    target_close_date: (c.target_close_date as string | null | undefined) ?? null,
    actual_close_date: (c.actual_close_date as string | null | undefined) ?? null,
    root_cause: (c.root_cause as string | null | undefined) ?? null,
    root_cause_method: (c.root_cause_method as string | null | undefined) ?? null,
    effectiveness_verified: typeof c.effectiveness_verified === "boolean" ? c.effectiveness_verified : undefined,
    effectiveness_check_date: (c.effectiveness_check_date as string | null | undefined) ?? null,
    tags: Array.isArray(c.tags) ? c.tags : undefined,
    created_by: c.created_by !== undefined ? String(c.created_by) : undefined,
    created_at: String(c.created_at ?? ""),
    updated_at: c.updated_at !== undefined ? String(c.updated_at) : undefined,
  };
}

function mapQualityEventDto(raw: unknown): QualityEvent {
  const e = raw as Record<string, unknown>;
  const detectedAt = String(e.detected_at ?? e.reported_at ?? "");
  const detectedBy = (e.detected_by ?? e.reported_by ?? e.created_by) as string | undefined;
  return {
    id: String(e.id ?? ""),
    event_number: String(e.event_number ?? ""),
    title: String(e.title ?? ""),
    event_type: String(e.event_type ?? ""),
    description: e.description !== undefined ? String(e.description) : undefined,
    status: String(e.status ?? ""),
    severity: String(e.severity ?? ""),
    priority: e.priority !== undefined ? String(e.priority) : undefined,
    department: (e.department as string | null | undefined) ?? null,
    location: (e.location as string | null | undefined) ?? null,
    detected_at: detectedAt,
    detected_by: detectedBy !== undefined ? String(detectedBy) : null,
    assigned_to: (e.assigned_to as string | null | undefined) ?? null,
    root_cause: (e.root_cause as string | null | undefined) ?? null,
    immediate_action: (e.immediate_action as string | null | undefined) ?? null,
    capa_required: typeof e.capa_required === "boolean" ? e.capa_required : undefined,
    capa_id: (e.capa_id as string | null | undefined) ?? null,
    due_date: (e.due_date as string | null | undefined) ?? null,
    closed_at: (e.closed_at as string | null | undefined) ?? null,
    tags: Array.isArray(e.tags) ? (e.tags as unknown[]) : undefined,
    created_by: e.created_by !== undefined ? String(e.created_by) : undefined,
    created_at: String(e.created_at ?? ""),
    updated_at: e.updated_at !== undefined ? String(e.updated_at) : undefined,
    reported_by: detectedBy !== undefined ? String(detectedBy) : undefined,
    reported_at: detectedAt || undefined,
  };
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
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

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
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  submitForReview: (id: string, data?: { approver_id?: string; comment?: string }) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/submit-for-review`, data ?? {})
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  approve: (id: string, data: { signature: string; comments?: string; effective_date?: string; review_date?: string }) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/approve`, {
        signature: data.signature,
        comment: data.comments,
        effective_date: data.effective_date,
        review_date: data.review_date,
      })
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  update: (
    id: string,
    data: Partial<{
      title: string;
      description: string | null;
      department: string | null;
      owner_id: string | null;
      approver_id: string | null;
      tags: string[];
      regulatory_frameworks: string[];
      file_id: string | null;
    }>,
  ) =>
    qmsApiClient
      .patch<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}`, data)
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  reject: (id: string, data: { reason: string }) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/reject`, data)
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  makeObsolete: (id: string) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/make-obsolete`, {})
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  getVersions: (id: string) =>
    qmsApiClient.get<unknown>(`/documents/${id}/versions`).then((r) => unwrapSuccessData<DocumentVersion[]>(r.data)),

  dueForReview: (params?: { days_ahead?: number }) =>
    qmsApiClient
      .get<unknown>("/documents/due-for-review", { params })
      .then((r) => (unwrapSuccessData<DocumentDto[]>(r.data) as DocumentDto[]).map(mapDocument)),

  listDistribution: (id: string) =>
    qmsApiClient.get<unknown>(`/documents/${id}/distribution`).then((r) => unwrapSuccessData<DocumentDistribution[]>(r.data)),

  addDistributionMember: (id: string, data: { user_id: string }) =>
    qmsApiClient
      .post<unknown>(`/documents/${id}/distribution`, data)
      .then((r) => unwrapSuccessData<DocumentDistribution>(r.data)),
};

// ─── Quality Events ─────────────────────────────────────────────────────────

export const qualityEventsApi = {
  list: (params?: {
    search?: string;
    status?: string;
    event_type?: string;
    severity?: string;
    assigned_to?: string;
    department?: string;
    page?: number;
    page_size?: number;
  }) =>
    qmsQualityEventApiClient
      .get<unknown>("/quality-events", { params })
      .then((r) => normalizePaginated<QualityEvent>(r.data, mapQualityEventDto)),

  get: (id: string) =>
    qmsQualityEventApiClient
      .get<unknown>(`/quality-events/${id}`)
      .then((r) => mapQualityEventDto(unwrapSuccessData(r.data))),

  summary: () =>
    qmsQualityEventApiClient.get<unknown>("/quality-events/summary").then((r) => unwrapSuccessData<QualityEventSummary>(r.data)),

  create: (data: {
    event_number: string;
    title: string;
    event_type: string;
    description: string;
    detected_at: string;
    severity?: string;
    priority?: string;
    department?: string | null;
    location?: string | null;
    assigned_to?: string | null;
    immediate_action?: string | null;
    capa_required?: boolean;
    due_date?: string | null;
    tags?: string[];
  }) =>
    qmsQualityEventApiClient
      .post<unknown>("/quality-events", data)
      .then((r) => mapQualityEventDto(unwrapSuccessData(r.data))),

  update: (id: string, data: Record<string, unknown>) =>
    qmsQualityEventApiClient.patch<unknown>(`/quality-events/${id}`, data).then((r) => mapQualityEventDto(unwrapSuccessData(r.data))),

  close: (id: string, data?: { resolution?: string | null }) =>
    qmsQualityEventApiClient
      .post<unknown>(`/quality-events/${id}/close`, data ?? {})
      .then((r) => mapQualityEventDto(unwrapSuccessData(r.data))),

  delete: (id: string) => qmsQualityEventApiClient.delete<unknown>(`/quality-events/${id}`).then((r) => unwrapSuccessData<{ message: string }>(r.data)),
};

// ─── CAPA ───────────────────────────────────────────────────────────────────

export const capaApi = {
  list: (params?: {
    status?: string;
    severity?: string;
    owner_id?: string;
    department?: string;
    overdue_only?: boolean;
    page?: number;
    page_size?: number;
  }) =>
    qmsCapaApiClient.get<unknown>("/capas", { params }).then((r) => normalizePaginated<CAPA>(r.data, mapCapaDto)),

  get: (id: string) => qmsCapaApiClient.get<unknown>(`/capas/${id}`).then((r) => mapCapaDto(unwrapSuccessData(r.data))),

  create: (data: {
    capa_number: string;
    title: string;
    description: string;
    capa_type?: string;
    severity?: string;
    source_type?: string | null;
    source_id?: string | null;
    owner_id?: string | null;
    department?: string | null;
    due_date?: string | null;
    tags?: string[];
  }) =>
    qmsCapaApiClient
      .post<unknown>("/capas", {
        capa_number: data.capa_number,
        title: data.title,
        description: data.description,
        capa_type: data.capa_type ?? "corrective",
        severity: data.severity ?? "major",
        source_type: data.source_type,
        source_id: data.source_id,
        owner_id: data.owner_id,
        department: data.department,
        due_date: data.due_date,
        tags: data.tags ?? [],
      })
      .then((r) => mapCapaDto(unwrapSuccessData(r.data))),

  update: (id: string, data: Partial<{
    title: string;
    description: string;
    severity: string;
    owner_id: string | null;
    department: string | null;
    root_cause: string | null;
    root_cause_method: string | null;
    due_date: string | null;
    target_close_date: string | null;
    tags: string[] | null;
  }>) =>
    qmsCapaApiClient.patch<unknown>(`/capas/${id}`, data).then((r) => mapCapaDto(unwrapSuccessData(r.data))),

  /** Backend route: `POST /capas/{id}/close` (not PATCH). */
  close: (id: string) =>
    qmsCapaApiClient.post<unknown>(`/capas/${id}/close`, {}).then((r) => mapCapaDto(unwrapSuccessData(r.data))),

  delete: (id: string) =>
    qmsCapaApiClient
      .delete<unknown>(`/capas/${id}`)
      .then((r) => unwrapSuccessData<{ message: string }>(r.data)),

  verifyEffectiveness: (id: string, data: { verified: boolean; notes?: string | null }) =>
    qmsCapaApiClient
      .post<unknown>(`/capas/${id}/verify-effectiveness`, data)
      .then((r) => mapCapaDto(unwrapSuccessData(r.data))),

  listActions: (capaId: string) =>
    qmsCapaApiClient.get<unknown>(`/capas/${capaId}/actions`).then((r) => unwrapSuccessData<CAPAAction[]>(r.data)),

  addAction: (
    capaId: string,
    data: { action_type: string; description: string; assigned_to?: string | null; due_date?: string | null },
  ) =>
    qmsCapaApiClient.post<unknown>(`/capas/${capaId}/actions`, data).then((r) => unwrapSuccessData<CAPAAction>(r.data)),

  completeAction: (capaId: string, actionId: string, data?: { evidence?: string | null }) =>
    qmsCapaApiClient
      .post<unknown>(`/capas/${capaId}/actions/${actionId}/complete`, data ?? {})
      .then((r) => unwrapSuccessData<CAPAAction>(r.data)),
};

// ─── Training ───────────────────────────────────────────────────────────────

export const trainingApi = {
  list: (params?: { page?: number; page_size?: number; department?: string; is_mandatory?: boolean }) =>
    qmsTrainingApiClient.get<unknown>("/training/courses", { params }).then((r) => normalizePaginated<Course>(r.data)),

  get: (id: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/courses/${id}`).then((r) => unwrapSuccessData<Course>(r.data)),

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
      .post<unknown>("/training/courses", {
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
      .then((r) => unwrapSuccessData<Course>(r.data)),

  assign: (courseId: string, data: { user_id: string; due_date?: string | null }) =>
    qmsTrainingApiClient
      .post<unknown>(`/training/courses/${courseId}/assign`, data)
      .then((r) => unwrapSuccessData<TrainingAssignment>(r.data)),

  listMyAssignments: (params?: { page?: number; page_size?: number; status?: string }) =>
    qmsTrainingApiClient
      .get<unknown>("/training/assignments", { params })
      .then((r) => normalizePaginated<TrainingAssignment>(r.data)),

  completeAssignment: (assignmentId: string, data: { score?: number | null; notes?: string | null; e_signature?: string | null }) =>
    qmsTrainingApiClient
      .post<unknown>(`/training/assignments/${assignmentId}/complete`, data)
      .then((r) => unwrapSuccessData<TrainingAssignment>(r.data)),

  listOverdueAssignments: () =>
    qmsTrainingApiClient.get<unknown>("/training/assignments/overdue").then((r) => unwrapSuccessData<TrainingAssignment[]>(r.data)),
};

// ─── Equipment ──────────────────────────────────────────────────────────────

export const equipmentApi = {
  list: (params?: {
    status?: string;
    equipment_type?: string;
    department?: string;
    requires_calibration?: boolean;
    page?: number;
    page_size?: number;
  }) =>
    qmsEquipmentApiClient.get<unknown>("/equipment", { params }).then((r) => normalizePaginated<Equipment>(r.data)),

  get: (id: string) =>
    qmsEquipmentApiClient.get<unknown>(`/equipment/${id}`).then((r) => unwrapSuccessData<Equipment>(r.data)),

  create: (data: {
    asset_tag: string;
    name: string;
    equipment_type: string;
    description?: string | null;
    manufacturer?: string | null;
    model?: string | null;
    serial_number?: string | null;
    location?: string | null;
    department?: string | null;
    requires_calibration?: boolean;
    calibration_frequency_days?: number | null;
    requires_pm?: boolean;
    pm_frequency_days?: number | null;
    assigned_to?: string | null;
    notes?: string | null;
    tags?: string[];
  }) =>
    qmsEquipmentApiClient.post<unknown>("/equipment", data).then((r) => unwrapSuccessData<Equipment>(r.data)),

  calibrate: (
    id: string,
    data: { calibration_date: string; passed: boolean; certificate_file_id?: string | null; notes?: string | null },
  ) =>
    qmsEquipmentApiClient.post<unknown>(`/equipment/${id}/calibrate`, data).then((r) => unwrapSuccessData<Equipment>(r.data)),

  decommission: (id: string, data: { reason: string }) =>
    qmsEquipmentApiClient.post<unknown>(`/equipment/${id}/decommission`, data).then((r) => unwrapSuccessData<Equipment>(r.data)),

  dueForCalibration: () =>
    qmsEquipmentApiClient.get<unknown>("/equipment/due-for-calibration").then((r) => unwrapSuccessData<Equipment[]>(r.data)),

  update: (
    id: string,
    data: Partial<{
      name: string;
      description: string | null;
      location: string | null;
      department: string | null;
      assigned_to: string | null;
      notes: string | null;
      requires_calibration: boolean;
      calibration_frequency_days: number | null;
    }>,
  ) =>
    qmsEquipmentApiClient
      .patch<unknown>(`/equipment/${id}`, data)
      .then((r) => unwrapSuccessData<Equipment>(r.data)),

  delete: (id: string) =>
    qmsEquipmentApiClient
      .delete<unknown>(`/equipment/${id}`)
      .then((r) => unwrapSuccessData<{ message: string }>(r.data)),
};
