"use client";

import { useState } from "react";
import Link from "next/link";
import type { Route } from "next";
import {
  Crown,
  Building2,
  Users,
  Server,
  Activity,
  LayoutDashboard,
  Search,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useTenants, useUsers, useAuditLog } from "@/lib/hooks/queries/platform";
import type { User, AuditEntry } from "@/lib/api/services/platform";
import { cn } from "@/lib/utils";

// ─── Constants ────────────────────────────────────────────────────────────────

const PAGE_SIZE = 10;

type Tab = "overview" | "users" | "services" | "audit";

const PLATFORM_SERVICES: { name: string; port: number; category: "Platform" | "QMS" | "EM" | "CCV" }[] = [
  { name: "Gateway", port: 8000, category: "Platform" },
  { name: "Auth", port: 8001, category: "Platform" },
  { name: "Tenant", port: 8002, category: "Platform" },
  { name: "User", port: 8003, category: "Platform" },
  { name: "Audit", port: 8004, category: "Platform" },
  { name: "Notification", port: 8005, category: "Platform" },
  { name: "Config", port: 8006, category: "Platform" },
  { name: "Workflow Engine", port: 8007, category: "Platform" },
  { name: "Schedule", port: 8008, category: "Platform" },
  { name: "File", port: 8009, category: "Platform" },
  { name: "Reporting", port: 8010, category: "Platform" },
  { name: "Analytics", port: 8011, category: "Platform" },
  { name: "Document", port: 8020, category: "QMS" },
  { name: "Quality Event", port: 8021, category: "QMS" },
  { name: "CAPA", port: 8022, category: "QMS" },
  { name: "Training", port: 8023, category: "QMS" },
  { name: "Equipment", port: 8024, category: "QMS" },
  { name: "Plate", port: 8030, category: "EM" },
  { name: "Image", port: 8031, category: "EM" },
  { name: "AI", port: 8032, category: "EM" },
  { name: "Job", port: 8033, category: "EM" },
  { name: "QA Review", port: 8034, category: "EM" },
  { name: "CRM", port: 8040, category: "CCV" },
  { name: "Contract", port: 8041, category: "CCV" },
  { name: "Work Order", port: 8042, category: "CCV" },
  { name: "Technician", port: 8043, category: "CCV" },
  { name: "Billing", port: 8044, category: "CCV" },
];

const STATUS_STYLE: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  inactive: "bg-slate-100 text-slate-500",
  suspended: "bg-red-100 text-red-600",
  pending: "bg-amber-100 text-amber-700",
};

const STATUS_LABEL: Record<string, string> = {
  active: "Active",
  inactive: "Inactive",
  suspended: "Suspended",
  pending: "Pending",
};

const ROLE_STYLE: Record<string, string> = {
  super_admin: "bg-red-100 text-red-700",
  tenant_admin: "bg-purple-100 text-purple-700",
  tenant_user: "bg-blue-100 text-blue-700",
};

const ROLE_LABEL: Record<string, string> = {
  super_admin: "Super Admin",
  tenant_admin: "Tenant Admin",
  tenant_user: "User",
};

const CATEGORY_STYLE: Record<string, string> = {
  Platform: "bg-slate-100 text-slate-700",
  QMS: "bg-green-50 text-green-700",
  EM: "bg-blue-50 text-blue-700",
  CCV: "bg-purple-50 text-purple-700",
};

// ─── Overview Tab ─────────────────────────────────────────────────────────────

