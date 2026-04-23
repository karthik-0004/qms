import { redirect } from "next/navigation";
import { auth } from "@/lib/auth/config";

export default async function QMSLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await auth();
  if (!session?.user) redirect("/login");

  return <>{children}</>;
}
