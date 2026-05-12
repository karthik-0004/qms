"use client";

import Link from "next/link";
import type { Route } from "next";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChevronLeft } from "lucide-react";
import { useForm } from "react-hook-form";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { TENANT_ADMIN_LABELS, TENANT_PRODUCT_IDS, TENANT_REGION_OPTIONS } from "@/constants/tenant-admin";
import { handleApiError } from "@/lib/api/client";
import type { CreateTenantPayload } from "@/lib/api/services/platform";
import { useCreateTenant } from "@/lib/hooks/queries/platform";
import { tenantCreateSchema, type TenantCreateFormValues } from "@/validators/tenant-admin.schema";

function anyOptionalField(...vals: (string | undefined)[]): boolean {
  return vals.some((v) => typeof v === "string" && v.trim().length > 0);
}

function toCreatePayload(values: TenantCreateFormValues): CreateTenantPayload {
  const payload: CreateTenantPayload = {
    tenant_name: values.tenant_name,
    products: values.products,
    tier: values.tier,
    region: values.region,
    primary_contact: {
      first_name: values.primary_first_name,
      last_name: values.primary_last_name,
      email: values.primary_email,
    },
    tenant_defaults: {
      timezone: values.tenant_timezone,
      locale: values.tenant_locale,
    },
  };
  if (values.primary_phone) payload.primary_contact.phone = values.primary_phone;

  if (
    anyOptionalField(values.company_website, values.company_industry, values.company_notes)
  ) {
    payload.company = {};
    if (values.company_website) payload.company.website = values.company_website;
    if (values.company_industry) payload.company.industry = values.company_industry;
    if (values.company_notes) payload.company.notes = values.company_notes;
  }

  if (
    anyOptionalField(
      values.address_line1,
      values.address_line2,
      values.city,
      values.state,
      values.country,
      values.postal_code
    )
  ) {
    payload.address = {};
    if (values.address_line1) payload.address.address_line1 = values.address_line1;
    if (values.address_line2) payload.address.address_line2 = values.address_line2;
    if (values.city) payload.address.city = values.city;
    if (values.state) payload.address.state = values.state;
    if (values.country) payload.address.country = values.country;
    if (values.postal_code) payload.address.postal_code = values.postal_code;
  }

  const needsBilling =
    anyOptionalField(values.billing_email, values.billing_phone, values.tax_id) ||
    !values.billing_address_same_as_address ||
    anyOptionalField(
      values.billing_address_line1,
      values.billing_address_line2,
      values.billing_city,
      values.billing_state,
      values.billing_country,
      values.billing_postal_code
    );

  if (needsBilling) {
    payload.billing = {
      billing_address_same_as_address: values.billing_address_same_as_address,
    };
    if (values.billing_email) payload.billing.billing_email = values.billing_email;
    if (values.billing_phone) payload.billing.billing_phone = values.billing_phone;
    if (values.tax_id) payload.billing.tax_id = values.tax_id;
    if (!values.billing_address_same_as_address) {
      payload.billing.billing_address = {};
      if (values.billing_address_line1) payload.billing.billing_address.address_line1 = values.billing_address_line1;
      if (values.billing_address_line2) payload.billing.billing_address.address_line2 = values.billing_address_line2;
      if (values.billing_city) payload.billing.billing_address.city = values.billing_city;
      if (values.billing_state) payload.billing.billing_address.state = values.billing_state;
      if (values.billing_country) payload.billing.billing_address.country = values.billing_country;
      if (values.billing_postal_code) payload.billing.billing_address.postal_code = values.billing_postal_code;
    }
  }

  return payload;
}

