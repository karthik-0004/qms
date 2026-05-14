"use client";

import { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { signOut } from "next-auth/react";
import {
  User,
  Save,
  Shield,
  Loader2,
  QrCode,
  LogOut,
  KeyRound,
  CheckCircle2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
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
  useSetupMFA,
  useVerifyMFA,
  useDisableMFA,
  useLogoutAll,
} from "@/lib/hooks/queries/platform";
import { toast } from "sonner";

// ─── Personal Info Tab ────────────────────────────────────────────────────────

function PersonalInfoTab({ userId }: { userId: string }) {
  const { data: user, isLoading } = useUser(userId);
  const { mutate: updateUser, isPending: saving } = useUpdateUser();

  const [form, setForm] = useState({
    first_name: "",
    last_name: "",
    display_name: "",
    phone: "",
    department: "",
    job_title: "",
  });
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        first_name: user.first_name,
        last_name: user.last_name,
        display_name: user.display_name ?? "",
        phone: user.phone ?? "",
        department: user.department ?? "",
        job_title: user.job_title ?? "",
      });
      setIsDirty(false);
    }
  }, [user]);

  function set(key: keyof typeof form) {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      setForm((prev) => ({ ...prev, [key]: e.target.value }));
      setIsDirty(true);
    };
  }

  function handleSave(e: React.FormEvent) {
    e.preventDefault();
    if (!isDirty) return;
    updateUser(
      {
        id: userId,
        data: {
          first_name: form.first_name || undefined,
          last_name: form.last_name || undefined,
          display_name: form.display_name || undefined,
          phone: form.phone || undefined,
          department: form.department || undefined,
          job_title: form.job_title || undefined,
        },
      },
      { onSuccess: () => setIsDirty(false) },
    );
  }

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-9 w-full" />)}
      </div>
    );
  }

  return (
    <form onSubmit={handleSave} className="space-y-4">
      {/* Email — always read-only, not in UpdateUserRequest */}
      <div className="space-y-1.5">
        <Label htmlFor="p-email">Email</Label>
        <Input
          id="p-email"
          type="email"
          value={(user as { email?: string } | undefined)?.email ?? ""}
          disabled
          className="bg-muted"
        />
        <p className="text-xs text-muted-foreground">Email cannot be changed here.</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label htmlFor="p-fn">First name *</Label>
          <Input id="p-fn" required value={form.first_name} onChange={set("first_name")} />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="p-ln">Last name *</Label>
          <Input id="p-ln" required value={form.last_name} onChange={set("last_name")} />
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="p-dn">Display name</Label>
        <Input id="p-dn" value={form.display_name} onChange={set("display_name")} placeholder="How your name appears to others" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-1.5">
          <Label htmlFor="p-phone">Phone</Label>
          <Input id="p-phone" value={form.phone} onChange={set("phone")} placeholder="+1-555-0123" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="p-dept">Department</Label>
          <Input id="p-dept" value={form.department} onChange={set("department")} placeholder="Engineering" />
        </div>
      </div>

      <div className="space-y-1.5">
        <Label htmlFor="p-title">Job title</Label>
        <Input id="p-title" value={form.job_title} onChange={set("job_title")} placeholder="Software Engineer" />
      </div>

      <div className="flex justify-end pt-2">
        <Button type="submit" disabled={!isDirty || saving} className="gap-1.5">
          {saving ? (
            <><Loader2 className="h-4 w-4 animate-spin" />Saving…</>
          ) : (
            <><Save className="h-4 w-4" />Save Changes</>
          )}
        </Button>
      </div>
    </form>
  );
}

// ─── MFA Setup Flow ───────────────────────────────────────────────────────────

function MFASetupFlow({ onDone }: { onDone: () => void }) {
  const { mutate: setupMFA, isPending: setting, data: setupData } = useSetupMFA();
  const { mutate: verifyMFA, isPending: verifying } = useVerifyMFA();
  const [code, setCode] = useState("");
  const [started, setStarted] = useState(false);

  function handleStart() {
    setStarted(true);
    setupMFA(undefined, {
      onError: () => setStarted(false),
    });
  }

  function handleVerify(e: React.FormEvent) {
    e.preventDefault();
    verifyMFA(code, {
      onSuccess: () => {
        setCode("");
        onDone();
      },
    });
  }

  if (!started) {
    return (
      <Button size="sm" onClick={handleStart} disabled={setting} className="gap-1.5">
        {setting ? <Loader2 className="h-4 w-4 animate-spin" /> : <QrCode className="h-4 w-4" />}
        Enable MFA
      </Button>
    );
  }

  if (setting || !setupData) {
    return <Skeleton className="h-48 w-full" />;
  }

  return (
    <div className="space-y-4 rounded-md border p-4">
      <p className="text-sm font-medium">Scan this QR code with your authenticator app</p>
      {/* Display QR code image from qr_code_url field (spec: MFASetupResponse.qr_code_url) */}
      <img
        src={setupData.qr_code_url}
        alt="MFA QR Code"
        className="h-40 w-40 border rounded"
      />
      <p className="text-xs text-muted-foreground">
        Or enter this secret manually:{" "}
        <code className="bg-muted px-1 py-0.5 rounded text-xs font-mono">{setupData.secret}</code>
      </p>
      <form onSubmit={handleVerify} className="flex gap-2">
        <Input
          placeholder="6-digit code"
          value={code}
          onChange={(e) => setCode(e.target.value)}
          maxLength={6}
          className="w-36"
        />
        <Button type="submit" size="sm" disabled={code.length !== 6 || verifying}>
          {verifying ? <Loader2 className="h-4 w-4 animate-spin" /> : "Verify"}
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={() => { setStarted(false); setCode(""); }}>
          Cancel
        </Button>
      </form>
    </div>
  );
}

