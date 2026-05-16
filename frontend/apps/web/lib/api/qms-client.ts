import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/lib/stores/auth.store";
import { getSessionFast, clearSessionCache, resolveSessionAuthContext } from "@/lib/api/session";

/**
 * Prefer routing QMS traffic through the platform gateway to avoid CORS / mixed-content
 * issues in browser environments. Service-specific URLs can still override this.
 */
const DEFAULT_GATEWAY_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const QMS_SERVICE_BASE_URLS = {
  document:
    process.env.NEXT_PUBLIC_QMS_DOCUMENT_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  qualityEvent:
    process.env.NEXT_PUBLIC_QMS_QUALITY_EVENT_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  capa:
    process.env.NEXT_PUBLIC_QMS_CAPA_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  training:
    process.env.NEXT_PUBLIC_QMS_TRAINING_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  equipment:
    process.env.NEXT_PUBLIC_QMS_EQUIPMENT_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  audit:
    process.env.NEXT_PUBLIC_QMS_AUDIT_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  complaint:
    process.env.NEXT_PUBLIC_QMS_COMPLAINT_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  risk:
    process.env.NEXT_PUBLIC_QMS_RISK_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  managementReview:
    process.env.NEXT_PUBLIC_QMS_MGMT_REVIEW_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  envMonitoring:
    process.env.NEXT_PUBLIC_QMS_ENV_MONITORING_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
  pt:
    process.env.NEXT_PUBLIC_QMS_PT_API_URL ??
    process.env.NEXT_PUBLIC_QMS_API_URL ??
    DEFAULT_GATEWAY_URL,
} as const;

export type QmsServiceKey = keyof typeof QMS_SERVICE_BASE_URLS;

export function createQmsApiClient(service: QmsServiceKey): AxiosInstance {
  const baseUrl = QMS_SERVICE_BASE_URLS[service];

  const client: AxiosInstance = axios.create({
    baseURL: typeof window === "undefined" ? `${baseUrl}/api/v1` : "/api/platform",
    headers: {
      "Content-Type": "application/json",
    },
    timeout: 30000,
    withCredentials: true,
  });

  client.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
    const session = await getSessionFast();
    const { bearerToken, tenantId: tenantFromSession, userId: userIdFromSession } = resolveSessionAuthContext(session);
    // Fall back to auth store access_token if session doesn't have bearer token
    const authToken = bearerToken ?? useAuthStore.getState().access_token;
    if (authToken) config.headers.Authorization = `Bearer ${authToken}`;
    const tenantId = tenantFromSession ?? useAuthStore.getState().tenant_id;
    if (tenantId) config.headers["X-Tenant-ID"] = tenantId;
    const userId = userIdFromSession ?? useAuthStore.getState().user?.id;
    if (userId) config.headers["X-User-ID"] = userId;
    config.headers["X-Request-ID"] = crypto.randomUUID();
    return config;
  });

  client.interceptors.response.use(
    (response) => response,
    async (error: AxiosError) => {
      const originalConfig = error.config as InternalAxiosRequestConfig & { _retried?: boolean };
      if (error.response?.status === 401 && !originalConfig._retried) {
        originalConfig._retried = true;
        clearSessionCache();
        const freshSession = await getSessionFast();
        const { bearerToken } = resolveSessionAuthContext(freshSession);
        // Fall back to auth store access_token if session doesn't have bearer token
        const authToken = bearerToken ?? useAuthStore.getState().access_token;
        if (authToken) {
          originalConfig.headers.Authorization = `Bearer ${authToken}`;
          return client(originalConfig);
        }
        window.location.href = "/signin?reason=session_expired";
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
export const qmsAuditApiClient: AxiosInstance = createQmsApiClient("audit");
export const qmsComplaintApiClient: AxiosInstance = createQmsApiClient("complaint");
export const qmsRiskApiClient: AxiosInstance = createQmsApiClient("risk");
export const qmsMgmtReviewApiClient: AxiosInstance = createQmsApiClient("managementReview");
export const qmsEnvMonitoringApiClient: AxiosInstance = createQmsApiClient("envMonitoring");
export const qmsPtApiClient: AxiosInstance = createQmsApiClient("pt");

/*
 * Backward-compat note:
 * `qmsApiClient` defaults to document-service to avoid breaking existing imports.
 * Use the per-service clients above for other domains.
 */

export const __deprecatedQmsApiClient__ = axios.create({
  baseURL: `${(process.env.NEXT_PUBLIC_QMS_API_URL ?? DEFAULT_GATEWAY_URL)}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
  withCredentials: true,
});
