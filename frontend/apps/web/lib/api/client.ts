import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/lib/stores/auth.store";
import { getSessionFast, clearSessionCache, resolveSessionAuthContext } from "@/lib/api/session";

const SERVER_API_BASE = `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/v1`;

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value: string) => void;
  reject: (error: Error) => void;
}> = [];

const processQueue = (error: Error | null, token: string | null = null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token!);
  });
  failedQueue = [];
};

export const apiClient: AxiosInstance = axios.create({
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, // Increased to 60 seconds to match proxy timeout
  withCredentials: true,
});

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  // Browser: use Next.js `/api/platform` route handler → gateway `/api/v1/*`
  // Server: use direct SERVER_API_BASE
  config.baseURL = typeof window === "undefined" ? SERVER_API_BASE : "/api/platform";

  // Use cached session — do NOT clear cache on every request as that forces a network
  // round-trip to /api/auth/session on each call and can return null under load,
  // causing the Authorization header to be missing and producing 401s.
  const session = await getSessionFast();

  const { bearerToken, tenantId: tenantFromSession, userId: userIdFromSession } = resolveSessionAuthContext(session);

  // Fall back to auth store access_token if session doesn't have bearer token
  const storeToken = useAuthStore.getState().access_token;
  const authToken = bearerToken ?? storeToken;
  if (authToken) config.headers.Authorization = `Bearer ${authToken}`;

  const tenantId = tenantFromSession ?? useAuthStore.getState().tenant_id;
  if (tenantId) config.headers["X-Tenant-ID"] = tenantId;
  const userId = userIdFromSession ?? useAuthStore.getState().user?.id;
  if (userId) config.headers["X-User-ID"] = userId;
  config.headers["X-Request-ID"] = crypto.randomUUID();

  return config;
});

apiClient.interceptors.response.use(
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
        return apiClient(originalConfig);
      }
      window.location.href = "/signin?reason=session_expired";
    }
    return Promise.reject(error);
  }
);

export const extractData = <T>(response: { data: { data: T } }): T =>
  response.data.data;

export const handleApiError = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const status = error.response?.status;
    const prefix = status ? `[${status}] ` : "";
    const errData = error.response?.data as Record<string, unknown> | undefined;
    const rawDetail = errData?.detail;
    if (typeof rawDetail === "string" && rawDetail.trim()) {
      return `${prefix}${rawDetail}`;
    }
    if (Array.isArray(rawDetail) && rawDetail.length > 0) {
      const first = rawDetail[0] as Record<string, unknown>;
      const msg = typeof first?.msg === "string" ? first.msg : null;
      if (msg) return `${prefix}${msg}`;
    }
    const apiError = errData?.error as Record<string, unknown> | undefined;
    const main = (apiError?.message as string) ?? error.message ?? "An unexpected error occurred";
    const details = apiError?.details as Array<{ message?: string }> | undefined;
    const firstDetail = details?.find((d) => d?.message)?.message;
    if (firstDetail && firstDetail !== main) {
      return `${prefix}${main} — ${firstDetail}`;
    }
    return `${prefix}${main}`;
  }
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred";
};
