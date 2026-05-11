import { getCachedSession } from "@/lib/auth/get-cached-session";
import { redirect } from "next/navigation";
import { DashboardProducts } from "@/components/platform/DashboardProducts";

export default async function DashboardPage() {
  const session = await getCachedSession();
  if (!session?.user) redirect("/login");

  const productAccess =
    ((session as unknown as Record<string, unknown>).product_access as string[]) ?? [];

  const userName =
    (session.user as { email?: string }).email?.split("@")[0] ?? "User";

  const role = session.user.role;

  return (
    <DashboardProducts
      productAccess={productAccess}
      userName={userName}
      role={role ?? "tenant_user"}
    />
  );
}
