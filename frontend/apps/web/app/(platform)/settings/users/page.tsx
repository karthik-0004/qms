"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import {
  Users,
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  UserPlus,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useUsers, useCreateUser } from "@/lib/hooks/queries/platform";
import type { User } from "@/lib/api/services/platform";
import { toast } from "sonner";

const ROLE_CONFIG: Record<string, { label: string; color: string }> = {
  super_admin: { label: "Super Admin", color: "bg-red-100 text-red-700" },
  tenant_admin: { label: "Tenant Admin", color: "bg-purple-100 text-purple-700" },
  tenant_user: { label: "User", color: "bg-blue-100 text-blue-700" },
  company_admin: { label: "Company Admin", color: "bg-amber-100 text-amber-700" },
  company_user: { label: "Company User", color: "bg-green-100 text-green-700" },
};

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  true: { label: "Active", color: "bg-green-100 text-green-700" },
  false: { label: "Inactive", color: "bg-slate-100 text-slate-500" },
};

const PAGE_SIZE = 10;

// Roles that tenant_admin can invite
const INVITABLE_ROLES = [
  { value: "tenant_user", label: "Tenant User" },
  { value: "tenant_admin", label: "Tenant Admin" },
];

function CreateUserDialog({ onClose }: { onClose: () => void }) {
  const { mutateAsync: createUser, isPending } = useCreateUser();
  const [form, setForm] = useState({
    email: "",
    first_name: "",
    last_name: "",
    display_name: "",
    phone: "",
    department: "",
    job_title: "",
    role: "tenant_user",
  });
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createUser(form);
      toast.success(`User ${form.email} created successfully. Temporary password sent via email.`);
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create user");
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-background rounded-xl border shadow-xl w-full max-w-md mx-4 p-6">
        <div className="flex items-center gap-2 mb-5">
          <UserPlus className="h-5 w-5 text-primary" />
          <h2 className="text-lg font-semibold">Create User</h2>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="iu-fn">First name *</Label>
              <Input id="iu-fn" required value={form.first_name} onChange={set("first_name")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="iu-ln">Last name *</Label>
              <Input id="iu-ln" required value={form.last_name} onChange={set("last_name")} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="iu-dn">Display name</Label>
            <Input
              id="iu-dn"
              value={form.display_name}
              onChange={set("display_name")}
              placeholder="Optional display name"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="iu-email">Email *</Label>
            <Input
              id="iu-email"
              type="email"
              required
              value={form.email}
              onChange={set("email")}
              placeholder="user@company.com"
            />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="iu-phone">Phone</Label>
              <Input
                id="iu-phone"
                value={form.phone}
                onChange={set("phone")}
                placeholder="+1-555-0123"
              />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="iu-dept">Department</Label>
              <Input
                id="iu-dept"
                value={form.department}
                onChange={set("department")}
                placeholder="Engineering"
              />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="iu-title">Job title</Label>
            <Input
              id="iu-title"
              value={form.job_title}
              onChange={set("job_title")}
              placeholder="Software Engineer"
            />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="iu-role">Role *</Label>
            <select
              id="iu-role"
              value={form.role}
              onChange={set("role")}
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
            >
              {INVITABLE_ROLES.map((r) => (
                <option key={r.value} value={r.value}>
                  {r.label}
                </option>
              ))}
            </select>
          </div>
          {error && <p className="text-xs text-destructive">{error}</p>}
          <div className="flex justify-end gap-2 pt-1">
            <Button variant="outline" type="button" onClick={onClose}>
              Cancel
            </Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? "Creating…" : "Create user"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function UsersPage() {
  const { data: session } = useSession();
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);

  const isTenantAdmin = session?.user?.role === "tenant_admin";

  const { data, isLoading: loading } = useUsers({
    search: search || undefined,
    role: roleFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const users: User[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Users className="h-6 w-6" />
            User Management
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage platform users, roles, and permissions
          </p>
        </div>
        {isTenantAdmin && (
          <Button size="sm" className="gap-1.5" onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4" />
            Create User
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by name or email..."
                className="pl-8"
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setPage(1);
                }}
              />
            </div>
            <select
              value={roleFilter}
              onChange={(e) => {
                setRoleFilter(e.target.value);
                setPage(1);
              }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">All Roles</option>
              {Object.entries(ROLE_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>
                  {v.label}
                </option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {loading ? "Loading…" : `${totalItems} users`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">User</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Role</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Department</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Phone</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Created</th>
                  <th className="pb-2 font-medium w-10"></th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                      <tr key={i} className="border-b">
                        {Array.from({ length: 6 }).map((_, j) => (
                          <td key={j} className="py-3 pr-4">
                            <Skeleton className="h-4 w-24" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : users.map((u) => {
                      const sCfg = STATUS_CONFIG[String(u.is_active)] ?? { label: "Unknown", color: "bg-slate-100 text-slate-600" };
                      const rCfg = ROLE_CONFIG[u.role] ?? { label: u.role, color: "bg-slate-100 text-slate-600" };
                      return (
                        <tr
                          key={u.id}
                          className="border-b last:border-0 hover:bg-muted/30 transition-colors"
                        >
                          <td className="py-3 pr-4">
                            <div className="flex items-center gap-3">
                              {u.avatar_url ? (
                                <img
                                  src={u.avatar_url}
                                  alt={`${u.first_name} ${u.last_name}`}
                                  className="h-8 w-8 rounded-full object-cover"
                                />
                              ) : (
                                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                                  <span className="text-xs font-medium text-primary">
                                    {u.first_name?.[0]?.toUpperCase() || "U"}
                                  </span>
                                </div>
                              )}
                              <div>
                                <p className="font-medium">
                                  {u.display_name || `${u.first_name} ${u.last_name}`}
                                </p>
                                <p className="text-xs text-muted-foreground">{u.email}</p>
                                {u.job_title && (
                                  <p className="text-xs text-muted-foreground">{u.job_title}</p>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="py-3 pr-4 hidden sm:table-cell">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${rCfg.color}`}
                            >
                              {rCfg.label}
                            </span>
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${sCfg.color}`}
                            >
                              {sCfg.label}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground text-xs hidden md:table-cell">
                            {u.department || "—"}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground text-xs hidden md:table-cell">
                            {u.phone || "—"}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground text-xs hidden lg:table-cell">
                            {new Date(u.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3">
                            <Button variant="ghost" size="sm">
                              <MoreHorizontal className="h-4 w-4" />
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
              </tbody>
            </table>
          </div>
          {!loading && totalItems > PAGE_SIZE && (
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

      {showCreate && <CreateUserDialog onClose={() => setShowCreate(false)} />}
    </div>
  );
}
