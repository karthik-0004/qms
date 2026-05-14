"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import {
  Users,
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  MoreHorizontal,
  UserPlus,
  Pencil,
  UserX,
  UserCheck,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  useUsers,
  useCreateUser,
  useUpdateUser,
  useDeactivateUser,
} from "@/lib/hooks/queries/platform";
import type { User } from "@/lib/api/services/platform";
import { usePermission } from "@/lib/hooks/usePermission";

const ROLE_CONFIG: Record<string, { label: string; color: string }> = {
  super_admin: { label: "Super Admin", color: "bg-red-100 text-red-700" },
  tenant_admin: { label: "Tenant Admin", color: "bg-purple-100 text-purple-700" },
  tenant_user: { label: "User", color: "bg-blue-100 text-blue-700" },
  company_admin: { label: "Company Admin", color: "bg-amber-100 text-amber-700" },
  company_user: { label: "Company User", color: "bg-green-100 text-green-700" },
};

const PAGE_SIZE = 10;

const INVITABLE_ROLES = [
  { value: "tenant_user", label: "Tenant User" },
  { value: "tenant_admin", label: "Tenant Admin" },
];

// ─── Create User Dialog ───────────────────────────────────────────────────────

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
  });
  const [error, setError] = useState<string | null>(null);

  const set = (key: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      await createUser({
        email: form.email,
        first_name: form.first_name,
        last_name: form.last_name,
        display_name: form.display_name || undefined,
        phone: form.phone || undefined,
        department: form.department || undefined,
        job_title: form.job_title || undefined,
      });
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create user");
    }
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <UserPlus className="h-5 w-5 text-primary" />
            Create User
          </DialogTitle>
          <DialogDescription>
            A welcome email with a temporary password will be sent to the user.
          </DialogDescription>
        </DialogHeader>
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
            <Input id="iu-dn" value={form.display_name} onChange={set("display_name")} placeholder="Optional" />
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="iu-email">Email *</Label>
            <Input id="iu-email" type="email" required value={form.email} onChange={set("email")} placeholder="user@company.com" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="iu-phone">Phone</Label>
              <Input id="iu-phone" value={form.phone} onChange={set("phone")} placeholder="+1-555-0123" />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="iu-dept">Department</Label>
              <Input id="iu-dept" value={form.department} onChange={set("department")} placeholder="Engineering" />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="iu-title">Job title</Label>
            <Input id="iu-title" value={form.job_title} onChange={set("job_title")} placeholder="Software Engineer" />
          </div>
          {error && <p className="text-xs text-destructive">{error}</p>}
          <DialogFooter>
            <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? <><Loader2 className="h-4 w-4 animate-spin mr-1" />Creating…</> : "Create user"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── Edit User Dialog ─────────────────────────────────────────────────────────

