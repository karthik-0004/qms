"use client";

import Link from "next/link";
import type { Route } from "next";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { TENANT_ADMIN_LABELS } from "@/constants/tenant-admin";
import { handleApiError } from "@/lib/api/client";
import { useTenantBySlug, useTenantSettings, useUpdateTenantSettings } from "@/lib/hooks/queries/platform";
import { tenantSettingsSchema, type TenantSettingsFormValues } from "@/validators/tenant-admin.schema";

export default function TenantSettingsForm({ slug }: { slug: string }) {
  const { data: tenant, isLoading: tLoad, isError: tErr } = useTenantBySlug(slug);
  const { data: settings, isLoading: sLoad } = useTenantSettings(tenant?.id);
  const update = useUpdateTenantSettings();
  const [banner, setBanner] = useState<{ type: "ok" | "err"; msg: string } | null>(null);

  const form = useForm<TenantSettingsFormValues>({
    resolver: zodResolver(tenantSettingsSchema),
    defaultValues: {
      max_users: 50,
      max_storage_gb: 10,
      timezone: "UTC",
      locale: "en-US",
    },
  });

  useEffect(() => {
    if (settings) {
      form.reset({
        max_users: settings.max_users,
        max_storage_gb: settings.max_storage_gb,
        timezone: settings.timezone,
        locale: settings.locale,
      });
    }
  }, [settings, form]);

  const onSubmit = async (values: TenantSettingsFormValues) => {
    if (!tenant) return;
    try {
      await update.mutateAsync({
        tenantId: tenant.id,
        data: {
          max_users: values.max_users,
          max_storage_gb: values.max_storage_gb,
          timezone: values.timezone,
          locale: values.locale,
        },
      });
      setBanner({ type: "ok", msg: TENANT_ADMIN_LABELS.settings_saved });
    } catch (e) {
      setBanner({ type: "err", msg: handleApiError(e) });
    }
  };

  if (tLoad || (tenant && sLoad)) {
    return (
      <div className="space-y-4 max-w-xl">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-56 w-full" />
      </div>
    );
  }

  if (tErr || !tenant) {
    return (
      <Card>
        <CardContent className="pt-6 text-sm text-muted-foreground">
          Tenant not found.
          <Button variant="link" className="px-1" asChild>
            <Link href={"/admin/tenants" as Route}>Back</Link>
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6 max-w-xl mx-auto">
      <div className="flex items-start gap-3">
        <Button variant="outline" size="icon" className="shrink-0 min-h-11 min-w-11" asChild>
          <Link href={`/admin/tenants/${tenant.slug}` as Route} aria-label={TENANT_ADMIN_LABELS.back_to_list}>
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{TENANT_ADMIN_LABELS.settings_title}</h1>
          <p className="text-sm text-muted-foreground mt-1 font-mono">{tenant.slug}</p>
        </div>
      </div>

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {banner?.type === "ok" && (
          <p className="text-sm text-green-700 dark:text-green-400">{banner.msg}</p>
        )}
        {banner?.type === "err" && <p className="text-sm text-red-600">{banner.msg}</p>}

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.card_limits_locale}</CardTitle>
          </CardHeader>
          <CardContent className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="mu">{TENANT_ADMIN_LABELS.field_max_users}</Label>
              <Input id="mu" type="number" className="min-h-11" {...form.register("max_users")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sg">{TENANT_ADMIN_LABELS.field_max_storage}</Label>
              <Input id="sg" type="number" className="min-h-11" {...form.register("max_storage_gb")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tz">{TENANT_ADMIN_LABELS.field_timezone}</Label>
              <Input id="tz" className="min-h-11" {...form.register("timezone")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="loc">{TENANT_ADMIN_LABELS.field_locale}</Label>
              <Input id="loc" className="min-h-11" {...form.register("locale")} />
            </div>
          </CardContent>
        </Card>

        <div className="flex justify-end gap-2">
          <Button type="button" variant="outline" className="min-h-11" asChild>
            <Link href={`/admin/tenants/${tenant.slug}` as Route}>Cancel</Link>
          </Button>
          <Button type="submit" className="min-h-11" disabled={update.isPending}>
            {update.isPending ? "…" : TENANT_ADMIN_LABELS.action_save}
          </Button>
        </div>
      </form>
    </div>
  );
}
