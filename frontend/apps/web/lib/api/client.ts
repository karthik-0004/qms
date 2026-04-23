import axios, { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from "axios";
import { getSession } from "next-auth/react";

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
  const session = await getSession();
  if (session) {
    const token = (session as unknown as Record<string, unknown>).access_token as string | undefined;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    const tenantId = (session as unknown as Record<string, unknown>).tenant_id as string | undefined;
    if (tenantId) {
      config.headers["X-Tenant-ID"] = tenantId;
    }
  }
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
    const errData = error.response?.data as Record<string, unknown> | undefined;
    const apiError = errData?.error as Record<string, unknown> | undefined;
    return (apiError?.message as string) ?? error.message ?? "An unexpected error occurred";
  }
  if (error instanceof Error) return error.message;
  return "An unexpected error occurred";
};