function EditUserDialog({ user, onClose }: { user: User; onClose: () => void }) {
  const { mutateAsync: updateUser, isPending } = useUpdateUser();
  const [form, setForm] = useState({
    first_name: user.first_name,
    last_name: user.last_name,
    display_name: user.display_name ?? "",
    phone: user.phone ?? "",
    department: user.department ?? "",
    job_title: user.job_title ?? "",
  });

  const set = (key: keyof typeof form) =>
    (e: React.ChangeEvent<HTMLInputElement>) =>
      setForm((prev) => ({ ...prev, [key]: e.target.value }));

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      await updateUser({
        id: user.id,
        data: {
          first_name: form.first_name || undefined,
          last_name: form.last_name || undefined,
          display_name: form.display_name || undefined,
          phone: form.phone || undefined,
          department: form.department || undefined,
          job_title: form.job_title || undefined,
        },
      });
      onClose();
    } catch {
      // toast handled by hook
    }
  }

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Pencil className="h-5 w-5 text-primary" />
            Edit User
          </DialogTitle>
          <DialogDescription>
            Update profile for {user.first_name} {user.last_name}
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="eu-fn">First name *</Label>
              <Input id="eu-fn" required value={form.first_name} onChange={set("first_name")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="eu-ln">Last name *</Label>
              <Input id="eu-ln" required value={form.last_name} onChange={set("last_name")} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="eu-dn">Display name</Label>
            <Input id="eu-dn" value={form.display_name} onChange={set("display_name")} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1.5">
              <Label htmlFor="eu-phone">Phone</Label>
              <Input id="eu-phone" value={form.phone} onChange={set("phone")} />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="eu-dept">Department</Label>
              <Input id="eu-dept" value={form.department} onChange={set("department")} />
            </div>
          </div>
          <div className="space-y-1.5">
            <Label htmlFor="eu-title">Job title</Label>
            <Input id="eu-title" value={form.job_title} onChange={set("job_title")} />
          </div>
          <DialogFooter>
            <Button variant="outline" type="button" onClick={onClose}>Cancel</Button>
            <Button type="submit" disabled={isPending}>
              {isPending ? <><Loader2 className="h-4 w-4 animate-spin mr-1" />Saving…</> : "Save changes"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

// ─── Deactivate Confirm Dialog ────────────────────────────────────────────────

function DeactivateDialog({
  user,
  onClose,
}: {
  user: User;
  onClose: () => void;
}) {
  const { mutateAsync: deactivate, isPending } = useDeactivateUser();

  async function handleConfirm() {
    try {
      await deactivate(user.id);
      onClose();
    } catch {
      // toast handled by hook
    }
  }

  return (
    <AlertDialog open onOpenChange={(open) => !open && onClose()}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>Deactivate user?</AlertDialogTitle>
          <AlertDialogDescription>
            This will deactivate{" "}
            <span className="font-semibold">
              {user.first_name} {user.last_name}
            </span>
            . They will no longer be able to sign in. This action can be reversed by an admin.
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isPending}
            className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
          >
            {isPending ? <><Loader2 className="h-4 w-4 animate-spin mr-1" />Deactivating…</> : "Deactivate"}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

// ─── Row Action Menu ──────────────────────────────────────────────────────────

function RowActions({
  user,
  currentUserId,
  canEdit,
}: {
  user: User;
  currentUserId: string;
  canEdit: boolean;
}) {
  const [open, setOpen] = useState(false);
  const [showEdit, setShowEdit] = useState(false);
  const [showDeactivate, setShowDeactivate] = useState(false);
  const isSelf = user.id === currentUserId;

  if (!canEdit) return null;

  return (
    <>
      <div className="relative">
        <Button
          variant="ghost"
          size="sm"
          onClick={(e) => {
            e.stopPropagation();
            setOpen((v) => !v);
          }}
          aria-label="User actions"
        >
          <MoreHorizontal className="h-4 w-4" />
        </Button>
        {open && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 z-10"
              onClick={(e) => {
                e.stopPropagation();
                setOpen(false);
              }}
            />
            <div className="absolute right-0 top-8 z-20 w-40 rounded-md border bg-background shadow-md py-1">
              <button
                className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted flex items-center gap-2"
                onClick={(e) => {
                  e.stopPropagation();
                  setOpen(false);
                  setShowEdit(true);
                }}
              >
                <Pencil className="h-3.5 w-3.5" />
                Edit
              </button>
              {user.is_active && !isSelf && (
                <button
                  className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted flex items-center gap-2 text-destructive"
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpen(false);
                    setShowDeactivate(true);
                  }}
                >
                  <UserX className="h-3.5 w-3.5" />
                  Deactivate
                </button>
              )}
              {!user.is_active && (
                <button
                  className="w-full text-left px-3 py-1.5 text-sm hover:bg-muted flex items-center gap-2 text-muted-foreground cursor-not-allowed"
                  disabled
                  title="Reactivate endpoint not yet available"
                  onClick={(e) => e.stopPropagation()}
                >
                  <UserCheck className="h-3.5 w-3.5" />
                  Reactivate
                  {/* TODO: Wire when reactivate endpoint is implemented */}
                </button>
              )}
            </div>
          </>
        )}
      </div>

      {showEdit && <EditUserDialog user={user} onClose={() => setShowEdit(false)} />}
      {showDeactivate && <DeactivateDialog user={user} onClose={() => setShowDeactivate(false)} />}
    </>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function UsersPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const { isTenantAdmin, isSuperAdmin } = usePermission();
  const canEdit = isTenantAdmin || isSuperAdmin;

  const currentUserId = (session?.user as { id?: string } | undefined)?.id ?? "";

  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showCreate, setShowCreate] = useState(false);

  const { data, isLoading: loading } = useUsers({
    page,
    page_size: PAGE_SIZE,
  });

  const users: User[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  // Client-side search filter (API doesn't have a search param in spec)
  const filtered = search.trim()
    ? users.filter((u) => {
        const q = search.toLowerCase();
        return (
          u.first_name.toLowerCase().includes(q) ||
          u.last_name.toLowerCase().includes(q) ||
          (u.display_name ?? "").toLowerCase().includes(q) ||
          (u.department ?? "").toLowerCase().includes(q)
        );
      })
    : users;

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
        {canEdit && (
          <Button size="sm" className="gap-1.5" onClick={() => setShowCreate(true)}>
            <Plus className="h-4 w-4" />
            Create User
          </Button>
        )}
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name or department..."
              className="pl-8"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
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
                        {Array.from({ length: 5 }).map((_, j) => (
                          <td key={j} className="py-3 pr-4">
                            <Skeleton className="h-4 w-24" />
                          </td>
                        ))}
                      </tr>
                    ))
                  : filtered.map((u) => {
                      const isActive = u.is_active;
                      return (
                        <tr
                          key={u.id}
                          className="border-b last:border-0 hover:bg-muted/50 transition-colors cursor-pointer"
                          onClick={() => router.push(`/settings/users/${u.id}` as any)}
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
                                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                                  <span className="text-xs font-medium text-primary">
                                    {u.first_name?.[0]?.toUpperCase() ?? "U"}
                                  </span>
                                </div>
                              )}
                              <div>
                                <p className="font-medium">
                                  {u.display_name || `${u.first_name} ${u.last_name}`}
                                </p>
                                {u.job_title && (
                                  <p className="text-xs text-muted-foreground">{u.job_title}</p>
                                )}
                              </div>
                            </div>
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                                isActive
                                  ? "bg-green-100 text-green-700"
                                  : "bg-slate-100 text-slate-500"
                              }`}
                            >
                              {isActive ? "Active" : "Inactive"}
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
                          <td className="py-3" onClick={(e) => e.stopPropagation()}>
                            <RowActions
                              user={u}
                              currentUserId={currentUserId}
                              canEdit={canEdit}
                            />
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
