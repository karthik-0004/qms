"use client";

import Link from "next/link";
import type { Route } from "next";
import { ChevronLeft, Building2, Hash } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { useTenantBySlug, useUsers } from "@/lib/hooks/queries/platform";
import type { User } from "@/lib/api/services/platform";

const ROLE_LABEL: Record<string, string> = {
  super_admin: "Super Admin",
  tenant_admin: "Tenant Admin",
  tenant_user: "User",
};

const ROLE_STYLE: Record<string, string> = {
  super_admin: "bg-red-100 text-red-700",
  tenant_admin: "bg-purple-100 text-purple-700",
  tenant_user: "bg-blue-100 text-blue-700",
};

export function TenantDetailView({ slug }: { slug: string }) {
  const { data: tenant, isLoading: tenantLoading, isError: tenantError } = useTenantBySlug(slug);
  const { data: usersData, isLoading: usersLoading } = useUsers({
    page: 1,
    page_size: 200,
  });

  const tenantUsers: User[] =
    tenant && usersData?.items
      ? usersData.items.filter((u) => u.tenant_id === tenant.id)
      : [];

  const tenantAdmins = tenantUsers.filter((u) => u.role === "tenant_admin");

  if (tenantLoading) {
    return (
      <div className="space-y-4 max-w-4xl">
        <Skeleton className="h-10 w-64" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (tenantError || !tenant) {
    return (
      <div className="space-y-4 max-w-4xl">
        <Button variant="outline" size="sm" className="gap-1" asChild>
          <Link href={"/admin/tenants" as Route}>
            <ChevronLeft className="h-4 w-4" />
            Back to tenants
          </Link>
        </Button>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">
              Tenant not found, or you do not have access to this slug.
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3 min-w-0">
          <Button variant="outline" size="icon" className="shrink-0 min-h-11 min-w-11" asChild>
            <Link href={"/admin/tenants" as Route} aria-label="Back to tenant list">
              <ChevronLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-slate-800 flex items-center justify-center shrink-0">
              <Building2 className="h-5 w-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-2xl font-bold tracking-tight truncate">{tenant.tenant_name}</h1>
              <p className="text-muted-foreground text-sm flex items-center gap-1.5 min-w-0">
                <Hash className="h-3.5 w-3.5 shrink-0" />
                <span className="font-mono truncate">{tenant.slug}</span>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Tenant</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Status</span>
              <span className="font-medium">{tenant.status}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Tier</span>
              <span className="font-medium">{tenant.tier}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Region</span>
              <span className="font-medium">{tenant.region}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">Products</span>
              <span className="font-medium text-right">{tenant.products.join(", ")}</span>
            </div>
            <div className="flex justify-between gap-4 text-xs font-mono break-all">
              <span className="text-muted-foreground shrink-0">ID</span>
              <span>{tenant.id}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Tenant admins</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-muted-foreground">
            {usersLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : tenantAdmins.length === 0 ? (
              <p>No tenant admin users are associated with this tenant in the directory yet.</p>
            ) : (
              <ul className="space-y-2">
                {tenantAdmins.map((u) => (
                  <li key={u.id} className="flex flex-wrap items-center justify-between gap-2">
                    <span className="text-foreground font-medium">
                      {u.first_name} {u.last_name}
                    </span>
                    <span
                      className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_STYLE[u.role] ?? "bg-slate-100"}`}
                    >
                      {ROLE_LABEL[u.role] ?? u.role}
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">All users in this tenant</CardTitle>
        </CardHeader>
        <CardContent>
          {usersLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : tenantUsers.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No users matched this tenant in the current directory page. Adjust user provisioning if
              you expect accounts here.
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">User</th>
                    <th className="pb-2 pr-4 font-medium">Role</th>
                    <th className="pb-2 font-medium">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {tenantUsers.map((u) => (
                    <tr key={u.id} className="border-b last:border-0">
                      <td className="py-2 pr-4">
                        <p className="font-medium">
                          {u.first_name} {u.last_name}
                        </p>
                        <p className="text-xs text-muted-foreground">{u.email}</p>
                      </td>
                      <td className="py-2 pr-4">
                        <span
                          className={`inline-flex rounded-full px-2 py-0.5 text-xs font-medium ${ROLE_STYLE[u.role] ?? "bg-slate-100"}`}
                        >
                          {ROLE_LABEL[u.role] ?? u.role}
                        </span>
                      </td>
                      <td className="py-2 text-muted-foreground">{u.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
