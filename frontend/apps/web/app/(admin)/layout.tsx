import { redirect } from "next/navigation";
import { getCachedSession } from "@/lib/auth/get-cached-session";
import { Sidebar } from "@/components/platform/Sidebar";
import { Header } from "@/components/platform/Header";

export default async function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getCachedSession();
  if (!session?.user) redirect("/super-admin/signin");

  const role = session.user.role;
  if (role !== "super_admin") redirect("/dashboard");

  return (
    <div className="flex h-screen overflow-hidden bg-background">
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
