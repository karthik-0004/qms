import { apiClient } from "../client";

// ─── Types ──────────────────────────────────────────────────────────────────

export interface Plate {
  id: string;
  barcode: string;
  plate_type: string;
  media_type: string;
  status: string;
  location: string | null;
  created_at: string;
  updated_at: string;
}

export interface EMImage {
  id: string;
  plate_id: string;
  image_type: string;
  s3_key: string;
  is_primary: boolean;
  captured_at: string;
}

export interface AIRun {
  id: string;
  plate_id: string;
  image_id: string;
  status: string;
  colony_count: number | null;
  confidence: number | null;
  has_contamination: boolean;
  model_name: string;
  started_at: string;
  completed_at: string | null;
}

export interface Job {
  id: string;
  job_type: string;
  status: string;
  priority: number;
  plate_barcode: string;
  worker_id: string | null;
  attempts: number;
  max_attempts: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface QAReview {
  id: string;
  plate_id: string;
  ai_run_id: string;
  reviewer_id: string | null;
  status: string;
  decision: string | null;
  override_colony_count: number | null;
  comments: string | null;
  reviewed_at: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ─── Plates ─────────────────────────────────────────────────────────────────

export const platesApi = {
  list: (params?: { search?: string; status?: string; plate_type?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Plate>>("/plates/plates", { params }).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Plate>(`/plates/plates/${id}`).then((r) => r.data),

  register: (data: { barcode: string; plate_type: string; media_type: string }) =>
    apiClient.post<Plate>("/plates/plates", data).then((r) => r.data),

  transition: (id: string, data: { action: string }) =>
    apiClient.post<Plate>(`/plates/plates/${id}/transition`, data).then((r) => r.data),
};

// ─── Images ─────────────────────────────────────────────────────────────────

export const imagesApi = {
  listByPlate: (plateId: string) =>
    apiClient.get<EMImage[]>(`/images/plates/${plateId}/images`).then((r) => r.data),

  upload: (plateId: string, formData: FormData) =>
    apiClient.post<EMImage>(`/images/plates/${plateId}/images`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then((r) => r.data),
};

// ─── AI Runs ────────────────────────────────────────────────────────────────

export const aiRunsApi = {
  listByPlate: (plateId: string) =>
    apiClient.get<AIRun[]>(`/ai/plates/${plateId}/runs`).then((r) => r.data),

  start: (data: { plate_id: string; image_id: string }) =>
    apiClient.post<AIRun>("/ai/runs", data).then((r) => r.data),
};

// ─── Jobs ───────────────────────────────────────────────────────────────────

export const jobsApi = {
  list: (params?: { status?: string; page?: number; page_size?: number }) =>
    apiClient.get<PaginatedResponse<Job>>("/jobs/jobs", { params }).then((r) => r.data),

  enqueue: (data: { job_type: string; plate_barcode: string; priority?: number }) =>
    apiClient.post<Job>("/jobs/jobs", data).then((r) => r.data),

  get: (id: string) =>
    apiClient.get<Job>(`/jobs/jobs/${id}`).then((r) => r.data),
};

// ─── QA Reviews ─────────────────────────────────────────────────────────────

export const qaReviewsApi = {
  listByPlate: (plateId: string) =>
    apiClient.get<QAReview[]>(`/qa-reviews/plates/${plateId}/reviews`).then((r) => r.data),

  create: (data: { plate_id: string; ai_run_id: string }) =>
    apiClient.post<QAReview>("/qa-reviews/reviews", data).then((r) => r.data),

  approve: (id: string, data: { comments?: string }) =>
    apiClient.post<QAReview>(`/qa-reviews/reviews/${id}/approve`, data).then((r) => r.data),

  reject: (id: string, data: { comments: string; override_colony_count?: number }) =>
    apiClient.post<QAReview>(`/qa-reviews/reviews/${id}/reject`, data).then((r) => r.data),
};
