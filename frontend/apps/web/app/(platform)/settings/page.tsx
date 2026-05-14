"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "next-auth/react";
import {
  Settings,
  Save,
  Bell,
  Shield,
  Globe,
  Palette,
  ArrowLeft,
  Home,
  RefreshCw,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { useUIStore } from "@/lib/stores/ui.store";
import { useTenantSettings, useUpdateTenantSettings } from "@/lib/hooks/queries/platform";
import { usePermission } from "@/lib/hooks/usePermission";

// ─── Form state shape (mirrors UpdateTenantSettingsRequest from spec) ─────────
interface SettingsForm {
  timezone: string;
  locale: string;
  features: Record<string, unknown>;
  branding: Record<string, unknown>;
  webhook_urls: string[];
  max_users: number;
  max_storage_gb: number;
}

function SettingsSkeleton() {
  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <Skeleton className="h-8 w-48" />
      {[1, 2, 3].map((i) => (
        <Card key={i}>
          <CardHeader>
            <Skeleton className="h-5 w-32" />
          </CardHeader>
          <CardContent className="space-y-4">
            <Skeleton className="h-9 w-full" />
            <Skeleton className="h-9 w-full" />
          </CardContent>
        </Card>
      ))}
    </div>
  );
}

export default function SettingsPage() {
  const router = useRouter();
  const { data: session } = useSession();
  const { theme, setTheme } = useUIStore();
  const { isTenantAdmin, isSuperAdmin } = usePermission();
  const canEdit = isTenantAdmin || isSuperAdmin;

  // Get tenantId from session
  const tenantId = (session?.user as { tenant_id?: string } | undefined)?.tenant_id ?? "";

  const {
    data: settings,
    isLoading,
    isError,
    refetch,
  } = useTenantSettings(tenantId || undefined);

  const { mutate: saveSettings, isPending: isSaving } = useUpdateTenantSettings();

  // Local form state — populated from API on load
  const [form, setForm] = useState<SettingsForm>({
    timezone: "UTC",
    locale: "en",
    features: {},
    branding: {},
    webhook_urls: [],
    max_users: 50,
    max_storage_gb: 10,
  });

  // Track whether user has made changes
  const [isDirty, setIsDirty] = useState(false);

  // Populate form when API data arrives
  useEffect(() => {
    if (settings) {
      setForm({
        timezone: settings.timezone,
        locale: settings.locale,
        features: settings.features,
        branding: settings.branding,
        webhook_urls: settings.webhook_urls,
        max_users: settings.max_users,
        max_storage_gb: settings.max_storage_gb,
      });
      setIsDirty(false);
    }
  }, [settings]);

  function updateField<K extends keyof SettingsForm>(key: K, value: SettingsForm[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
    setIsDirty(true);
  }

  // MFA enforce is stored inside features object
  const mfaEnforced = Boolean(form.features?.enforce_mfa);
  function setMfaEnforced(val: boolean) {
    updateField("features", { ...form.features, enforce_mfa: val });
  }

  // Email notifications stored inside features object
  const emailNotifications = form.features?.email_notifications !== false;
  function setEmailNotifications(val: boolean) {
    updateField("features", { ...form.features, email_notifications: val });
  }

  function handleSave() {
    if (!tenantId || !isDirty) return;
    saveSettings(
      {
        tenantId,
        data: {
          timezone: form.timezone,
          locale: form.locale,
          features: form.features,
          branding: form.branding,
          webhook_urls: form.webhook_urls,
          max_users: form.max_users,
          max_storage_gb: form.max_storage_gb,
        },
      },
      {
        onSuccess: () => setIsDirty(false),
      },
    );
  }

  if (isLoading) return <SettingsSkeleton />;

  if (isError) {
    return (
      <div className="space-y-6 max-w-4xl mx-auto">
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 flex items-center justify-between">
          <p className="text-sm text-destructive">Failed to load settings. Please try again.</p>
          <Button variant="outline" size="sm" onClick={() => refetch()} className="gap-1.5">
            <RefreshCw className="h-4 w-4" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <Home className="h-4 w-4 mr-1" />
          Home
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">Platform Settings</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Settings className="h-6 w-6" />
          Platform Settings
        </h1>
        <p className="text-muted-foreground text-sm mt-1">Manage organization-wide configuration</p>
      </div>

      {/* General */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Globe className="h-4 w-4" />
            General
          </CardTitle>
          <CardDescription>Organization and locale settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="timezone">Timezone</Label>
              <select
                id="timezone"
                value={form.timezone}
                onChange={(e) => updateField("timezone", e.target.value)}
                disabled={!canEdit}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="America/New_York">Eastern (ET)</option>
                <option value="America/Chicago">Central (CT)</option>
                <option value="America/Denver">Mountain (MT)</option>
                <option value="America/Los_Angeles">Pacific (PT)</option>
                <option value="Europe/London">London (GMT/BST)</option>
                <option value="Europe/Berlin">Berlin (CET/CEST)</option>
                <option value="Asia/Tokyo">Tokyo (JST)</option>
                <option value="UTC">UTC</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="locale">Locale</Label>
              <select
                id="locale"
                value={form.locale}
                onChange={(e) => updateField("locale", e.target.value)}
                disabled={!canEdit}
                className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <option value="en">English</option>
                <option value="en-GB">English (UK)</option>
                <option value="de">German</option>
                <option value="fr">French</option>
                <option value="ja">Japanese</option>
              </select>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="max-users">Max Users</Label>
              <Input
                id="max-users"
                type="number"
                min={1}
                max={10000}
                value={form.max_users}
                onChange={(e) => updateField("max_users", Number(e.target.value))}
                disabled={!canEdit}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="max-storage">Max Storage (GB)</Label>
              <Input
                id="max-storage"
                type="number"
                min={1}
                max={10000}
                value={form.max_storage_gb}
                onChange={(e) => updateField("max_storage_gb", Number(e.target.value))}
                disabled={!canEdit}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Bell className="h-4 w-4" />
            Notifications
          </CardTitle>
          <CardDescription>Email and alert preferences</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Email Notifications</p>
              <p className="text-xs text-muted-foreground">Receive email alerts for critical events</p>
            </div>
            <Switch
              checked={emailNotifications}
              onCheckedChange={setEmailNotifications}
              disabled={!canEdit}
            />
          </div>
        </CardContent>
      </Card>

      {/* Security */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Shield className="h-4 w-4" />
            Security
          </CardTitle>
          <CardDescription>Authentication and compliance settings</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Enforce MFA</p>
              <p className="text-xs text-muted-foreground">
                Require multi-factor authentication for all users
              </p>
            </div>
            <Switch
              checked={mfaEnforced}
              onCheckedChange={setMfaEnforced}
              disabled={!canEdit}
            />
          </div>
          <Separator />
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Audit Logging</p>
              <p className="text-xs text-muted-foreground">Log all user actions for compliance</p>
            </div>
            {/* Audit logging is always on — read-only display */}
            <Switch checked={true} disabled />
          </div>
        </CardContent>
      </Card>

      {/* Appearance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <Palette className="h-4 w-4" />
            Appearance
          </CardTitle>
          <CardDescription>Theme and display preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium">Dark Mode</p>
              <p className="text-xs text-muted-foreground">Use dark color scheme</p>
            </div>
            <Switch
              checked={theme === "dark"}
              onCheckedChange={(checked) => setTheme(checked ? "dark" : "light")}
            />
          </div>
        </CardContent>
      </Card>

      {/* Save */}
      {canEdit && (
        <div className="flex justify-end">
          <Button
            className="gap-1.5"
            onClick={handleSave}
            disabled={!isDirty || isSaving}
          >
            {isSaving ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Saving…
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                Save Settings
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );
}
