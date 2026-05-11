import type { Session } from "next-auth";
import { ActiveProductSync } from "@/components/platform/ActiveProductSync";
import { Header } from "@/components/platform/Header";
import { Sidebar } from "@/components/platform/Sidebar";

export function PlatformShell({
  session,
  children,
}: {
  session: Session;
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen overflow-hidden bg-background">
      <ActiveProductSync />
      <Sidebar session={session} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header session={session} />
        <main className="flex-1 overflow-y-auto p-6 bg-slate-50 dark:bg-slate-900/50">
          {children}
        </main>
      </div>
    </div>
  );
}
