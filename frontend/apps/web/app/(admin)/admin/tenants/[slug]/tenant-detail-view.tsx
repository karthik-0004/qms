"use client";

import Link from "next/link";
import type { Route } from "next";
import { ChevronLeft, Building2, Hash, Loader2, Mail, Pencil, Settings } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { TENANT_ADMIN_LABELS } from "@/constants/tenant-admin";
import { handleApiError } from "@/lib/api/client";
import type { User } from "@/lib/api/services/platform";
import {
  useResendTenantWelcomeEmail,
  useTenantBySlug,
  useUsers,
} from "@/lib/hooks/queries/platform";

const ROLE_LABEL: Record<string, string> = {
  super_admin: TENANT_ADMIN_LABELS.role_super_admin,
  tenant_admin: TENANT_ADMIN_LABELS.role_tenant_admin,
  tenant_user: TENANT_ADMIN_LABELS.role_tenant_user,
};

const ROLE_STYLE: Record<string, string> = {
  super_admin: "bg-red-100 text-red-700",
  tenant_admin: "bg-purple-100 text-purple-700",
  tenant_user: "bg-blue-100 text-blue-700",
};

export function TenantDetailView({ slug }: { slug: string }) {
  const { data: tenant, isLoading: tenantLoading, isError: tenantError } = useTenantBySlug(slug);
  const resendWelcome = useResendTenantWelcomeEmail();
  const { data: usersData, isLoading: usersLoading } = useUsers({
    page: 1,
    page_size: 200,
  });

  const tenantUsers: User[] =
    tenant && usersData?.items
      ? usersData.items.filter((u) => u.tenant_id === tenant.id)
      : [];

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
        <Button variant="outline" size="sm" className="gap-1 min-h-11" asChild>
          <Link href={"/super-admin/tenants" as Route}>
            <ChevronLeft className="h-4 w-4" />
            {TENANT_ADMIN_LABELS.detail_back_link}
          </Link>
        </Button>
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-muted-foreground">
              {TENANT_ADMIN_LABELS.detail_not_found}
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  const companyProfile =
    tenant.company_profile && typeof tenant.company_profile === "object"
      ? tenant.company_profile
      : {};
  const billingProfile =
    tenant.billing_profile && typeof tenant.billing_profile === "object"
      ? tenant.billing_profile
      : {};
  const pc = tenant.primary_contact ?? {
    first_name: null,
    last_name: null,
    email: null,
    phone: null,
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3 min-w-0">
          <Button variant="outline" size="icon" className="shrink-0 min-h-11 min-w-11" asChild>
            <Link href={"/super-admin/tenants" as Route} aria-label={TENANT_ADMIN_LABELS.detail_back_link}>
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
        <div className="flex flex-wrap gap-2 shrink-0">
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="min-h-11 gap-1.5"
            disabled={resendWelcome.isPending}
            aria-label={TENANT_ADMIN_LABELS.action_resend_welcome_aria}
            onClick={() => {
              resendWelcome.mutate(tenant.id, {
                onSuccess: () => toast.success(TENANT_ADMIN_LABELS.resend_welcome_success),
                onError: (err) => {
                  const msg = handleApiError(err);
                  toast.error(msg || TENANT_ADMIN_LABELS.resend_welcome_error);
                },
              });
            }}
          >
            {resendWelcome.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Mail className="h-4 w-4" />
            )}
            {TENANT_ADMIN_LABELS.action_resend_welcome}
          </Button>
          <Button variant="outline" size="sm" className="min-h-11 gap-1.5" asChild>
            <Link href={`/super-admin/tenants/${tenant.slug}/edit` as Route}>
              <Pencil className="h-4 w-4" />
              {TENANT_ADMIN_LABELS.action_edit}
            </Link>
          </Button>
          <Button variant="outline" size="sm" className="min-h-11 gap-1.5" asChild>
            <Link href={`/super-admin/tenants/${tenant.slug}/settings` as Route}>
              <Settings className="h-4 w-4" />
              {TENANT_ADMIN_LABELS.action_settings}
            </Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.detail_workspace_card}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_status}
              </span>
              <span className="font-medium">{tenant.status}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_tier}
              </span>
              <span className="font-medium">{tenant.tier}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_region}
              </span>
              <span className="font-medium">{tenant.region}</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_products}
              </span>
              <span className="font-medium text-right">{tenant.products.join(", ")}</span>
            </div>
            <div className="flex justify-between gap-4 text-xs font-mono break-all">
              <span className="text-muted-foreground shrink-0">
                {TENANT_ADMIN_LABELS.detail_label_id}
              </span>
              <span>{tenant.id}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.detail_primary_contact_card}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_name}
              </span>
              <span className="font-medium text-right">
                {pc.first_name ?? TENANT_ADMIN_LABELS.detail_value_empty}{" "}
                {pc.last_name ?? ""}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_email}
              </span>
              <span className="font-medium text-right break-all">
                {pc.email ?? TENANT_ADMIN_LABELS.detail_value_empty}
              </span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-muted-foreground">
                {TENANT_ADMIN_LABELS.detail_label_phone}
              </span>
              <span className="font-medium">
                {pc.phone ?? TENANT_ADMIN_LABELS.detail_value_empty}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{TENANT_ADMIN_LABELS.detail_profile_snapshot}</CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-2 gap-4 text-xs">
          <pre className="rounded-lg border bg-muted/40 p-3 overflow-x-auto font-mono whitespace-pre-wrap">
            {JSON.stringify(companyProfile, null, 2)}
          </pre>
          <pre className="rounded-lg border bg-muted/40 p-3 overflow-x-auto font-mono whitespace-pre-wrap">
            {JSON.stringify(billingProfile, null, 2)}
          </pre>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">{TENANT_ADMIN_LABELS.detail_all_users}</CardTitle>
        </CardHeader>
        <CardContent>
          {usersLoading ? (
            <Skeleton className="h-32 w-full" />
          ) : tenantUsers.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              {TENANT_ADMIN_LABELS.detail_users_empty}
            </p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">
                      {TENANT_ADMIN_LABELS.directory_col_user}
                    </th>
                    <th className="pb-2 pr-4 font-medium">
                      {TENANT_ADMIN_LABELS.directory_col_role}
                    </th>
                    <th className="pb-2 font-medium">
                      {TENANT_ADMIN_LABELS.directory_col_status}
                    </th>
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
                      <td className="py-2 text-muted-foreground">
                        {u.is_active
                          ? TENANT_ADMIN_LABELS.directory_user_status_active
                          : TENANT_ADMIN_LABELS.directory_user_status_inactive}
                      </td>
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
