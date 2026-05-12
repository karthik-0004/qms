"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, Building2, Copy, Check } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCreateCompany } from "@/lib/hooks/queries/platform";
import type { CompanyWithAdmin } from "@/lib/api/services/platform";

function SuccessDialog({ result, onDone }: { result: CompanyWithAdmin; onDone: () => void }) {
  const [copied, setCopied] = useState(false);

  function copy() {
    navigator.clipboard.writeText(result.temporary_password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-700">
            <Building2 className="h-5 w-5" />
            Company created successfully
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            <strong>{result.company.name}</strong> has been created. The admin account is ready — share
            these credentials with the company admin.
          </p>
          <div className="rounded-md border bg-muted/50 p-4 space-y-2">
            <div>
              <p className="text-xs text-muted-foreground">Admin name</p>
              <p className="text-sm font-medium">
                {result.admin.first_name} {result.admin.last_name}
              </p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Temporary password</p>
              <div className="flex items-center gap-2 mt-1">
                <code className="text-sm font-mono bg-background border rounded px-2 py-1 flex-1 select-all">
                  {result.temporary_password}
                </code>
                <Button variant="outline" size="sm" onClick={copy} className="shrink-0">
                  {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </div>
          <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
            This password will not be shown again. Make sure to copy it before closing.
          </p>
          <div className="flex justify-end">
            <Button onClick={onDone}>Done</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default function NewCompanyPage() {
  const router = useRouter();
  const { mutateAsync: createCompany, isPending } = useCreateCompany();
  const [result, setResult] = useState<CompanyWithAdmin | null>(null);

  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    company_code: "",
    employee_limit: "10",
    // structured address
    address_line1: "",
    address_line2: "",
    city: "",
    state: "",
    country: "",
    postal_code: "",
    // admin
    admin_email: "",
    admin_first_name: "",
    admin_last_name: "",
    admin_phone: "",
  });
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  function buildAddress(): string | undefined {
    const parts = [
      form.address_line1,
      form.address_line2,
      form.city,
      form.state && form.postal_code ? `${form.state} ${form.postal_code}` : form.state || form.postal_code,
      form.country,
    ].filter(Boolean);
    return parts.length > 0 ? parts.join(", ") : undefined;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const data = await createCompany({
        name: form.name,
        email: form.email,
        phone: form.phone || undefined,
        address: buildAddress(),
        company_code: form.company_code || undefined,
        employee_limit: parseInt(form.employee_limit, 10),
        admin: {
          email: form.admin_email,
          first_name: form.admin_first_name,
          last_name: form.admin_last_name,
          phone: form.admin_phone || undefined,
        },
      });
      setResult(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create company");
    }
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div className="flex items-center gap-3">
        <Button variant="ghost" size="sm" asChild>
          <Link href="/settings/companies">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Building2 className="h-6 w-6" />
            New Company
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Create a company and its initial admin account.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Company Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-1.5">
              <Label htmlFor="name">Company name *</Label>
              <Input id="name" required value={form.name} onChange={set("name")} placeholder="Acme Corp" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="email">Company email *</Label>
              <Input id="email" type="email" required value={form.email} onChange={set("email")} placeholder="contact@acme.com" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" value={form.phone} onChange={set("phone")} placeholder="+1 555 0100" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="employee_limit">Employee limit</Label>
                <Input id="employee_limit" type="number" min="1" max="10000" value={form.employee_limit} onChange={set("employee_limit")} />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="company_code">
                Company code <span className="text-muted-foreground text-xs">(auto-generated if blank)</span>
              </Label>
              <Input id="company_code" value={form.company_code} onChange={set("company_code")} placeholder="ACME-CORP" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Company Address</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid gap-1.5">
              <Label htmlFor="address_line1">Address line 1</Label>
              <Input id="address_line1" value={form.address_line1} onChange={set("address_line1")} placeholder="123 Main Street" />
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="address_line2">Address line 2</Label>
              <Input id="address_line2" value={form.address_line2} onChange={set("address_line2")} placeholder="Suite 100" />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor="city">City</Label>
                <Input id="city" value={form.city} onChange={set("city")} placeholder="New York" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="state">State / Province</Label>
                <Input id="state" value={form.state} onChange={set("state")} placeholder="NY" />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor="country">Country</Label>
                <Input id="country" value={form.country} onChange={set("country")} placeholder="United States" />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="postal_code">Postal code</Label>
                <Input id="postal_code" value={form.postal_code} onChange={set("postal_code")} placeholder="10001" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Company Admin</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              An auth account will be created automatically. A temporary password will be shown after creation.
            </p>
            <div className="grid gap-1.5">
              <Label htmlFor="admin_email">Admin email *</Label>
              <Input
                id="admin_email"
                type="email"
                required
                value={form.admin_email}
                onChange={set("admin_email")}
                placeholder="admin@acme.com"
              />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="grid gap-1.5">
                <Label htmlFor="admin_first_name">First name *</Label>
                <Input id="admin_first_name" required value={form.admin_first_name} onChange={set("admin_first_name")} />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="admin_last_name">Last name *</Label>
                <Input id="admin_last_name" required value={form.admin_last_name} onChange={set("admin_last_name")} />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="admin_phone">Phone</Label>
              <Input id="admin_phone" value={form.admin_phone} onChange={set("admin_phone")} />
            </div>
          </CardContent>
        </Card>

        {error && (
          <p className="text-sm text-destructive rounded-md border border-destructive/30 bg-destructive/10 px-3 py-2">
            {error}
          </p>
        )}

        <div className="flex justify-end gap-3">
          <Button variant="outline" type="button" asChild>
            <Link href="/settings/companies">Cancel</Link>
          </Button>
          <Button type="submit" disabled={isPending}>
            {isPending ? "Creating…" : "Create company"}
          </Button>
        </div>
      </form>

      {result && (
        <SuccessDialog result={result} onDone={() => router.push("/settings/companies")} />
      )}
    </div>
  );
}
