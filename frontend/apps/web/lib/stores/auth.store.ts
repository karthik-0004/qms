"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

export interface AuthUser {
  id: string;
  email: string;
  role: string;
  tenant_id: string | null;
  mfa_enabled: boolean;
  permissions: string[];
  product_access: string[];
}

interface AuthState {
  user: AuthUser | null;
  tenant_id: string | null;
  access_token: string | null;
  isLoading: boolean;
  setUser: (user: AuthUser | null) => void;
  setTenantId: (tenant_id: string | null) => void;
  setAccessToken: (token: string | null) => void;
  setLoading: (loading: boolean) => void;
  clear: () => void;
  hasPermission: (permission: string) => boolean;
  isRole: (...roles: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tenant_id: null,
      access_token: null,
      isLoading: false,

      setUser: (user) => set({ user }),
      setTenantId: (tenant_id) => set({ tenant_id }),
      setAccessToken: (access_token) => set({ access_token }),
      setLoading: (isLoading) => set({ isLoading }),

      clear: () =>
        set({ user: null, tenant_id: null, access_token: null, isLoading: false }),

      hasPermission: (permission: string) => {
        const { user } = get();
        if (!user) return false;
        if (user.role === "super_admin") return true;
        if (user.permissions.includes("*")) return true;
        return user.permissions.includes(permission);
      },

      isRole: (...roles: string[]) => {
        const { user } = get();
        if (!user) return false;
        return roles.includes(user.role);
      },
    }),
    {
      name: "rainer-auth",
      partialize: (state) => ({
        user: state.user,
        tenant_id: state.tenant_id,
      }),
    }
  )
);
