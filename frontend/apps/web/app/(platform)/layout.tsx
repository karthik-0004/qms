import { redirect } from "next/navigation";
import { getCachedSession } from "@/lib/auth/get-cached-session";
import { PlatformShell } from "@/components/platform/PlatformShell";

export default async function PlatformLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getCachedSession();
  if (!session?.user) redirect("/login");

  return <PlatformShell session={session}>{children}</PlatformShell>;
}
