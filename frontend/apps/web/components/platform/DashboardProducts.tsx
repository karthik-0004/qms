"use client";

import { ProductCard } from "./ProductCard";
import { usePlatformKPIs } from "@/lib/hooks/queries/analytics";
import { Skeleton } from "@/components/ui/skeleton";

interface DashboardProductsProps {
  productAccess: string[];
  userName: string;
}

export function DashboardProducts({ productAccess, userName }: DashboardProductsProps) {
  const { data: kpiData, isLoading } = usePlatformKPIs();
  const kpis = kpiData?.kpis;

  const fmt = (n: number | undefined) => (n !== undefined ? String(n) : "—");

  const products = [
    {
      id: "qms" as const,
      name: "RainerQMS",
      description:
        "Quality Management System — Document control, CAPA, training, audits, and more.",
      href: "/qms/documents",
      color: "blue" as const,
      available: productAccess.length === 0 || productAccess.includes("qms"),
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
      available: productAccess.length === 0 || productAccess.includes("em"),
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
      available: productAccess.length === 0 || productAccess.includes("ccv"),
      stats: [
        { label: "Work Orders (MTD)", value: fmt(kpis?.workorders_this_month) },
        { label: "Certs Issued YTD", value: fmt(kpis?.certificates_issued_ytd) },
        { label: "Total Users", value: fmt(kpis?.total_users) },
      ],
    },
  ];

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
        {products.map((product) => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
}
