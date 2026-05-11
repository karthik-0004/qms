import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "@/lib/stores/auth.store";
import { getSessionFast, resolveSessionAuthContext } from "@/lib/api/session";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

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
  baseURL: `${API_BASE_URL}/api/v1`,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
  withCredentials: true,
});

apiClient.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const session = await getSessionFast();
  const { bearerToken, tenantId: tenantFromSession } = resolveSessionAuthContext(session);
  if (bearerToken) config.headers.Authorization = `Bearer ${bearerToken}`;
  const tenantId = tenantFromSession ?? useAuthStore.getState().tenant_id;
  if (tenantId) config.headers["X-Tenant-ID"] = tenantId;
  const userId = useAuthStore.getState().user?.id;
  if (userId) config.headers["X-User-ID"] = userId;
  config.headers["X-Request-ID"] = crypto.randomUUID();
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      window.location.href = "/login?session=expired";
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
