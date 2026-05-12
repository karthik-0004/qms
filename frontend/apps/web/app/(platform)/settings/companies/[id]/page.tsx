"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  Building2,
  Users,
  Plus,
  ChevronLeft,
  ChevronRight,
  Mail,
  Phone,
  MapPin,
  Hash,
  UserCog,
  Copy,
  Check,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useCompany, useCompanyUsers, useCreateCompanyUser, useCompanyRoles } from "@/lib/hooks/queries/platform";
import { usePermission } from "@/lib/hooks/usePermission";
import type { CompanyUser, CompanyUserCreated } from "@/lib/api/services/platform";

const PAGE_SIZE = 10;

function DetailRow({ icon: Icon, label, value }: { icon: React.ElementType; label: string; value: string | null | undefined }) {
  return (
    <div className="flex items-start gap-3">
      <Icon className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
      <div>
        <p className="text-xs text-muted-foreground">{label}</p>
        <p className="text-sm font-medium">{value ?? "—"}</p>
      </div>
    </div>
  );
}

function AddUserDialog({ companyId, onClose }: { companyId: string; onClose: () => void }) {
  const { data: rolesData } = useCompanyRoles(companyId);
  const { mutateAsync: createUser, isPending } = useCreateCompanyUser(companyId);
  const [form, setForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    display_name: "",
    phone: "",
    department: "",
    role_id: "",
  });
  const [error, setError] = useState<string | null>(null);
  const [created, setCreated] = useState<CompanyUserCreated | null>(null);
  const [copied, setCopied] = useState(false);

  const set = (key: keyof typeof form) => (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
    setForm((prev) => ({ ...prev, [key]: e.target.value }));

  function copyPassword() {
    if (!created) return;
    navigator.clipboard.writeText(created.temporary_password);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const result = await createUser({
        email: form.email,
        first_name: form.first_name,
        last_name: form.last_name,
        display_name: form.display_name || undefined,
        phone: form.phone || undefined,
        department: form.department || undefined,
        role_id: form.role_id || undefined,
      });
      setCreated(result);
    } catch (err: unknown) {
      // Extract human-readable message from backend {detail: {code, message}} shape
      let message = "Failed to add user";
      if (err && typeof err === "object" && "response" in err) {
        const resp = (err as { response?: { data?: { detail?: { message?: string } | string } } }).response;
        const detail = resp?.data?.detail;
        if (detail && typeof detail === "object" && "message" in detail) {
          message = detail.message as string;
        } else if (typeof detail === "string") {
          message = detail;
        } else if (err instanceof Error) {
          message = err.message;
        }
      } else if (err instanceof Error) {
        message = err.message;
      }
      setError(message);
    }
  }

  if (created) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
        <Card className="w-full max-w-md mx-4">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-700">
              <UserCog className="h-5 w-5" />
              User added successfully
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Share these credentials with <strong>{created.user.first_name} {created.user.last_name}</strong>.
            </p>
            <div className="rounded-md border bg-muted/50 p-4 space-y-2">
              <div>
                <p className="text-xs text-muted-foreground">Temporary password</p>
                <div className="flex items-center gap-2 mt-1">
                  <code className="text-sm font-mono bg-background border rounded px-2 py-1 flex-1 select-all">
                    {created.temporary_password}
                  </code>
                  <Button variant="outline" size="sm" onClick={copyPassword} className="shrink-0">
                    {copied ? <Check className="h-4 w-4 text-green-600" /> : <Copy className="h-4 w-4" />}
                  </Button>
                </div>
              </div>
            </div>
            <p className="text-xs text-amber-700 bg-amber-50 border border-amber-200 rounded-md px-3 py-2">
              This password will not be shown again. Copy it before closing.
            </p>
            <div className="flex justify-end">
              <Button onClick={onClose}>Done</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <UserCog className="h-5 w-5" />
            Add Company User
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-3">
            <div className="grid gap-1.5">
              <Label htmlFor="uemail">Email *</Label>
              <Input id="uemail" type="email" required value={form.email} onChange={set("email")} placeholder="user@acme.com" />
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1.5">
                <Label htmlFor="fn">First name *</Label>
                <Input id="fn" required value={form.first_name} onChange={set("first_name")} />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="ln">Last name *</Label>
                <Input id="ln" required value={form.last_name} onChange={set("last_name")} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-2">
              <div className="grid gap-1.5">
                <Label htmlFor="phone">Phone</Label>
                <Input id="phone" value={form.phone} onChange={set("phone")} />
              </div>
              <div className="grid gap-1.5">
                <Label htmlFor="dept">Department</Label>
                <Input id="dept" value={form.department} onChange={set("department")} />
              </div>
            </div>
            <div className="grid gap-1.5">
              <Label htmlFor="dname">Display name</Label>
              <Input id="dname" value={form.display_name} onChange={set("display_name")} placeholder="Optional display name" />
            </div>
            {rolesData && rolesData.length > 0 && (
              <div className="grid gap-1.5">
                <Label htmlFor="role">Permission role</Label>
                <select
                  id="role"
                  value={form.role_id}
                  onChange={set("role_id")}
                  className="h-9 rounded-md border border-input bg-background px-3 text-sm w-full"
                >
                  <option value="">No role (read-only defaults)</option>
                  {rolesData.map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.name}
                    </option>
                  ))}
                </select>
              </div>
            )}
            {error && (
              <p className="text-xs text-destructive">{error}</p>
            )}
            <div className="flex justify-end gap-2 pt-2">
              <Button variant="outline" type="button" onClick={onClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending ? "Adding…" : "Add user"}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