// ─── Disable MFA Flow ─────────────────────────────────────────────────────────

function DisableMFAFlow({ onDone }: { onDone: () => void }) {
  const [open, setOpen] = useState(false);
  const [password, setPassword] = useState("");
  const { mutate: disableMFA, isPending } = useDisableMFA();

  function handleConfirm() {
    // MFADisableRequest requires `password` field (confirmed from spec)
    disableMFA(password, {
      onSuccess: () => {
        setOpen(false);
        setPassword("");
        onDone();
      },
    });
  }

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        className="gap-1.5 text-destructive border-destructive/30 hover:bg-destructive/10"
        onClick={() => setOpen(true)}
      >
        <KeyRound className="h-4 w-4" />
        Disable MFA
      </Button>

      <AlertDialog open={open} onOpenChange={setOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Disable MFA?</AlertDialogTitle>
            <AlertDialogDescription>
              Enter your password to confirm. This will remove MFA protection from your account.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="py-2">
            <Label htmlFor="mfa-pw">Password</Label>
            <Input
              id="mfa-pw"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1.5"
              placeholder="Your current password"
            />
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setPassword("")}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleConfirm}
              disabled={!password || isPending}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              {isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              Disable MFA
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}

// ─── Security Tab ─────────────────────────────────────────────────────────────

function SecurityTab({ userId }: { userId: string }) {
  const { data: user } = useUser(userId);
  const { mutate: logoutAll, isPending: loggingOut } = useLogoutAll();
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);
  const [mfaEnabled, setMfaEnabled] = useState<boolean | null>(null);

  // mfa_enabled is not in UserResponse spec — we track it locally after setup/disable
  // The user object from user-service doesn't include mfa_enabled
  // TODO: Surface mfa_enabled in UserResponse when auth-service exposes it

  function handleLogoutAll() {
    logoutAll(undefined, {
      onSuccess: () => {
        setShowLogoutConfirm(false);
        signOut({ callbackUrl: "/signin" });
      },
    });
  }

  return (
    <div className="space-y-6">
      {/* MFA Section — POST /auth/mfa/setup and /auth/mfa/verify are confirmed implemented */}
      <div>
        <h3 className="text-sm font-semibold mb-1">Multi-Factor Authentication</h3>
        <p className="text-xs text-muted-foreground mb-3">
          Add an extra layer of security to your account using a TOTP authenticator app.
        </p>
        {mfaEnabled === true ? (
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1.5 text-sm text-green-700">
              <CheckCircle2 className="h-4 w-4" />
              MFA is enabled
            </div>
            <DisableMFAFlow onDone={() => setMfaEnabled(false)} />
          </div>
        ) : (
          <MFASetupFlow onDone={() => setMfaEnabled(true)} />
        )}
      </div>

      <Separator />

      {/* Sign out all devices — POST /auth/logout-all confirmed implemented */}
      <div>
        <h3 className="text-sm font-semibold mb-1">Active Sessions</h3>
        <p className="text-xs text-muted-foreground mb-3">
          Sign out from all devices where you are currently logged in.
        </p>
        <Button
          variant="outline"
          size="sm"
          className="gap-1.5"
          onClick={() => setShowLogoutConfirm(true)}
        >
          <LogOut className="h-4 w-4" />
          Sign out all devices
        </Button>
      </div>

      <AlertDialog open={showLogoutConfirm} onOpenChange={setShowLogoutConfirm}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Sign out all devices?</AlertDialogTitle>
            <AlertDialogDescription>
              This will revoke all active sessions. You will be redirected to sign in again.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction onClick={handleLogoutAll} disabled={loggingOut}>
              {loggingOut ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
              Sign out all
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

export default function ProfilePage() {
  const { data: session, status } = useSession();
  const userId = (session?.user as { id?: string } | undefined)?.id ?? "";

  if (status === "loading" || !userId) {
    return (
      <div className="space-y-6 max-w-2xl mx-auto">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-2xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <User className="h-6 w-6" />
          My Profile
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Manage your personal information and security settings
        </p>
      </div>

      <Tabs defaultValue="personal">
        <TabsList>
          <TabsTrigger value="personal">Personal Info</TabsTrigger>
          <TabsTrigger value="security">
            <Shield className="h-4 w-4 mr-1.5" />
            Security
          </TabsTrigger>
        </TabsList>

        <TabsContent value="personal" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Personal Information</CardTitle>
              <CardDescription>Update your name, contact details, and job info</CardDescription>
            </CardHeader>
            <CardContent>
              <PersonalInfoTab userId={userId} />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="mt-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Security</CardTitle>
              <CardDescription>MFA and session management</CardDescription>
            </CardHeader>
            <CardContent>
              <SecurityTab userId={userId} />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
