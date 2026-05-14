"use client";

import { useEffect } from "react";
import type { Session } from "next-auth";
import { SessionProvider, useSession } from "next-auth/react";
import { useAuthStore } from "@/lib/stores/auth.store";
import {
  SESSION_PROVIDER_REFETCH_INTERVAL_SEC,
  SESSION_PROVIDER_REFETCH_ON_WINDOW_FOCUS,
} from "@/constants/session-provider";

type AppSessionProviderProps = {
  children: React.ReactNode;
  session: Session | null;
};

function SessionToAuthStoreSync() {
  const { data: session } = useSession();
  const setUser = useAuthStore((s) => s.setUser);
  const setTenantId = useAuthStore((s) => s.setTenantId);
  const setAccessToken = useAuthStore((s) => s.setAccessToken);

  useEffect(() => {
    if (session?.user) {
      const accessToken = session.user.access_token || session.accessToken || null;
      setUser({
        id: session.user.id,
        email: session.user.email || "",
        role: session.user.role,
        tenant_id: session.user.tenant_id,
        mfa_enabled: session.user.mfa_enabled || false,
        permissions: session.user.permissions || [],
        product_access: session.user.product_access || [],
      });
      setTenantId(session.user.tenant_id);
      setAccessToken(accessToken);
    } else {
      setUser(null);
      setTenantId(null);
      setAccessToken(null);
    }
  }, [session, setUser, setTenantId, setAccessToken]);

  return null;
}

export function AppSessionProvider({ children, session }: AppSessionProviderProps) {
  return (
    <SessionProvider
      session={session}
      refetchInterval={SESSION_PROVIDER_REFETCH_INTERVAL_SEC}
      refetchOnWindowFocus={SESSION_PROVIDER_REFETCH_ON_WINDOW_FOCUS}
    >
      <SessionToAuthStoreSync />
      {children}
    </SessionProvider>
  );
}