export default function CompanyDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { isTenantAdmin } = usePermission();
  const [page, setPage] = useState(1);
  const [showAddUser, setShowAddUser] = useState(false);

  const { data: company, isLoading: loadingCompany } = useCompany(id);
  const { data: usersData, isLoading: loadingUsers } = useCompanyUsers(id, {
    page,
    page_size: PAGE_SIZE,
  });

  const users: CompanyUser[] = usersData?.items ?? [];
  const totalItems = usersData?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex items-center gap-3">
        {isTenantAdmin && (
          <Button variant="ghost" size="sm" asChild>
            <Link href="/settings/companies">
              <ArrowLeft className="h-4 w-4" />
            </Link>
          </Button>
        )}
        <div>
          {loadingCompany ? (
            <Skeleton className="h-7 w-48" />
          ) : (
            <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
              <Building2 className="h-6 w-6" />
              {company?.name}
            </h1>
          )}
          <p className="text-muted-foreground text-sm mt-1">Company details and user management</p>
        </div>
      </div>

      {/* Company info card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Company information</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingCompany ? (
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}
            </div>
          ) : company ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              <DetailRow icon={Mail} label="Email" value={company.email} />
              <DetailRow icon={Phone} label="Phone" value={company.phone} />
              <DetailRow icon={Hash} label="Code" value={company.company_code} />
              <DetailRow icon={MapPin} label="Address" value={company.address} />
              <DetailRow icon={Users} label="Employee limit" value={String(company.employee_limit)} />
              <DetailRow
                icon={Building2}
                label="Status"
                value={company.status.charAt(0).toUpperCase() + company.status.slice(1)}
              />
            </div>
          ) : null}
        </CardContent>
      </Card>

      {/* Users table */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-base">
            {loadingUsers ? "Loading users…" : `${totalItems} users`}
          </CardTitle>
          <Button size="sm" className="gap-1.5" onClick={() => setShowAddUser(true)}>
            <Plus className="h-4 w-4" />
            Add user
          </Button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Name</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Department</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Job title</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Joined</th>
                </tr>
              </thead>
              <tbody>
                {loadingUsers
                  ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                      <tr key={i} className="border-b">
                        {Array.from({ length: 5 }).map((_, j) => (
                          <td key={j} className="py-3 pr-4">
                            <Skeleton className="h-4 w-24" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : users.map((user) => (
                      <tr key={user.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                        <td className="py-3 pr-4">
                          <p className="font-medium">
                            {user.first_name} {user.last_name}
                          </p>
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">
                          {user.department ?? "—"}
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">
                          {user.job_title ?? "—"}
                        </td>
                        <td className="py-3 pr-4">
                          <span
                            className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                              user.is_active
                                ? "bg-green-100 text-green-700"
                                : "bg-slate-100 text-slate-500"
                            }`}
                          >
                            {user.is_active ? "Active" : "Inactive"}
                          </span>
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground text-xs hidden lg:table-cell">
                          {new Date(user.created_at).toLocaleDateString()}
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>
          {!loadingUsers && totalItems > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">
                Page {page} of {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {showAddUser && (
        <AddUserDialog companyId={id} onClose={() => setShowAddUser(false)} />
      )}
    </div>
  );
}
