"use client";

import { use, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import {
  ArrowLeft,
  Pencil,
  UserX,
  UserCheck,
  CheckCircle2,
  XCircle,
  Loader2,
  ShieldAlert,
  Clock,
  Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
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
  useUser,
  useUpdateUser,
  useDeactivateUser,
  useUserPermissions,
  useRoles,
  useAssignRole,
  useRemoveRole,
  useUserAuditLogs,
} from "@/lib/hooks/queries/platform";
import { usePermission, type Permission } from "@/lib/hooks/usePermission";
import type { User } from "@/lib/api/services/platform";

// ─── Helpers ──────────────────────────────────────────────────────────────────

function initials(u: User) {
  return `${u.first_name?.[0] ?? ""}${u.last_name?.[0] ?? ""}`.toUpperCase();
}

// ─── Edit Dialog (reused from users list) ────────────────────────────────────

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
          <DialogTitle>Edit Profile</DialogTitle>
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

// ─── Deactivate Dialog ────────────────────────────────────────────────────────

function DeactivateDialog({ user, onClose }: { user: User; onClose: () => void }) {
  const router = useRouter();
  const { mutateAsync: deactivate, isPending } = useDeactivateUser();

  async function handleConfirm() {
    try {
      await deactivate(user.id);
      onClose();
      router.push("/settings/users");
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
            . They will no longer be able to sign in.
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

// ─── Profile Tab ──────────────────────────────────────────────────────────────

function ProfileTab({ user }: { user: User }) {
  const fields: { label: string; value: string | null | undefined }[] = [
    { label: "First Name", value: user.first_name },
    { label: "Last Name", value: user.last_name },
    { label: "Display Name", value: user.display_name },
    { label: "Phone", value: user.phone },
    { label: "Department", value: user.department },
    { label: "Job Title", value: user.job_title },
    { label: "Tenant ID", value: user.tenant_id },
    { label: "Platform User ID", value: user.platform_user_id },
    { label: "Created", value: new Date(user.created_at).toLocaleString() },
    { label: "Last Updated", value: new Date(user.updated_at).toLocaleString() },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
      {fields.map(({ label, value }) => (
        <div key={label} className="space-y-1">
          <p className="text-xs text-muted-foreground font-medium uppercase tracking-wide">{label}</p>
          <p className="text-sm">{value || <span className="text-muted-foreground">—</span>}</p>
        </div>
      ))}
    </div>
  );
}

// ─── Permissions Tab ──────────────────────────────────────────────────────────

// All permissions from usePermission.ts — used for the grid display
const ALL_PERMISSIONS: Permission[] = [
  "tenant:read", "tenant:write", "tenant:delete",
  "user:read", "user:write", "user:delete",
  "role:read", "role:write",
  "audit:read", "audit:export",
  "config:read", "config:write",
  "company:read", "company:write", "company:delete",
  "company_user:read", "company_user:write", "company_user:delete",
  "document:read", "document:write", "document:approve", "document:delete",
  "quality_event:read", "quality_event:write",
  "capa:read", "capa:write", "capa:approve",
  "training:read", "training:write", "training:assign",
  "equipment:read", "equipment:write",
  "plate:read", "plate:write",
  "job:read", "job:write",
  "qa_review:read", "qa_review:write", "qa_review:approve",
  "crm:read", "crm:write",
  "contract:read", "contract:write",
  "workorder:read", "workorder:write", "workorder:execute",
  "certificate:read", "certificate:write", "certificate:issue",
  "billing:read", "billing:write",
  "report:read", "report:generate",
  "analytics:read",
];

function PermissionsTab({
  userId,
  isSelf,
  canEdit,
}: {
  userId: string;
  isSelf: boolean;
  canEdit: boolean;
}) {
  const { data: permsData, isLoading: permsLoading, isError: permsError } = useUserPermissions(userId);
  const { data: roles, isLoading: rolesLoading } = useRoles();
  const { mutate: assignRole, isPending: assigning } = useAssignRole();
  const { mutate: removeRole, isPending: removing } = useRemoveRole();

  const [selectedRoleId, setSelectedRoleId] = useState("");

  const userPermSet = new Set(permsData?.permissions ?? []);

  // Find current role from the roles list by matching permissions
  // (The user-service doesn't return the role name directly in UserPermissionsResponse)
  const currentRole = roles?.find((r) =>
    r.permissions.length > 0 &&
    r.permissions.every((p) => userPermSet.has(p)) &&
    userPermSet.size === r.permissions.length
  );

  function handleSaveRole() {
    if (!selectedRoleId) return;
    // Assign new role; if there's a current role, remove it after
    assignRole(
      { userId, roleId: selectedRoleId },
      {
        onSuccess: () => {
          if (currentRole) {
            removeRole({ userId, roleId: currentRole.id });
          }
          setSelectedRoleId("");
        },
      },
    );
  }

  if (permsLoading || rolesLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => <Skeleton key={i} className="h-8 w-full" />)}
      </div>
    );
  }

  if (permsError) {
    return (
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        <ShieldAlert className="h-4 w-4 inline mr-2" />
        Permission management API not yet available.
        {/* TODO: Wire when permissions endpoints are implemented in user-service */}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Current role */}
      <div>
        <h3 className="text-sm font-semibold mb-2">Current Role</h3>
        {currentRole ? (
          <div className="rounded-md border p-3">
            <p className="font-medium text-sm">{currentRole.name}</p>
            {currentRole.description && (
              <p className="text-xs text-muted-foreground mt-0.5">{currentRole.description}</p>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">No role assigned</p>
        )}
      </div>

      {/* Change role */}
      {canEdit && (
        <div>
          <h3 className="text-sm font-semibold mb-2">Change Role</h3>
          {isSelf ? (
            <p className="text-sm text-muted-foreground italic">
              You cannot change your own role.
            </p>
          ) : (
            <div className="flex gap-2">
              <select
                value={selectedRoleId}
                onChange={(e) => setSelectedRoleId(e.target.value)}
                className="flex-1 h-9 rounded-md border border-input bg-background px-3 text-sm"
              >
                <option value="">Select a role…</option>
                {(roles ?? []).map((r) => (
                  <option key={r.id} value={r.id}>
                    {r.name}
                  </option>
                ))}
              </select>
              <Button
                size="sm"
                onClick={handleSaveRole}
                disabled={!selectedRoleId || assigning || removing}
              >
                {assigning || removing ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Save Role"
                )}
              </Button>
            </div>
          )}
        </div>
      )}

      <Separator />

      {/* Effective permissions grid */}
      <div>
        <h3 className="text-sm font-semibold mb-3">Effective Permissions</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-1.5">
          {ALL_PERMISSIONS.map((perm) => {
            const granted = userPermSet.has(perm);
            return (
              <div
                key={perm}
                className={`flex items-center gap-2 rounded px-2 py-1 text-xs ${
                  granted ? "text-foreground" : "text-muted-foreground"
                }`}
              >
                {granted ? (
                  <CheckCircle2 className="h-3.5 w-3.5 text-green-500 shrink-0" />
                ) : (
                  <XCircle className="h-3.5 w-3.5 text-slate-300 shrink-0" />
                )}
                {perm}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Activity Tab ─────────────────────────────────────────────────────────────

function ActivityTab({ userId }: { userId: string }) {
  const [page, setPage] = useState(1);
  const { data, isLoading, isError } = useUserAuditLogs(userId, page);

  const logs = data?.items ?? [];
  const hasNext = data?.has_next ?? false;
  const hasPrev = data?.has_prev ?? false;

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => <Skeleton key={i} className="h-14 w-full" />)}
      </div>
    );
  }

  if (isError) {
    return (
      <p className="text-sm text-muted-foreground">Failed to load activity. Please try again.</p>
    );
  }

  if (logs.length === 0) {
    return (
      <div className="text-center py-12 text-muted-foreground">
        <Activity className="h-8 w-8 mx-auto mb-2 opacity-40" />
        <p className="text-sm">No activity recorded yet.</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        {logs.map((log) => (
          <div key={log.id} className="flex gap-3 rounded-md border p-3">
            <Clock className="h-4 w-4 text-muted-foreground mt-0.5 shrink-0" />
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium">{log.action}</span>
                {log.resource_type && (
                  <span className="text-xs text-muted-foreground">
                    on {log.resource_type}
                    {log.resource_id ? ` #${log.resource_id.slice(0, 8)}` : ""}
                  </span>
                )}
                <span
                  className={`ml-auto text-xs px-1.5 py-0.5 rounded-full ${
                    log.severity === "high" || log.severity === "critical"
                      ? "bg-red-100 text-red-700"
                      : log.severity === "medium"
                      ? "bg-amber-100 text-amber-700"
                      : "bg-slate-100 text-slate-600"
                  }`}
                >
                  {log.severity}
                </span>
              </div>
              <p className="text-xs text-muted-foreground mt-0.5">
                {new Date(log.created_at).toLocaleString()}
                {log.source_service && ` · ${log.source_service}`}
              </p>
            </div>
          </div>
        ))}
      </div>

      {(hasPrev || hasNext) && (
        <div className="flex justify-between items-center pt-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p - 1)}
            disabled={!hasPrev}
          >
            Previous
          </Button>
          <span className="text-xs text-muted-foreground">Page {page}</span>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setPage((p) => p + 1)}
            disabled={!hasNext}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function UserDetailPage({
  params,
}: {
  params: Promise<{ userId: string }>;
}) {
  const { userId } = use(params);
  const router = useRouter();
  const { data: session } = useSession();
  const { isTenantAdmin, isSuperAdmin } = usePermission();
  const canEdit = isTenantAdmin || isSuperAdmin;

  const currentUserId = (session?.user as { id?: string } | undefined)?.id ?? "";
  const isSelf = userId === currentUserId;

  const { data: user, isLoading, isError } = useUser(userId);

  const [showEdit, setShowEdit] = useState(false);
  const [showDeactivate, setShowDeactivate] = useState(false);

  if (isLoading) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <Skeleton className="h-8 w-32" />
        <div className="flex gap-4">
          <Skeleton className="h-16 w-16 rounded-full" />
          <div className="space-y-2">
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-32" />
          </div>
        </div>
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (isError || !user) {
    return (
      <div className="max-w-4xl mx-auto">
        <Button variant="ghost" size="sm" onClick={() => router.back()} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <p className="text-sm text-destructive">Failed to load user. They may not exist.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Back */}
      <Button
        variant="ghost"
        size="sm"
        onClick={() => router.push("/settings/users")}
        className="h-7 px-2 text-muted-foreground hover:text-foreground"
      >
        <ArrowLeft className="h-4 w-4 mr-1" />
        Back to Users
      </Button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-center gap-4">
          {user.avatar_url ? (
            <img
              src={user.avatar_url}
              alt={initials(user)}
              className="h-16 w-16 rounded-full object-cover"
            />
          ) : (
            <div className="h-16 w-16 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <span className="text-xl font-semibold text-primary">{initials(user)}</span>
            </div>
          )}
          <div>
            <h1 className="text-xl font-bold">
              {user.display_name || `${user.first_name} ${user.last_name}`}
            </h1>
            {user.job_title && (
              <p className="text-sm text-muted-foreground">{user.job_title}</p>
            )}
            {user.department && (
              <p className="text-xs text-muted-foreground">{user.department}</p>
            )}
            <div className="flex items-center gap-2 mt-1">
              <span
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
                  user.is_active
                    ? "bg-green-100 text-green-700"
                    : "bg-slate-100 text-slate-500"
                }`}
              >
                {user.is_active ? "Active" : "Inactive"}
              </span>
              <span className="text-xs text-muted-foreground">
                Joined {new Date(user.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {canEdit && (
          <div className="flex gap-2 shrink-0">
            <Button
              variant="outline"
              size="sm"
              className="gap-1.5"
              onClick={() => setShowEdit(true)}
            >
              <Pencil className="h-4 w-4" />
              Edit Profile
            </Button>
            {user.is_active && !isSelf && (
              <Button
                variant="outline"
                size="sm"
                className="gap-1.5 text-destructive border-destructive/30 hover:bg-destructive/10"
                onClick={() => setShowDeactivate(true)}
              >
                <UserX className="h-4 w-4" />
                Deactivate
              </Button>
            )}
            {!user.is_active && (
              <Button
                variant="outline"
                size="sm"
                className="gap-1.5"
                disabled
                title="Reactivate endpoint not yet available"
              >
                <UserCheck className="h-4 w-4" />
                Reactivate
                {/* TODO: Wire when reactivate endpoint is implemented in user-service */}
              </Button>
            )}
          </div>
        )}
      </div>

      {/* Tabs */}
      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="permissions">Permissions</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="profile" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Profile Details</CardTitle>
              <CardDescription>All fields from the user record</CardDescription>
            </CardHeader>
            <CardContent>
              <ProfileTab user={user} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="permissions" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Roles & Permissions</CardTitle>
              <CardDescription>
                Current role assignment and effective permission set
              </CardDescription>
            </CardHeader>
            <CardContent>
              <PermissionsTab userId={userId} isSelf={isSelf} canEdit={canEdit} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Activity Log</CardTitle>
              <CardDescription>Recent actions performed by this user</CardDescription>
            </CardHeader>
            <CardContent>
              <ActivityTab userId={userId} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {showEdit && <EditUserDialog user={user} onClose={() => setShowEdit(false)} />}
      {showDeactivate && (
        <DeactivateDialog user={user} onClose={() => setShowDeactivate(false)} />
      )}
    </div>
  );
}