export default function TenantCreateForm() {
  const router = useRouter();
  const create = useCreateTenant();
  const form = useForm<TenantCreateFormValues>({
    resolver: zodResolver(tenantCreateSchema),
    defaultValues: {
      tenant_name: "",
      products: ["qms"],
      tier: "starter",
      region: TENANT_REGION_OPTIONS[0].value,
      primary_first_name: "",
      primary_last_name: "",
      primary_email: "",
      primary_phone: "",
      company_website: "",
      company_industry: "",
      company_notes: "",
      address_line1: "",
      address_line2: "",
      city: "",
      state: "",
      country: "",
      postal_code: "",
      billing_email: "",
      billing_phone: "",
      tax_id: "",
      billing_address_same_as_address: true,
      billing_address_line1: "",
      billing_address_line2: "",
      billing_city: "",
      billing_state: "",
      billing_country: "",
      billing_postal_code: "",
      tenant_timezone: "UTC",
      tenant_locale: "en-US",
    },
  });

  const sameBilling = form.watch("billing_address_same_as_address");
  const tier = form.watch("tier");
  const region = form.watch("region");

  const onSubmit = async (values: TenantCreateFormValues) => {
    try {
      const tenant = await create.mutateAsync(toCreatePayload(values));
      router.push(`/super-admin/tenants/${tenant.slug}` as Route);
    } catch (e) {
      form.setError("root", { message: handleApiError(e) });
    }
  };

  const toggleProduct = (p: string) => {
    const cur = form.getValues("products") ?? [];
    form.setValue(
      "products",
      cur.includes(p) ? cur.filter((x) => x !== p) : [...cur, p],
      { shouldValidate: true }
    );
  };

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      <div className="flex items-start gap-3">
        <Button variant="outline" size="icon" className="shrink-0 min-h-11 min-w-11" asChild>
          <Link href={"/super-admin/tenants" as Route} aria-label={TENANT_ADMIN_LABELS.back_to_list}>
            <ChevronLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{TENANT_ADMIN_LABELS.submitCreate}</h1>
          <p className="text-sm text-muted-foreground mt-1">{TENANT_ADMIN_LABELS.listSubtitle}</p>
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
                      checked={form.watch("products")?.includes(p)}
                      onCheckedChange={() => toggleProduct(p)}
                    />
                    <span className="font-medium uppercase">{p}</span>
                  </label>
                ))}
              </div>
              {form.formState.errors.products && (
                <p className="text-xs text-red-600">{form.formState.errors.products.message}</p>
              )}
            </div>
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tier">{TENANT_ADMIN_LABELS.field_tier}</Label>
                <select
                  id="tier"
                  className="flex h-11 w-full rounded-md border border-input bg-background px-3 text-sm"
                  value={tier}
                  onChange={(e) => form.setValue("tier", e.target.value as TenantCreateFormValues["tier"])}
                >
                  <option value="starter">{TENANT_ADMIN_LABELS.tier_starter}</option>
                  <option value="professional">{TENANT_ADMIN_LABELS.tier_professional}</option>
                  <option value="enterprise">{TENANT_ADMIN_LABELS.tier_enterprise}</option>
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="region">{TENANT_ADMIN_LABELS.field_region}</Label>
                <select
                  id="region"
                  className="flex h-11 w-full rounded-md border border-input bg-background px-3 text-sm"
                  value={region}
                  onChange={(e) =>
                    form.setValue("region", e.target.value as TenantCreateFormValues["region"])
                  }
                >
                  {TENANT_REGION_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {TENANT_ADMIN_LABELS[opt.labelKey as keyof typeof TENANT_ADMIN_LABELS]}
                    </option>
                  ))}
                </select>
                {form.formState.errors.region && (
                  <p className="text-xs text-red-600">{form.formState.errors.region.message}</p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.section_contact}</CardTitle>
          </CardHeader>
          <CardContent className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="pf">{TENANT_ADMIN_LABELS.field_primary_first_name}</Label>
              <Input id="pf" className="min-h-11" {...form.register("primary_first_name")} />
              {form.formState.errors.primary_first_name && (
                <p className="text-xs text-red-600">{form.formState.errors.primary_first_name.message}</p>
              )}
            </div>
            <div className="space-y-2">
              <Label htmlFor="pl">{TENANT_ADMIN_LABELS.field_primary_last_name}</Label>
              <Input id="pl" className="min-h-11" {...form.register("primary_last_name")} />
              {form.formState.errors.primary_last_name && (
                <p className="text-xs text-red-600">{form.formState.errors.primary_last_name.message}</p>
              )}
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="pe">{TENANT_ADMIN_LABELS.field_primary_email}</Label>
              <Input id="pe" type="email" className="min-h-11" autoComplete="email" {...form.register("primary_email")} />
              {form.formState.errors.primary_email && (
                <p className="text-xs text-red-600">{form.formState.errors.primary_email.message}</p>
              )}
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="pp">{TENANT_ADMIN_LABELS.field_primary_phone}</Label>
              <Input id="pp" className="min-h-11" {...form.register("primary_phone")} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.section_company}</CardTitle>
          </CardHeader>
          <CardContent className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="cw">{TENANT_ADMIN_LABELS.field_company_website}</Label>
              <Input id="cw" className="min-h-11" {...form.register("company_website")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ci">{TENANT_ADMIN_LABELS.field_company_industry}</Label>
              <Input id="ci" className="min-h-11" {...form.register("company_industry")} />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="cn">{TENANT_ADMIN_LABELS.field_company_notes}</Label>
              <Input id="cn" className="min-h-11" {...form.register("company_notes")} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.section_address}</CardTitle>
          </CardHeader>
          <CardContent className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="a1">Line 1</Label>
              <Input id="a1" className="min-h-11" {...form.register("address_line1")} />
            </div>
            <div className="space-y-2 sm:col-span-2">
              <Label htmlFor="a2">Line 2</Label>
              <Input id="a2" className="min-h-11" {...form.register("address_line2")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="city">City</Label>
              <Input id="city" className="min-h-11" {...form.register("city")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="state">State</Label>
              <Input id="state" className="min-h-11" {...form.register("state")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input id="country" className="min-h-11" {...form.register("country")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="postal">Postal code</Label>
              <Input id="postal" className="min-h-11" {...form.register("postal_code")} />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.section_billing}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="be">{TENANT_ADMIN_LABELS.field_primary_email} (billing)</Label>
                <Input id="be" type="email" className="min-h-11" {...form.register("billing_email")} />
                {form.formState.errors.billing_email && (
                  <p className="text-xs text-red-600">{form.formState.errors.billing_email.message}</p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="bp">{TENANT_ADMIN_LABELS.field_primary_phone} (billing)</Label>
                <Input id="bp" className="min-h-11" {...form.register("billing_phone")} />
              </div>
              <div className="space-y-2 sm:col-span-2">
                <Label htmlFor="tax">Tax ID</Label>
                <Input id="tax" className="min-h-11" {...form.register("tax_id")} />
              </div>
            </div>
            <div className="flex items-center gap-3 min-h-11">
              <Switch
                id="sameBill"
                checked={sameBilling}
                onCheckedChange={(c) => form.setValue("billing_address_same_as_address", Boolean(c))}
              />
              <Label htmlFor="sameBill">{TENANT_ADMIN_LABELS.billing_same_as_primary}</Label>
            </div>
            {!sameBilling && (
              <div className="grid sm:grid-cols-2 gap-4 pt-2 border-t">
                <div className="space-y-2 sm:col-span-2">
                  <Label>Billing line 1</Label>
                  <Input className="min-h-11" {...form.register("billing_address_line1")} />
                </div>
                <div className="space-y-2 sm:col-span-2">
                  <Label>Billing line 2</Label>
                  <Input className="min-h-11" {...form.register("billing_address_line2")} />
                </div>
                <div className="space-y-2">
                  <Label>Billing city</Label>
                  <Input className="min-h-11" {...form.register("billing_city")} />
                </div>
                <div className="space-y-2">
                  <Label>Billing state</Label>
                  <Input className="min-h-11" {...form.register("billing_state")} />
                </div>
                <div className="space-y-2">
                  <Label>Billing country</Label>
                  <Input className="min-h-11" {...form.register("billing_country")} />
                </div>
                <div className="space-y-2">
                  <Label>Billing postal</Label>
                  <Input className="min-h-11" {...form.register("billing_postal_code")} />
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">{TENANT_ADMIN_LABELS.section_defaults}</CardTitle>
          </CardHeader>
          <CardContent className="grid sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tz">{TENANT_ADMIN_LABELS.field_timezone}</Label>
              <Input id="tz" className="min-h-11" {...form.register("tenant_timezone")} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="loc">{TENANT_ADMIN_LABELS.field_locale}</Label>
              <Input id="loc" className="min-h-11" {...form.register("tenant_locale")} />
            </div>
          </CardContent>
        </Card>

        <div className="flex flex-wrap gap-3 justify-end">
          <Button type="button" variant="outline" className="min-h-11" asChild>
            <Link href={"/super-admin/tenants" as Route}>Cancel</Link>
          </Button>
          <Button type="submit" className="min-h-11" disabled={create.isPending}>
            {create.isPending ? TENANT_ADMIN_LABELS.submitCreating : TENANT_ADMIN_LABELS.submitCreate}
          </Button>
        </div>
      </form>
    </div>
  );
}
