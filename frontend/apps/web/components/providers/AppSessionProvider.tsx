"use client";

import type { Session } from "next-auth";
import { SessionProvider } from "next-auth/react";
import {
  SESSION_PROVIDER_REFETCH_INTERVAL_SEC,
  SESSION_PROVIDER_REFETCH_ON_WINDOW_FOCUS,
} from "@/constants/session-provider";

type AppSessionProviderProps = {
  children: React.ReactNode;
  session: Session | null;
};

export function AppSessionProvider({ children, session }: AppSessionProviderProps) {
  return (
    <SessionProvider
      session={session}
      refetchInterval={SESSION_PROVIDER_REFETCH_INTERVAL_SEC}
      refetchOnWindowFocus={SESSION_PROVIDER_REFETCH_ON_WINDOW_FOCUS}
    >
      {children}
    </SessionProvider>
  );
}
