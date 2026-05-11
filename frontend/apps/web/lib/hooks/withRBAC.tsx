"use client";

import type { Route } from "next";
import { redirect } from "next/navigation";
import { usePermission, type Permission } from "./usePermission";
import { Skeleton } from "@/components/ui/skeleton";

interface WithRBACOptions {
  required: Permission | Permission[];
  mode?: "any" | "all";
  fallbackUrl?: Route;
}

export function withRBAC<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  options: WithRBACOptions
) {
  const {
    required,
    mode = "any",
    fallbackUrl = "/dashboard" as Route,
  } = options;
  const permissions = Array.isArray(required) ? required : [required];

  function RBACGuard(props: P) {
    const { hasAnyPermission, hasAllPermissions, isLoading } = usePermission();

    if (isLoading) {
      return (
        <div className="space-y-4 p-6">
          <Skeleton className="h-8 w-64" />
          <Skeleton className="h-64 w-full" />
        </div>
      );
    }

    const hasAccess =
      mode === "all"
        ? hasAllPermissions(permissions)
        : hasAnyPermission(permissions);

    if (!hasAccess) {
      redirect(fallbackUrl);
    }

    return <WrappedComponent {...props} />;
  }

  RBACGuard.displayName = `withRBAC(${WrappedComponent.displayName ?? WrappedComponent.name ?? "Component"})`;
  return RBACGuard;
}
