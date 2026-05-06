import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { getSession } from "next-auth/react";

const QMS_SERVICE_BASE_URLS = {
  document: process.env.NEXT_PUBLIC_QMS_DOCUMENT_API_URL ?? process.env.NEXT_PUBLIC_QMS_API_URL ?? "http://localhost:8020",
  qualityEvent: process.env.NEXT_PUBLIC_QMS_QUALITY_EVENT_API_URL ?? process.env.NEXT_PUBLIC_QMS_API_URL ?? "http://localhost:8021",
  capa: process.env.NEXT_PUBLIC_QMS_CAPA_API_URL ?? process.env.NEXT_PUBLIC_QMS_API_URL ?? "http://localhost:8022",
  training: process.env.NEXT_PUBLIC_QMS_TRAINING_API_URL ?? process.env.NEXT_PUBLIC_QMS_API_URL ?? "http://localhost:8023",
  equipment: process.env.NEXT_PUBLIC_QMS_EQUIPMENT_API_URL ?? process.env.NEXT_PUBLIC_QMS_API_URL ?? "http://localhost:8024",
} as const;

export type QmsServiceKey = keyof typeof QMS_SERVICE_BASE_URLS;

export function createQmsApiClient(service: QmsServiceKey): AxiosInstance {
  const baseUrl = QMS_SERVICE_BASE_URLS[service];

  const client: AxiosInstance = axios.create({
    baseURL: `${baseUrl}/api/v1`,
    headers: {
      "Content-Type": "application/json",
    },
    timeout: 30000,
    withCredentials: true,
  });

  client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    const session = await getSession();
    if (session) {
      const token = (session as unknown as Record<string, unknown>).access_token as string | undefined;
      if (token) config.headers.Authorization = `Bearer ${token}`;
      const tenantId = (session as unknown as Record<string, unknown>).tenant_id as string | undefined;
      if (tenantId) config.headers["X-Tenant-ID"] = tenantId;
    }
    config.headers["X-Request-ID"] = crypto.randomUUID();
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      if (error.response?.status === 401) {
        window.location.href = "/login?session=expired";
      }
      return Promise.reject(error);
    },
  );

  return client;
}

export const qmsApiClient: AxiosInstance = createQmsApiClient("document");

export const qmsTrainingApiClient: AxiosInstance = createQmsApiClient("training");
export const qmsQualityEventApiClient: AxiosInstance = createQmsApiClient("qualityEvent");
export const qmsCapaApiClient: AxiosInstance = createQmsApiClient("capa");
export const qmsEquipmentApiClient: AxiosInstance = createQmsApiClient("equipment");

/*
 * Backward-compat note:
 * `qmsApiClient` defaults to document-service to avoid breaking existing imports.
 * Use the per-service clients above for other domains.
 */

export const __deprecatedQmsApiClient__ = axios.create({
  baseURL: `${(process.env.NEXT_PUBLIC_QMS_API_URL ?? "http://localhost:8020")}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
  withCredentials: true,
});
