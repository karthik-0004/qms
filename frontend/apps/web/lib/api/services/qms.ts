import {
  qmsApiClient,
  qmsAuditApiClient,
  qmsCapaApiClient,
  qmsComplaintApiClient,
  qmsEnvMonitoringApiClient,
  qmsEquipmentApiClient,
  qmsMgmtReviewApiClient,
  qmsPtApiClient,
  qmsQualityEventApiClient,
  qmsRiskApiClient,
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
  vault?: string;
  taxonomy_id?: string | null;
  folder_id?: string | null;
  category_path?: string | null;
  review_interval_days?: number | null;
  next_review_date?: string | null;
  obsolete_reason?: string | null;
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

// ── Phase 4: Job Codes ───────────────────────────────────────────────────────

export interface JobCode {
  id: string;
  tenant_id: string;
  code: string;
  title: string;
  description: string | null;
  department: string | null;
  requires_certification: boolean;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  course_count: number;
  user_count: number;
  compliance_pct: number | null;
}

export interface JobCodeCourseLink {
  id: string;
  job_code_id: string;
  course_id: string;
  course_title: string | null;
  is_required: boolean;
  sort_order: number;
}

export interface JobCodeAssignment {
  id: string;
  tenant_id: string;
  job_code_id: string;
  user_id: string;
  assigned_by: string | null;
  assigned_at: string;
  is_primary: boolean;
}

export interface Trainer {
  id: string;
  tenant_id: string;
  user_id: string;
  job_code_id: string | null;
  qualification: string | null;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Exam {
  id: string;
  tenant_id: string;
  course_id: string;
  course_title: string | null;
  title: string;
  description: string | null;
  passing_score: number;
  duration_minutes: number | null;
  is_active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
  question_count: number;
}

export interface ExamQuestion {
  id: string;
  exam_id: string;
  question_text: string;
  options: string[];
  correct_answer: string;
  sort_order: number;
}

export interface ExamAttempt {
  id: string;
  tenant_id: string;
  exam_id: string;
  user_id: string;
  score: number | null;
  passed: boolean | null;
  answers: Record<string, string> | null;
  started_at: string;
  completed_at: string | null;
  status: string;
}

export interface TrainingDashboardStats {
  total_courses: number;
  total_assignments: number;
  completed_assignments: number;
  overdue_assignments: number;
  in_progress_assignments: number;
  pending_assignments: number;
  total_job_codes: number;
  users_with_overdue: number;
  overall_compliance_pct: number;
  upcoming_recertifications: number;
  total_trainers: number;
}

export interface JobCodeUserStatus {
  user_id: string;
  user_name: string | null;
  job_code_id: string;
  job_code_title: string;
  is_primary: boolean;
  courses: CourseStatusItem[];
}

export interface CourseStatusItem {
  course_id: string;
  course_title: string;
  is_required: boolean;
  assignment_id: string | null;
  status: string | null;
  score: number | null;
  passed: boolean | null;
  completed_at: string | null;
  due_date: string | null;
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

export interface CalibrationRecord {
  id: string;
  equipment_id: string;
  calibration_date: string;
  calibrated_by: string | null;
  passed: boolean;
  certificate_file_id: string | null;
  notes: string | null;
  standards_used?: string[] | null;
  as_found_reading?: string | null;
  as_left_reading?: string | null;
  measurement_uncertainty?: number | null;
  created_at: string;
}

export interface Taxonomy {
  id: string;
  tenant_id: string;
  name: string;
  description?: string | null;
  sort_order: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Folder {
  id: string;
  tenant_id: string;
  taxonomy_id: string;
  parent_id?: string | null;
  name: string;
  description?: string | null;
  path: string;
  sort_order: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ControlledCopy {
  id: string;
  document_id: string;
  version: string;
  copy_number: string;
  issued_to: string;
  issued_by: string;
  issued_at: string;
  recalled_at?: string | null;
  status: string;
  notes?: string | null;
}

export interface ContentDto {
  authoring_mode: string;
  content_ast?: unknown;
  html_snapshot?: string;
  editor_nonce?: string;
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
  vault?: string;
  taxonomy_id?: string | null;
  folder_id?: string | null;
  category_path?: string | null;
  review_interval_days?: number | null;
  next_review_date?: string | null;
  obsolete_reason?: string | null;
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
    vault: dto.vault,
    taxonomy_id: dto.taxonomy_id,
    folder_id: dto.folder_id,
    category_path: dto.category_path,
    review_interval_days: dto.review_interval_days,
    next_review_date: dto.next_review_date,
    obsolete_reason: dto.obsolete_reason,
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
  list: (params?: { search?: string; status?: string; doc_type?: string; department?: string; taxonomy_id?: string; folder_id?: string; page?: number; page_size?: number }) =>
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

  makeEffective: (id: string) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/make-effective`, {})
      .then((r) => ("data" in (r.data as object) ? mapDocument((r.data as SuccessEnvelope<DocumentDto>).data) : mapDocument(r.data as DocumentDto))),

  makeSuperseded: (id: string) =>
    qmsApiClient
      .post<SuccessEnvelope<DocumentDto> | DocumentDto>(`/documents/${id}/make-superseded`, {})
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

  // §4.4 — Editor content
  saveContent: (id: string, data: { authoring_mode: string; content_ast?: unknown; html_snapshot?: string }) =>
    qmsApiClient.post<unknown>(`/documents/${id}/content`, data).then((r) => unwrapSuccessData(r.data)),

  getContent: (id: string) =>
    qmsApiClient.get<unknown>(`/documents/${id}/content`).then((r) => unwrapSuccessData(r.data)),

  // §4.4 — File upload
  uploadFile: (id: string, formData: FormData) =>
    qmsApiClient
      .post<unknown>(`/documents/${id}/file`, formData, { headers: { "Content-Type": "multipart/form-data" } })
      .then((r) => unwrapSuccessData<{ file_id: string; filename: string; size_bytes: number }>(r.data)),

  // §7.1 — Controlled copies
  listControlledCopies: (id: string) =>
    qmsApiClient.get<unknown>(`/documents/${id}/controlled-copies`).then((r) => unwrapSuccessData(r.data)),

  issueControlledCopy: (id: string, data: { copy_number: string; issued_to: string; notes?: string }) =>
    qmsApiClient.post<unknown>(`/documents/${id}/controlled-copies`, data).then((r) => unwrapSuccessData(r.data)),

  recallControlledCopy: (docId: string, copyId: string) =>
    qmsApiClient.post<unknown>(`/documents/${docId}/controlled-copies/${copyId}/recall`).then((r) => unwrapSuccessData(r.data)),

  acknowledge: (id: string, data: { signature: string }) =>
    qmsApiClient
      .post<unknown>(`/documents/${id}/acknowledge`, data)
      .then((r) => unwrapSuccessData(r.data)),

  createVersion: (id: string, data: { change_type: string; change_summary: string }) =>
    qmsApiClient
      .post<unknown>(`/documents/${id}/versions`, data)
      .then((r) => unwrapSuccessData(r.data)),
};

// ─── Taxonomies & Folders ────────────────────────────────────────────────────

export const taxonomyApi = {
  list: () =>
    qmsApiClient.get<unknown>("/taxonomies").then((r) => unwrapSuccessData<Taxonomy[]>(r.data)),

  get: (id: string) =>
    qmsApiClient.get<unknown>(`/taxonomies/${id}`).then((r) => unwrapSuccessData<Taxonomy>(r.data)),

  create: (data: { name: string; description?: string; sort_order?: number }) =>
    qmsApiClient.post<unknown>("/taxonomies", data).then((r) => unwrapSuccessData<Taxonomy>(r.data)),

  listFolders: (taxonomyId: string) =>
    qmsApiClient.get<unknown>(`/taxonomies/${taxonomyId}/folders`).then((r) => unwrapSuccessData<Folder[]>(r.data)),

  createFolder: (taxonomyId: string, data: { name: string; parent_id?: string; description?: string; path?: string; sort_order?: number }) =>
    qmsApiClient.post<unknown>(`/taxonomies/${taxonomyId}/folders`, data).then((r) => unwrapSuccessData<Folder>(r.data)),
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

  // ── Dashboard ──────────────────────────────────────────────────────────────

  dashboardStats: () =>
    qmsTrainingApiClient.get<unknown>("/training/dashboard").then((r) => unwrapSuccessData<TrainingDashboardStats>(r.data)),

  // ── Job Codes ──────────────────────────────────────────────────────────────

  listJobCodes: (params?: { department?: string }) =>
    qmsTrainingApiClient.get<unknown>("/training/job-codes", { params }).then((r) => unwrapSuccessData<JobCode[]>(r.data)),

  getJobCode: (id: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/job-codes/${id}`).then((r) => unwrapSuccessData<JobCode>(r.data)),

  createJobCode: (data: { code: string; title: string; description?: string; department?: string; requires_certification?: boolean }) =>
    qmsTrainingApiClient.post<unknown>("/training/job-codes", data).then((r) => unwrapSuccessData<JobCode>(r.data)),

  updateJobCode: (id: string, data: { title?: string; description?: string; department?: string; requires_certification?: boolean; is_active?: boolean }) =>
    qmsTrainingApiClient.patch<unknown>(`/training/job-codes/${id}`, data).then((r) => unwrapSuccessData<JobCode>(r.data)),

  deleteJobCode: (id: string) =>
    qmsTrainingApiClient.delete(`/training/job-codes/${id}`).then((r) => r.data as { message: string }),

  getJobCodeCourses: (jobCodeId: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/job-codes/${jobCodeId}/courses`).then((r) => unwrapSuccessData<JobCodeCourseLink[]>(r.data)),

  linkCourseToJobCode: (jobCodeId: string, data: { course_id: string; is_required?: boolean; sort_order?: number }) =>
    qmsTrainingApiClient.post<unknown>(`/training/job-codes/${jobCodeId}/courses`, data).then((r) => unwrapSuccessData<JobCodeCourseLink>(r.data)),

  unlinkCourseFromJobCode: (jobCodeId: string, courseId: string) =>
    qmsTrainingApiClient.delete(`/training/job-codes/${jobCodeId}/courses/${courseId}`).then((r) => r.data as { message: string }),

  getJobCodeAssignees: (jobCodeId: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/job-codes/${jobCodeId}/assignees`).then((r) => unwrapSuccessData<JobCodeAssignment[]>(r.data)),

  assignUserToJobCode: (jobCodeId: string, data: { user_id: string; is_primary?: boolean }) =>
    qmsTrainingApiClient.post<unknown>(`/training/job-codes/${jobCodeId}/assignees`, data).then((r) => unwrapSuccessData<JobCodeAssignment>(r.data)),

  unassignUserFromJobCode: (jobCodeId: string, userId: string) =>
    qmsTrainingApiClient.delete(`/training/job-codes/${jobCodeId}/assignees/${userId}`).then((r) => r.data as { message: string }),

  getJobCodeStatusMatrix: (jobCodeId: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/job-codes/${jobCodeId}/status`).then((r) => unwrapSuccessData<JobCodeUserStatus[]>(r.data)),

  // ── Trainers ───────────────────────────────────────────────────────────────

  listTrainers: (params?: { is_active?: boolean }) =>
    qmsTrainingApiClient.get<unknown>("/training/trainers", { params }).then((r) => unwrapSuccessData<Trainer[]>(r.data)),

  createTrainer: (data: { user_id: string; job_code_id?: string; qualification?: string }) =>
    qmsTrainingApiClient.post<unknown>("/training/trainers", data).then((r) => unwrapSuccessData<Trainer>(r.data)),

  updateTrainer: (id: string, data: { job_code_id?: string; qualification?: string; is_active?: boolean }) =>
    qmsTrainingApiClient.patch<unknown>(`/training/trainers/${id}`, data).then((r) => unwrapSuccessData<Trainer>(r.data)),

  // ── Exams ──────────────────────────────────────────────────────────────────

  listExams: (params?: { course_id?: string }) =>
    qmsTrainingApiClient.get<unknown>("/training/exams", { params }).then((r) => unwrapSuccessData<Exam[]>(r.data)),

  getExam: (id: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/exams/${id}`).then((r) => unwrapSuccessData<Exam>(r.data)),

  createExam: (data: { course_id: string; title: string; description?: string; passing_score?: number; duration_minutes?: number }) =>
    qmsTrainingApiClient.post<unknown>("/training/exams", data).then((r) => unwrapSuccessData<Exam>(r.data)),

  addExamQuestion: (examId: string, data: { question_text: string; options: string[]; correct_answer: string; sort_order?: number }) =>
    qmsTrainingApiClient.post<unknown>(`/training/exams/${examId}/questions`, data).then((r) => unwrapSuccessData<ExamQuestion>(r.data)),

  listExamQuestions: (examId: string) =>
    qmsTrainingApiClient.get<unknown>(`/training/exams/${examId}/questions`).then((r) => unwrapSuccessData<ExamQuestion[]>(r.data)),

  startExamAttempt: (examId: string) =>
    qmsTrainingApiClient.post<unknown>(`/training/exams/${examId}/attempts`).then((r) => unwrapSuccessData<ExamAttempt>(r.data)),

  submitExamAttempt: (attemptId: string, data: { answers: Record<string, string> }) =>
    qmsTrainingApiClient.post<unknown>(`/training/exam-attempts/${attemptId}/submit`, data).then((r) => unwrapSuccessData<ExamAttempt>(r.data)),

  listMyExamAttempts: () =>
    qmsTrainingApiClient.get<unknown>("/training/my-exam-attempts").then((r) => unwrapSuccessData<ExamAttempt[]>(r.data)),
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

  listCalibrations: (id: string) =>
    qmsEquipmentApiClient
      .get<unknown>(`/equipment/${id}/calibrations`)
      .then((r) => unwrapSuccessData<CalibrationRecord[]>(r.data)),
};

// ─── Audit Management ────────────────────────────────────────────────────────

export interface AuditFinding {
  id: string;
  audit_id: string;
  finding_number: string;
  classification: string;
  description: string;
  iso_clause: string | null;
  evidence_file_ids: string[];
  capa_id: string | null;
  auditee_response: string | null;
  response_due_date: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface AuditChecklistItem {
  id: string;
  checklist_id: string;
  iso_clause: string | null;
  question: string;
  expected_evidence: string | null;
  sort_order: number;
}

export interface AuditChecklist {
  id: string;
  tenant_id: string;
  name: string;
  criteria: string | null;
  description: string | null;
  is_active: boolean;
  items: AuditChecklistItem[];
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface Audit {
  id: string;
  tenant_id: string;
  audit_number: string;
  title: string;
  audit_type: string;
  entity_type: string | null;
  entity_ref: string | null;
  scope: string | null;
  criteria: string | null;
  status: string;
  lead_auditor_id: string | null;
  audit_team: string[];
  auditee_id: string | null;
  scheduled_start: string | null;
  scheduled_end: string | null;
  performed_start: string | null;
  performed_end: string | null;
  checklist_id: string | null;
  summary: string | null;
  report_file_id: string | null;
  score: number | null;
  tags: string[];
  findings: AuditFinding[];
  finding_count: number;
  major_nc_count: number;
  minor_nc_count: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface AuditSummary {
  total: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  open_findings: number;
}

export const auditApi = {
  list: (params?: { status?: string; audit_type?: string; page?: number; page_size?: number }) =>
    qmsAuditApiClient
      .get<unknown>("/audits", { params })
      .then((r) => normalizePaginated<Audit>(r.data)),

  get: (id: string) =>
    qmsAuditApiClient.get<unknown>(`/audits/${id}`).then((r) => unwrapSuccessData<Audit>(r.data)),

  create: (data: {
    audit_number: string;
    title: string;
    audit_type: string;
    scope?: string | null;
    criteria?: string | null;
    lead_auditor_id?: string | null;
    auditee_id?: string | null;
    scheduled_start?: string | null;
    scheduled_end?: string | null;
    checklist_id?: string | null;
    tags?: string[];
  }) =>
    qmsAuditApiClient.post<unknown>("/audits", data).then((r) => unwrapSuccessData<Audit>(r.data)),

  update: (id: string, data: Partial<{
    title: string;
    scope: string | null;
    criteria: string | null;
    lead_auditor_id: string | null;
    auditee_id: string | null;
    scheduled_start: string | null;
    scheduled_end: string | null;
    summary: string | null;
    score: number | null;
    tags: string[];
  }>) =>
    qmsAuditApiClient.patch<unknown>(`/audits/${id}`, data).then((r) => unwrapSuccessData<Audit>(r.data)),

  start: (id: string) =>
    qmsAuditApiClient.post<unknown>(`/audits/${id}/start`, {}).then((r) => unwrapSuccessData<Audit>(r.data)),

  complete: (id: string, summary?: string) =>
    qmsAuditApiClient
      .post<unknown>(`/audits/${id}/complete`, {}, { params: summary ? { summary } : undefined })
      .then((r) => unwrapSuccessData<Audit>(r.data)),

  delete: (id: string) =>
    qmsAuditApiClient.delete<unknown>(`/audits/${id}`).then((r) => unwrapSuccessData<{ message: string }>(r.data)),

  addFinding: (auditId: string, data: {
    classification: string;
    description: string;
    iso_clause?: string | null;
    response_due_date?: string | null;
  }) =>
    qmsAuditApiClient
      .post<unknown>(`/audits/${auditId}/findings`, data)
      .then((r) => unwrapSuccessData<AuditFinding>(r.data)),

  listFindings: (auditId: string) =>
    qmsAuditApiClient
      .get<unknown>(`/audits/${auditId}/findings`)
      .then((r) => unwrapSuccessData<AuditFinding[]>(r.data)),

  updateFinding: (findingId: string, data: Partial<{
    classification: string;
    description: string;
    iso_clause: string | null;
    auditee_response: string | null;
    response_due_date: string | null;
  }>) =>
    qmsAuditApiClient
      .patch<unknown>(`/audits/findings/${findingId}`, data)
      .then((r) => unwrapSuccessData<AuditFinding>(r.data)),

  listChecklists: () =>
    qmsAuditApiClient.get<unknown>("/checklists").then((r) => unwrapSuccessData<AuditChecklist[]>(r.data)),

  createChecklist: (data: {
    name: string;
    description?: string | null;
    criteria?: string | null;
    items: { question: string; iso_clause?: string | null; expected_evidence?: string | null; sort_order?: number }[];
  }) =>
    qmsAuditApiClient.post<unknown>("/checklists", data).then((r) => unwrapSuccessData<AuditChecklist>(r.data)),
};

// ─── Customer Complaints ─────────────────────────────────────────────────────

export interface Complaint {
  id: string;
  tenant_id: string;
  complaint_number: string;
  customer_name: string | null;
  received_via: string;
  severity: string;
  category: string | null;
  description: string;
  status: string;
  investigator_id: string | null;
  root_cause: string | null;
  response_text: string | null;
  response_sent_at: string | null;
  capa_id: string | null;
  received_at: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export const complaintsApi = {
  list: (params?: { status?: string; severity?: string; category?: string; page?: number; page_size?: number }) =>
    qmsComplaintApiClient.get<unknown>("/complaints", { params }).then((r) => normalizePaginated<Complaint>(r.data)),

  get: (id: string) =>
    qmsComplaintApiClient.get<unknown>(`/complaints/${id}`).then((r) => unwrapSuccessData<Complaint>(r.data)),

  create: (data: {
    complaint_number: string;
    description: string;
    received_at: string;
    customer_name?: string | null;
    received_via?: string;
    severity?: string;
    category?: string | null;
    investigator_id?: string | null;
  }) =>
    qmsComplaintApiClient.post<unknown>("/complaints", data).then((r) => unwrapSuccessData<Complaint>(r.data)),

  update: (id: string, data: Partial<{
    customer_name: string | null;
    received_via: string;
    severity: string;
    category: string | null;
    description: string;
    status: string;
    investigator_id: string | null;
    root_cause: string | null;
    capa_id: string | null;
  }>) =>
    qmsComplaintApiClient.patch<unknown>(`/complaints/${id}`, data).then((r) => unwrapSuccessData<Complaint>(r.data)),

  respond: (id: string, data: { response_text: string }) =>
    qmsComplaintApiClient.post<unknown>(`/complaints/${id}/respond`, data).then((r) => unwrapSuccessData<Complaint>(r.data)),

  escalateToCapa: (id: string, data: { capa_id: string }) =>
    qmsComplaintApiClient.post<unknown>(`/complaints/${id}/escalate-to-capa`, data).then((r) => unwrapSuccessData<Complaint>(r.data)),

  delete: (id: string) =>
    qmsComplaintApiClient.delete<unknown>(`/complaints/${id}`).then((r) => unwrapSuccessData<{ message: string }>(r.data)),
};

// ─── Risk Management ──────────────────────────────────────────────────────────

export interface Risk {
  id: string;
  tenant_id: string;
  risk_id: string;
  category: string;
  description: string;
  severity: number;
  likelihood: number;
  risk_score: number;
  mitigation_plan: string | null;
  owner_id: string | null;
  status: string;
  review_date: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface RiskMatrixCell {
  severity: number;
  likelihood: number;
  count: number;
  risk_ids: string[];
}

export const riskApi = {
  list: (params?: { status?: string; category?: string; page?: number; page_size?: number }) =>
    qmsRiskApiClient.get<unknown>("/risks", { params }).then((r) => normalizePaginated<Risk>(r.data)),

  get: (id: string) =>
    qmsRiskApiClient.get<unknown>(`/risks/${id}`).then((r) => unwrapSuccessData<Risk>(r.data)),

  getMatrix: () =>
    qmsRiskApiClient.get<unknown>("/risks/matrix").then((r) => unwrapSuccessData<RiskMatrixCell[]>(r.data)),

  create: (data: {
    risk_id: string;
    category: string;
    description: string;
    severity?: number;
    likelihood?: number;
    owner_id?: string | null;
    mitigation_plan?: string | null;
    review_date?: string | null;
  }) =>
    qmsRiskApiClient.post<unknown>("/risks", data).then((r) => unwrapSuccessData<Risk>(r.data)),

  update: (id: string, data: Partial<{
    category: string;
    description: string;
    severity: number;
    likelihood: number;
    mitigation_plan: string | null;
    owner_id: string | null;
    status: string;
    review_date: string | null;
  }>) =>
    qmsRiskApiClient.patch<unknown>(`/risks/${id}`, data).then((r) => unwrapSuccessData<Risk>(r.data)),

  delete: (id: string) =>
    qmsRiskApiClient.delete<unknown>(`/risks/${id}`).then((r) => unwrapSuccessData<{ message: string }>(r.data)),
};

// ─── Management Review ────────────────────────────────────────────────────────

export interface ManagementReview {
  id: string;
  tenant_id: string;
  review_number: string;
  title: string;
  scheduled_date: string;
  completed_date: string | null;
  facilitator_id: string | null;
  attendees: unknown[];
  status: string;
  agenda: string | null;
  minutes: string | null;
  outcomes: unknown[];
  action_items: unknown[];
  next_review_date: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export const managementReviewApi = {
  list: (params?: { status?: string; page?: number; page_size?: number }) =>
    qmsMgmtReviewApiClient.get<unknown>("/management-reviews", { params }).then((r) => normalizePaginated<ManagementReview>(r.data)),

  get: (id: string) =>
    qmsMgmtReviewApiClient.get<unknown>(`/management-reviews/${id}`).then((r) => unwrapSuccessData<ManagementReview>(r.data)),

  create: (data: {
    review_number: string;
    title: string;
    scheduled_date: string;
    facilitator_id?: string | null;
    agenda?: string | null;
  }) =>
    qmsMgmtReviewApiClient.post<unknown>("/management-reviews", data).then((r) => unwrapSuccessData<ManagementReview>(r.data)),

  update: (id: string, data: Partial<{
    title: string;
    status: string;
    scheduled_date: string;
    completed_date: string | null;
    facilitator_id: string | null;
    attendees: unknown[];
    agenda: string | null;
    minutes: string | null;
    outcomes: unknown[];
    action_items: unknown[];
    next_review_date: string | null;
  }>) =>
    qmsMgmtReviewApiClient.patch<unknown>(`/management-reviews/${id}`, data).then((r) => unwrapSuccessData<ManagementReview>(r.data)),

  complete: (id: string) =>
    qmsMgmtReviewApiClient.post<unknown>(`/management-reviews/${id}/complete`, {}).then((r) => unwrapSuccessData<ManagementReview>(r.data)),

  delete: (id: string) =>
    qmsMgmtReviewApiClient.delete<unknown>(`/management-reviews/${id}`).then((r) => unwrapSuccessData<{ message: string }>(r.data)),
};

// ─── Environmental Monitoring ─────────────────────────────────────────────────

export interface MonitoringPoint {
  id: string;
  tenant_id: string;
  point_id: string;
  location: string;
  parameter: string;
  alert_limit: number | null;
  action_limit: number | null;
  frequency_type: string;
  frequency_value: number | null;
  status: string;
  last_reading_value: number | null;
  last_reading_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface MonitoringReading {
  id: string;
  tenant_id: string;
  point_id: string;
  value: number;
  recorded_at: string;
  recorded_by_user_id: string | null;
  status: string;
  notes: string | null;
  created_at: string;
}

export const envMonitoringApi = {
  listPoints: (params?: { status?: string; page?: number; page_size?: number }) =>
    qmsEnvMonitoringApiClient
      .get<unknown>("/monitoring-points", { params })
      .then((r) => normalizePaginated<MonitoringPoint>(r.data, (v) => v as MonitoringPoint)),

  getPoint: (id: string) =>
    qmsEnvMonitoringApiClient.get<unknown>(`/monitoring-points/${id}`).then((r) => unwrapSuccessData<MonitoringPoint>(r.data)),

  createPoint: (data: {
    point_id: string;
    location: string;
    parameter: string;
    frequency_type: string;
    alert_limit?: number | null;
    action_limit?: number | null;
    frequency_value?: number | null;
  }) =>
    qmsEnvMonitoringApiClient.post<unknown>("/monitoring-points", data).then((r) => unwrapSuccessData<MonitoringPoint>(r.data)),

  updatePoint: (id: string, data: Record<string, unknown>) =>
    qmsEnvMonitoringApiClient.patch<unknown>(`/monitoring-points/${id}`, data).then((r) => unwrapSuccessData<MonitoringPoint>(r.data)),

  addReading: (pointId: string, data: { value: number; recorded_at: string; notes?: string }) =>
    qmsEnvMonitoringApiClient.post<unknown>(`/monitoring-points/${pointId}/readings`, data).then((r) => unwrapSuccessData<MonitoringReading>(r.data)),

  listReadings: (pointId: string, params?: { from?: string; to?: string }) =>
    qmsEnvMonitoringApiClient.get<unknown>(`/monitoring-points/${pointId}/readings`, { params }).then((r) => {
      const data = r.data as { data?: MonitoringReading[]; items?: MonitoringReading[] } | MonitoringReading[];
      if (Array.isArray(data)) return data as MonitoringReading[];
      if (Array.isArray((data as { data?: MonitoringReading[] }).data)) return (data as { data: MonitoringReading[] }).data;
      if (Array.isArray((data as { items?: MonitoringReading[] }).items)) return (data as { items: MonitoringReading[] }).items;
      return [] as MonitoringReading[];
    }),

  listExcursions: (pointId: string) =>
    qmsEnvMonitoringApiClient.get<unknown>(`/monitoring-points/${pointId}/excursions`).then((r) => {
      const data = r.data as { data?: MonitoringReading[] } | MonitoringReading[];
      if (Array.isArray(data)) return data as MonitoringReading[];
      return ((data as { data?: MonitoringReading[] }).data ?? []) as MonitoringReading[];
    }),
};

// ─── Proficiency Testing ──────────────────────────────────────────────────────

export interface PTProgram {
  id: string;
  tenant_id: string;
  provider: string;
  scheme_name: string;
  parameter: string;
  frequency_months: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface PTRound {
  id: string;
  tenant_id: string;
  program_id: string;
  round_id: string;
  sample_received_date: string | null;
  result_due_date: string | null;
  reported_result: number | null;
  reference_value: number | null;
  z_score: number | null;
  en_number: number | null;
  status: string;
  capa_id: string | null;
  notes: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export const ptApi = {
  listPrograms: (params?: { page?: number; page_size?: number }) =>
    qmsPtApiClient
      .get<unknown>("/pt/programs", { params })
      .then((r) => normalizePaginated<PTProgram>(r.data, (v) => v as PTProgram)),

  getProgram: (id: string) =>
    qmsPtApiClient.get<unknown>(`/pt/programs/${id}`).then((r) => unwrapSuccessData<PTProgram>(r.data)),

  createProgram: (data: {
    provider: string;
    scheme_name: string;
    parameter: string;
    frequency_months: number;
  }) =>
    qmsPtApiClient.post<unknown>("/pt/programs", data).then((r) => unwrapSuccessData<PTProgram>(r.data)),

  listRounds: (programId: string) =>
    qmsPtApiClient.get<unknown>(`/pt/programs/${programId}/rounds`).then((r) => {
      const data = r.data as { data?: PTRound[] } | PTRound[];
      if (Array.isArray(data)) return data as PTRound[];
      return ((data as { data?: PTRound[] }).data ?? []) as PTRound[];
    }),

  createRound: (programId: string, data: {
    round_id: string;
    sample_received_date?: string | null;
    result_due_date?: string | null;
    notes?: string | null;
  }) =>
    qmsPtApiClient.post<unknown>(`/pt/programs/${programId}/rounds`, data).then((r) => unwrapSuccessData<PTRound>(r.data)),

  getRound: (roundId: string) =>
    qmsPtApiClient.get<unknown>(`/pt/rounds/${roundId}`).then((r) => unwrapSuccessData<PTRound>(r.data)),

  updateRound: (roundId: string, data: Record<string, unknown>) =>
    qmsPtApiClient.patch<unknown>(`/pt/rounds/${roundId}`, data).then((r) => unwrapSuccessData<PTRound>(r.data)),

  calculateScores: (roundId: string) =>
    qmsPtApiClient.post<unknown>(`/pt/rounds/${roundId}/calculate-scores`).then((r) => unwrapSuccessData<{
      round_id: string;
      reported_result: number;
      reference_value: number;
      z_score: number;
      en_number: number;
      z_score_pass: boolean;
      en_number_pass: boolean;
    }>(r.data)),
};
