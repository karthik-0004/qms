"use client";

import Link from "next/link";
import type { Route } from "next";
import {
  Activity,
  ArrowRight,
  Building2,
  CheckCircle2,
  Crown,
  LayoutDashboard,
  Users,
} from "lucide-react";
import { ProductCard } from "./ProductCard";
import { usePlatformKPIs } from "@/lib/hooks/queries/analytics";
import { useSuperAdminDashboardMetrics } from "@/lib/hooks/queries/platform";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useMemo } from "react";
import { useSearchParams } from "next/navigation";
import { cn } from "@/lib/utils";

interface DashboardProductsProps {
  productAccess: string[];
  userName: string;
  role: string;
}

/** When session has no product_access (common today), tenant users fall back to all products; super admins must never get that shortcut. */
function isProductAvailable(productId: "qms" | "em" | "ccv", productAccess: string[], role: string): boolean {
  if (role === "super_admin") return false;
  return productAccess.length === 0 || productAccess.includes(productId);
}

function formatCount(n: number) {
  return n.toLocaleString();
}

export function DashboardProducts({ productAccess, userName, role }: DashboardProductsProps) {
  const { data: kpiData } = usePlatformKPIs({ enabled: role !== "super_admin" });
  const kpis = kpiData?.kpis;
  const searchParams = useSearchParams();
  const query = (searchParams.get("q") ?? "").trim().toLowerCase();
  const superAdminMetrics = useSuperAdminDashboardMetrics(role === "super_admin");

  const fmt = (n: number | undefined) => (n !== undefined ? String(n) : "—");

  if (role === "super_admin") {
    const {
      tenantTotal,
      activeTenantTotal,
      userTotal,
      auditTotal,
      isLoading,
    } = superAdminMetrics;
    const inactiveTenants = Math.max(0, tenantTotal - activeTenantTotal);

    return (
      <div className="space-y-8">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Welcome back, {userName}</h1>
          <p className="text-muted-foreground mt-1">
            Platform overview — live counts across tenants and users. Open details from any card or
            use quick actions below.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
          {isLoading ? (
            Array.from({ length: 4 }).map((_, i) => (
              <Card key={i}>
                <CardContent className="pt-6">
                  <Skeleton className="h-4 w-24 mb-4" />
                  <Skeleton className="h-9 w-20" />
                </CardContent>
              </Card>
            ))
          ) : (
            <>
              <Link href={"/admin/tenants" as Route} className="group block min-h-[44px]">
                <Card
                  className={cn(
                    "h-full transition-all border-border bg-card shadow-sm",
                    "group-hover:border-blue-400/70 group-hover:shadow-md dark:group-hover:border-blue-600"
                  )}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-blue-600 p-2.5 text-white">
                          <Building2 className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">
                            Total tenants
                          </p>
                          <p className="text-3xl font-bold tabular-nums text-blue-700 dark:text-blue-400 mt-1">
                            {formatCount(tenantTotal)}
                          </p>
                          {inactiveTenants > 0 && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {formatCount(inactiveTenants)} not active
                            </p>
                          )}
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-50 group-hover:opacity-100 shrink-0 transition-opacity" />
                    </div>
                  </CardContent>
                </Card>
              </Link>

              <Link href={"/admin/tenants" as Route} className="group block min-h-[44px]">
                <Card
                  className={cn(
                    "h-full transition-all border-border bg-card shadow-sm",
                    "group-hover:border-green-400/70 group-hover:shadow-md dark:group-hover:border-green-700"
                  )}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-emerald-600 p-2.5 text-white">
                          <CheckCircle2 className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">
                            Active tenants
                          </p>
                          <p className="text-3xl font-bold tabular-nums text-emerald-700 dark:text-emerald-400 mt-1">
                            {formatCount(activeTenantTotal)}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">Status = active</p>
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-50 group-hover:opacity-100 shrink-0 transition-opacity" />
                    </div>
                  </CardContent>
                </Card>
              </Link>

              <Link href={"/admin" as Route} className="group block min-h-[44px]">
                <Card
                  className={cn(
                    "h-full transition-all border-border bg-card shadow-sm",
                    "group-hover:border-violet-400/70 group-hover:shadow-md dark:group-hover:border-violet-600"
                  )}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-violet-600 p-2.5 text-white">
                          <Users className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">
                            Directory users
                          </p>
                          <p className="text-3xl font-bold tabular-nums text-violet-700 dark:text-violet-400 mt-1">
                            {formatCount(userTotal)}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">Across all tenants</p>
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-50 group-hover:opacity-100 shrink-0 transition-opacity" />
                    </div>
                  </CardContent>
                </Card>
              </Link>

              <Link href={"/admin" as Route} className="group block min-h-[44px]">
                <Card
                  className={cn(
                    "h-full transition-all border-border bg-card shadow-sm",
                    "group-hover:border-amber-400/70 group-hover:shadow-md dark:group-hover:border-amber-700"
                  )}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between gap-3">
                      <div className="flex items-center gap-3">
                        <div className="rounded-xl bg-amber-600 p-2.5 text-white">
                          <Activity className="h-5 w-5" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-muted-foreground">
                            Audit log entries
                          </p>
                          <p className="text-3xl font-bold tabular-nums text-amber-800 dark:text-amber-400 mt-1">
                            {formatCount(auditTotal)}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            Total recorded events
                          </p>
                        </div>
                      </div>
                      <ArrowRight className="h-4 w-4 text-muted-foreground opacity-50 group-hover:opacity-100 shrink-0 transition-opacity" />
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </>
          )}
        </div>

        <div className="flex flex-col sm:flex-row flex-wrap gap-3">
          <Button size="lg" variant="outline" className="min-h-11 justify-between gap-2" asChild>
            <Link href={"/admin/tenants" as Route}>
              <span className="inline-flex items-center gap-2">
                <Building2 className="h-4 w-4" /> Manage tenants
              </span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
          <Button size="lg" variant="outline" className="min-h-11 justify-between gap-2" asChild>
            <Link href={"/admin" as Route}>
              <span className="inline-flex items-center gap-2">
                <Crown className="h-4 w-4 text-red-600" /> Platform admin
              </span>
              <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        </div>

        <p className="text-xs text-muted-foreground flex items-center gap-2">
          <LayoutDashboard className="h-3.5 w-3.5 shrink-0" />
          More navigation is available in the sidebar.
        </p>
      </div>
    );
  }

  const products = [
    {
      id: "qms" as const,
      name: "RainerQMS",
      description:
        "Quality Management System — Document control, CAPA, training, audits, and more.",
      href: "/qms/documents",
      color: "blue" as const,
      available: isProductAvailable("qms", productAccess, role),
      stats: [
        { label: "Total Documents", value: fmt(kpis?.documents_total) },
        { label: "Open CAPAs", value: fmt(kpis?.open_capas) },
        { label: "Upcoming Trainings", value: fmt(kpis?.upcoming_trainings) },
      ],
    },
    {
      id: "em" as const,
      name: "EndGameBiotech",
      description:
        "EM Plate Analytics — AI-powered colony detection, QA review, and environmental monitoring.",
      href: "/em/plates",
      color: "green" as const,
      available: isProductAvailable("em", productAccess, role),
      stats: [
        { label: "Quality Events", value: fmt(kpis?.open_quality_events) },
        { label: "Equipment Due Cal", value: fmt(kpis?.equipment_due_calibration) },
        { label: "Active Users", value: fmt(kpis?.active_users_30d) },
      ],
    },
    {
      id: "ccv" as const,
      name: "RainerCCV",
      description:
        "Calibration, Certification & Validation — Field execution, work orders, and certificates.",
      href: "/ccv/work-orders",
      color: "orange" as const,
      available: isProductAvailable("ccv", productAccess, role),
      stats: [
        { label: "Work Orders (MTD)", value: fmt(kpis?.workorders_this_month) },
        { label: "Certs Issued YTD", value: fmt(kpis?.certificates_issued_ytd) },
        { label: "Total Users", value: fmt(kpis?.total_users) },
      ],
    },
  ];

  const filteredProducts = useMemo(() => {
    if (!query) return products;
    return products.filter((p) => {
      const haystack = `${p.id} ${p.name} ${p.description}`.toLowerCase();
      return haystack.includes(query);
    });
  }, [products, query]);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-foreground">
          Welcome back, {userName}
        </h1>
        <p className="text-muted-foreground mt-1">
          Select a product to get started or continue where you left off.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}
