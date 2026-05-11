"use client";

import Link from "next/link";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronLeft } from "lucide-react";
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { TENANT_ADMIN_LABELS, TENANT_PRODUCT_IDS } from "@/constants/tenant-admin";
import { handleApiError } from "@/lib/api/client";
import {
  useDeleteTenant,
  useTenantBySlug,
  useUpdateTenant,
} from "@/lib/hooks/queries/platform";
import { tenantUpdateSchema, type TenantUpdateFormValues } from "@/validators/tenant-admin.schema";

export default function TenantEditForm({ slug }: { slug: string }) {
  const router = useRouter();
  const { data: tenant, isLoading, isError } = useTenantBySlug(slug);
  const update = useUpdateTenant();
  const del = useDeleteTenant();
  const [deleteOpen, setDeleteOpen] = useState(false);

  const form = useForm<TenantUpdateFormValues>({
    resolver: zodResolver(tenantUpdateSchema),
    defaultValues: {
      tenant_name: "",
      tier: "starter",
      products: [],
    },
  });

  useEffect(() => {
    if (tenant) {
      form.reset({
        tenant_name: tenant.tenant_name,
        tier: tenant.tier as TenantUpdateFormValues["tier"],
        products: tenant.products as TenantUpdateFormValues["products"],
      });
    }
  }, [tenant, form]);

  const toggleProduct = (p: string) => {
    const cur = form.getValues("products") ?? [];
    form.setValue(
      "products",
      cur.includes(p as never) ? cur.filter((x) => x !== p) : [...cur, p as never],
      { shouldValidate: true }
    );
  };

  const onSubmit = async (values: TenantUpdateFormValues) => {
    if (!tenant) return;
    try {
      await update.mutateAsync({ id: tenant.id, data: values });
      router.push(`/admin/tenants/${tenant.slug}` as Route);
    } catch (e) {
      form.setError("root", { message: handleApiError(e) });
    }
  };

  const confirmDelete = async () => {
    if (!tenant) return;
    try {
      await del.mutateAsync(tenant.id);
      setDeleteOpen(false);
      router.push("/admin/tenants" as Route);
    } catch (e) {
      form.setError("root", { message: handleApiError(e) });
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-3xl">
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    );
  }

  if (isError || !tenant) {
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
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-start gap-3">
        <Button variant="outline" size="icon" className="shrink-0 min-h-11 min-w-11" asChild>
          <Link href={`/admin/tenants/${tenant.slug}` as Route} aria-label={TENANT_ADMIN_LABELS.back_to_list}>
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{TENANT_ADMIN_LABELS.action_edit}</h1>
          <p className="text-sm text-muted-foreground mt-1 font-mono">{tenant.slug}</p>
        </div>
      </div>

      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {form.formState.errors.root?.message && (
          <p className="text-sm text-red-600">{form.formState.errors.root.message}</p>
        )}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.section_core}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="tenant_name">{TENANT_ADMIN_LABELS.field_workspace_name}</Label>
              <Input id="tenant_name" className="min-h-11" {...form.register("tenant_name")} />
              {form.formState.errors.tenant_name && (
                <p className="text-xs text-red-600">{form.formState.errors.tenant_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label>{TENANT_ADMIN_LABELS.field_products}</Label>
              <div className="flex flex-wrap gap-4">
                {(TENANT_PRODUCT_IDS as unknown as string[]).map((p) => (
                  <label key={p} className="flex items-center gap-2 cursor-pointer text-sm min-h-11">
                    <Checkbox
                      checked={form.watch("products")?.includes(p as never)}
                      onCheckedChange={() => toggleProduct(p)}
                    />
                    <span className="font-medium uppercase">{p}</span>
                  </label>
                ))}
              </div>
            </div>
            <div className="space-y-2 max-w-xs">
              <Label htmlFor="tier">{TENANT_ADMIN_LABELS.field_tier}</Label>
              <select
                id="tier"
                className="flex h-11 w-full rounded-md border border-input bg-background px-3 text-sm"
                {...form.register("tier")}
              >
                <option value="starter">{TENANT_ADMIN_LABELS.tier_starter}</option>
                <option value="professional">{TENANT_ADMIN_LABELS.tier_professional}</option>
                <option value="enterprise">{TENANT_ADMIN_LABELS.tier_enterprise}</option>
              </select>
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3 justify-between">
          <Button type="button" variant="destructive" className="min-h-11" onClick={() => setDeleteOpen(true)}>
            {TENANT_ADMIN_LABELS.action_delete_tenant}
          </Button>
          <div className="flex gap-2">
            <Button type="button" variant="outline" className="min-h-11" asChild>
              <Link href={`/admin/tenants/${tenant.slug}` as Route}>Cancel</Link>
            </Button>
            <Button type="submit" className="min-h-11" disabled={update.isPending}>
              {update.isPending ? "…" : TENANT_ADMIN_LABELS.action_save}
            </Button>
          </div>
        </div>
      </form>

      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>{TENANT_ADMIN_LABELS.delete_confirm_title}</DialogTitle>
            <DialogDescription>{TENANT_ADMIN_LABELS.delete_confirm_desc}</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button type="button" variant="destructive" onClick={confirmDelete} disabled={del.isPending}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
