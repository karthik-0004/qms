import { redirect } from "next/navigation";
import { getCachedSession } from "@/lib/auth/get-cached-session";

export default async function RootPage() {
  const session = await getCachedSession();
  if (!session?.user) redirect("/signin");
  if (session.user.role === "super_admin") redirect("/super-admin");
  redirect("/dashboard");
}