function OverviewTab({
  tenantTotal,
  userTotal,
}: {
  tenantTotal: number;
  userTotal: number;
}) {
  const stats = [
    {
      label: "Total Tenants",
      value: tenantTotal,
      color: "text-blue-600",
      bg: "bg-blue-50",
      icon: Building2,
    },
    {
      label: "Total Users",
      value: userTotal,
      color: "text-purple-600",
      bg: "bg-purple-50",
      icon: Users,
    },
    {
      label: "Microservices",
      value: PLATFORM_SERVICES.length,
      color: "text-green-600",
      bg: "bg-green-50",
      icon: Server,
    },
    {
      label: "Products",
      value: 3,
      color: "text-amber-600",
      bg: "bg-amber-50",
      icon: LayoutDashboard,
    },
  ];

  const products = [
    {
      id: "QMS",
      name: "Quality Management System",
      color: "border-green-200 bg-green-50",
      badge: "bg-green-100 text-green-700",
      modules: ["Documents", "Quality Events", "CAPA", "Training", "Equipment"],
      services: 5,
    },
    {
      id: "EM",
      name: "EndGame Biotech (EM)",
      color: "border-blue-200 bg-blue-50",
      badge: "bg-blue-100 text-blue-700",
      modules: ["Plates", "Images", "AI Analysis", "Jobs", "QA Review"],
      services: 5,
    },
    {
      id: "CCV",
      name: "Certification, Calibration & Validation",
      color: "border-purple-200 bg-purple-50",
      badge: "bg-purple-100 text-purple-700",
      modules: ["CRM", "Contracts", "Work Orders", "Technicians", "Billing", "Certificates"],
      services: 5,
    },
  ];

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-center gap-3">
        <Link
          href={"/super-admin/tenants" as Route}
          className="inline-flex items-center rounded-lg border bg-card px-4 py-2 text-sm font-medium text-primary hover:bg-muted/60 transition-colors min-h-11"
        >
          Tenant directory — create and open tenants by slug
        </Link>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {stats.map(({ label, value, color, bg, icon: Icon }) => (
          <div key={label} className={`rounded-xl border p-4 ${bg}`}>
            <div className="flex items-center gap-3">
              <Icon className={`h-5 w-5 ${color}`} />
              <p className="text-sm font-medium text-muted-foreground">{label}</p>
            </div>
            <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-4">
          Platform Products
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {products.map((p) => (
            <div key={p.id} className={`rounded-xl border-2 p-4 ${p.color}`}>
              <div className="flex items-center justify-between mb-3">
                <span
                  className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-bold ${p.badge}`}
                >
                  {p.id}
                </span>
                <span className="text-xs text-muted-foreground">
                  {p.services} services
                </span>
              </div>
              <p className="text-sm font-semibold mb-2">{p.name}</p>
              <ul className="space-y-1">
                {p.modules.map((m) => (
                  <li key={m} className="text-xs text-muted-foreground flex items-center gap-1.5">
                    <span className="w-1 h-1 rounded-full bg-current inline-block" />
                    {m}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground mb-3">
          Platform Services (12 Core)
        </h3>
        <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
          {PLATFORM_SERVICES.filter((s) => s.category === "Platform").map((s) => (
            <div
              key={s.name}
              className="border rounded-lg p-2.5 text-center space-y-1.5"
            >
              <div className="w-2 h-2 rounded-full bg-green-400 mx-auto" />
              <p className="text-xs font-medium">{s.name}</p>
              <span className="text-xs text-muted-foreground">:{s.port}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Users Tab ────────────────────────────────────────────────────────────────

function UsersTab() {
  const [search, setSearch] = useState("");
  const [roleFilter, setRoleFilter] = useState("");
  const [page, setPage] = useState(1);

  const { data, isLoading } = useUsers({
    search: search || undefined,
    role: roleFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const users: User[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or email…"
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
          <option value="super_admin">Super Admin</option>
          <option value="tenant_admin">Tenant Admin</option>
          <option value="tenant_user">User</option>
        </select>
      </div>

      <p className="text-sm text-muted-foreground">
        {isLoading ? "Loading…" : `${totalItems} users`}
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">User</th>
              <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Role</th>
              <th className="pb-2 pr-4 font-medium">Status</th>
              <th className="pb-2 pr-4 font-medium hidden md:table-cell">Tenant ID</th>
              <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Last Login</th>
              <th className="pb-2 pr-4 font-medium hidden xl:table-cell">Joined</th>
            </tr>
          </thead>
          <tbody>
            {isLoading
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
                  const life = u.is_active ? "active" : "inactive";
                  return (
                  <tr
                    key={u.id}
                    className="border-b last:border-0 hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-3 pr-4">
                      <p className="font-medium">
                        {u.first_name} {u.last_name}
                      </p>
                      <p className="text-xs text-muted-foreground">{u.email}</p>
                    </td>
                    <td className="py-3 pr-4 hidden sm:table-cell">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${ROLE_STYLE[u.role] ?? "bg-slate-100 text-slate-600"}`}
                      >
                        {ROLE_LABEL[u.role] ?? u.role}
                      </span>
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLE[life] ?? ""}`}
                      >
                        {STATUS_LABEL[life] ?? life}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground font-mono hidden md:table-cell">
                      {u.tenant_id ? u.tenant_id.slice(0, 12) + "…" : "—"}
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground hidden lg:table-cell">
                      {u.last_login
                        ? new Date(u.last_login).toLocaleString()
                        : "Never"}
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground hidden xl:table-cell">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                );
              })}
          </tbody>
        </table>
      </div>

      {!isLoading && totalItems > PAGE_SIZE && (
        <div className="flex items-center justify-between pt-4 border-t">
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
    </div>
  );
}

// ─── Services Tab ─────────────────────────────────────────────────────────────

function ServicesTab() {
  const categories = ["Platform", "QMS", "EM", "CCV"] as const;

  return (
    <div className="space-y-8">
      <p className="text-sm text-muted-foreground">
        {PLATFORM_SERVICES.length} microservices across 4 domains
      </p>
      {categories.map((cat) => {
        const services = PLATFORM_SERVICES.filter((s) => s.category === cat);
        return (
          <div key={cat}>
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
              <span
                className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${CATEGORY_STYLE[cat]}`}
              >
                {cat}
              </span>
              <span>{services.length} services</span>
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {services.map((s) => (
                <div
                  key={s.name}
                  className="border rounded-lg p-3 flex flex-col items-center text-center gap-1.5 hover:bg-muted/30 transition-colors"
                >
                  <div className="w-2 h-2 rounded-full bg-green-400" title="Running" />
                  <p className="text-xs font-medium">{s.name}</p>
                  <span className="text-xs text-muted-foreground font-mono">
                    :{s.port}
                  </span>
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );
}

// ─── Audit Tab ────────────────────────────────────────────────────────────────

function AuditTab() {
  const [page, setPage] = useState(1);
  const { data, isLoading } = useAuditLog({ page, page_size: PAGE_SIZE });

  const entries: AuditEntry[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        {isLoading ? "Loading…" : `${totalItems} audit entries`}
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Action</th>
              <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Entity Type</th>
              <th className="pb-2 pr-4 font-medium hidden md:table-cell">Entity ID</th>
              <th className="pb-2 pr-4 font-medium hidden lg:table-cell">User</th>
              <th className="pb-2 pr-4 font-medium hidden xl:table-cell">Tenant</th>
              <th className="pb-2 pr-4 font-medium">Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">
                    {Array.from({ length: 6 }).map((_, j) => (
                      <td key={j} className="py-3 pr-4">
                        <Skeleton className="h-4 w-24" />
                      </td>
                    ))}
                  </tr>
                ))
              : entries.map((e) => (
                  <tr
                    key={e.id}
                    className="border-b last:border-0 hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-3 pr-4">
                      <span className="font-mono text-xs font-medium bg-slate-100 text-slate-700 rounded px-1.5 py-0.5">
                        {e.action}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground hidden sm:table-cell">
                      {e.entity_type}
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground font-mono hidden md:table-cell">
                      {e.entity_id.slice(0, 8)}…
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground font-mono hidden lg:table-cell">
                      {e.user_id.slice(0, 8)}…
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground font-mono hidden xl:table-cell">
                      {e.tenant_id.slice(0, 8)}…
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground">
                      {new Date(e.created_at).toLocaleString()}
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {!isLoading && totalItems > PAGE_SIZE && (
        <div className="flex items-center justify-between pt-4 border-t">
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
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────

const TABS: { id: Tab; label: string; icon: React.ElementType }[] = [
  { id: "overview", label: "Overview", icon: LayoutDashboard },
  { id: "users", label: "Users", icon: Users },
  { id: "services", label: "Services", icon: Server },
  { id: "audit", label: "Audit Log", icon: Activity },
];

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const { data: tenantsData } = useTenants({ page: 1, page_size: 1 });
  const { data: usersData } = useUsers({ page: 1, page_size: 1 });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-red-600 flex items-center justify-center shrink-0">
          <Crown className="h-5 w-5 text-white" />
        </div>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Super Admin Panel</h1>
          <p className="text-muted-foreground text-sm">
            Platform-wide management — Rainer SaaS
          </p>
        </div>
        <span className="ml-auto inline-flex items-center rounded-full px-3 py-1 text-xs font-medium bg-red-100 text-red-700 shrink-0">
          Super Admin
        </span>
      </div>

      {/* Tabs */}
      <div className="border-b">
        <nav className="-mb-px flex gap-0 overflow-x-auto">
          {TABS.map(({ id, label, icon: Icon }) => (
            <button
              key={id}
              onClick={() => setActiveTab(id)}
              className={cn(
                "flex items-center gap-2 px-4 py-2.5 text-sm font-medium border-b-2 whitespace-nowrap transition-colors",
                activeTab === id
                  ? "border-red-600 text-red-600"
                  : "border-transparent text-muted-foreground hover:text-foreground hover:border-muted-foreground/30"
              )}
            >
              <Icon className="h-4 w-4" />
              {label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <Card>
        <CardContent className="pt-6">
          {activeTab === "overview" && (
            <OverviewTab
              tenantTotal={tenantsData?.total ?? 0}
              userTotal={usersData?.total ?? 0}
            />
          )}
          {activeTab === "users" && <UsersTab />}
          {activeTab === "services" && <ServicesTab />}
          {activeTab === "audit" && <AuditTab />}
        </CardContent>
      </Card>
    </div>
  );
}
