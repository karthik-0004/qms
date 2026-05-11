"use client";

import { useState } from "react";
import Link from "next/link";
import type { Route } from "next";
import {
  Plus,
  Search,
  ChevronLeft,
  ChevronRight,
  Pause,
  Play,
  ExternalLink,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  useTenants,
  useCreateTenant,
  useSuspendTenant,
  useActivateTenant,
} from "@/lib/hooks/queries/platform";
import type { Tenant } from "@/lib/api/services/platform";

const PAGE_SIZE = 10;

const TIER_STYLE: Record<string, string> = {
  starter: "bg-slate-100 text-slate-700",
  professional: "bg-blue-100 text-blue-700",
  enterprise: "bg-purple-100 text-purple-700",
};

const STATUS_STYLE: Record<string, string> = {
  active: "bg-green-100 text-green-700",
  inactive: "bg-slate-100 text-slate-500",
  suspended: "bg-red-100 text-red-600",
  pending: "bg-amber-100 text-amber-700",
  provisioning: "bg-amber-100 text-amber-700",
  provisioning_failed: "bg-red-100 text-red-700",
};

const STATUS_LABEL: Record<string, string> = {
  active: "Active",
  inactive: "Inactive",
  suspended: "Suspended",
  pending: "Pending",
  provisioning: "Provisioning",
  provisioning_failed: "Failed",
};

function CreateTenantDialog({
  open,
  onOpenChange,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const [name, setName] = useState("");
  const [products, setProducts] = useState<string[]>([]);
  const [tier, setTier] = useState("starter");
  const [region, setRegion] = useState("us-east-1");
  const { mutate: createTenant, isPending } = useCreateTenant();

  const toggleProduct = (p: string) =>
    setProducts((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim() || products.length === 0) return;
    createTenant(
      { tenant_name: name.trim(), products, tier, region },
      {
        onSuccess: () => {
          setName("");
          setProducts([]);
          setTier("starter");
          setRegion("us-east-1");
          onOpenChange(false);
        },
      }
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Create New Tenant</DialogTitle>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          <div className="space-y-2">
            <Label htmlFor="tenant-name">Tenant Name</Label>
            <Input
              id="tenant-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Acme Corporation"
              required
            />
          </div>

          <div className="space-y-2">
            <Label>Products</Label>
            <div className="flex gap-4">
              {(["qms", "em", "ccv"] as const).map((p) => (
                <label key={p} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={products.includes(p)}
                    onChange={() => toggleProduct(p)}
                    className="rounded border-input"
                  />
                  <span className="text-sm font-medium uppercase">{p}</span>
                </label>
              ))}
            </div>
            {products.length === 0 && (
              <p className="text-xs text-red-500">Select at least one product</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tier">Tier</Label>
              <select
                id="tier"
                value={tier}
                onChange={(e) => setTier(e.target.value)}
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                <option value="starter">Starter</option>
                <option value="professional">Professional</option>
                <option value="enterprise">Enterprise</option>
              </select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="region">Region</Label>
              <select
                id="region"
                value={region}
                onChange={(e) => setRegion(e.target.value)}
                className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              >
                <option value="us-east-1">US East (N. Virginia)</option>
                <option value="us-west-2">US West (Oregon)</option>
                <option value="eu-west-1">EU West (Ireland)</option>
              </select>
            </div>
          </div>

          <DialogFooter className="pt-2">
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isPending || !name.trim() || products.length === 0}
            >
              {isPending ? "Creating…" : "Create Tenant"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}

export function TenantsTab() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [createOpen, setCreateOpen] = useState(false);

  const { data, isLoading } = useTenants({
    status_filter: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });
  const { mutate: suspend, isPending: suspending } = useSuspendTenant();
  const { mutate: activate, isPending: activating } = useActivateTenant();

  const tenants: Tenant[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  const filtered = search
    ? tenants.filter(
        (t) =>
          t.tenant_name.toLowerCase().includes(search.toLowerCase()) ||
          t.slug.toLowerCase().includes(search.toLowerCase())
      )
    : tenants;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <p className="text-sm text-muted-foreground">
          {isLoading ? "Loading…" : `${totalItems} tenants`}
        </p>
        <Button size="sm" className="gap-1.5" onClick={() => setCreateOpen(true)}>
          <Plus className="h-4 w-4" />
          New Tenant
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or slug…"
            className="pl-8"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm min-h-11 sm:min-h-9"
        >
          <option value="">All Status</option>
          <option value="active">Active</option>
          <option value="suspended">Suspended</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">Tenant</th>
              <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Tier</th>
              <th className="pb-2 pr-4 font-medium hidden md:table-cell">Products</th>
              <th className="pb-2 pr-4 font-medium">Status</th>
              <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Region</th>
              <th className="pb-2 pr-4 font-medium hidden xl:table-cell">Created</th>
              <th className="pb-2 font-medium">Actions</th>
            </tr>
          </thead>
          <tbody>
            {isLoading
              ? Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i} className="border-b">
                    {Array.from({ length: 7 }).map((_, j) => (
                      <td key={j} className="py-3 pr-4">
                        <Skeleton className="h-4 w-20" />
                      </td>
                    ))}
                  </tr>
                ))
              : filtered.map((t) => (
                  <tr
                    key={t.id}
                    className="border-b last:border-0 hover:bg-muted/30 transition-colors"
                  >
                    <td className="py-3 pr-4">
                      <Link
                        href={`/admin/tenants/${t.slug}` as Route}
                        className="group block rounded-md -m-1 p-1 hover:bg-muted/50"
                      >
                        <p className="font-medium text-foreground group-hover:underline">
                          {t.tenant_name}
                        </p>
                        <p className="text-xs text-muted-foreground font-mono">{t.slug}</p>
                      </Link>
                    </td>
                    <td className="py-3 pr-4 hidden sm:table-cell">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${TIER_STYLE[t.tier] ?? "bg-slate-100 text-slate-700"}`}
                      >
                        {t.tier.charAt(0).toUpperCase() + t.tier.slice(1)}
                      </span>
                    </td>
                    <td className="py-3 pr-4 hidden md:table-cell">
                      <div className="flex gap-1 flex-wrap">
                        {t.products.map((p) => (
                          <span
                            key={p}
                            className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium bg-blue-50 text-blue-700"
                          >
                            {p.toUpperCase()}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="py-3 pr-4">
                      <span
                        className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLE[t.status] ?? ""}`}
                      >
                        {STATUS_LABEL[t.status] ?? t.status}
                      </span>
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground hidden lg:table-cell">
                      {t.region}
                    </td>
                    <td className="py-3 pr-4 text-xs text-muted-foreground hidden xl:table-cell">
                      {new Date(t.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3">
                      <div className="flex flex-wrap items-center gap-1">
                        <Button variant="ghost" size="sm" className="h-8 px-2 text-xs" asChild>
                          <Link href={`/admin/tenants/${t.slug}` as Route}>
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Open
                          </Link>
                        </Button>
                        {t.status === "active" ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs h-8 px-2"
                            onClick={() => suspend(t.id)}
                            disabled={suspending}
                          >
                            <Pause className="h-3 w-3 mr-1" />
                            Suspend
                          </Button>
                        ) : t.status === "suspended" ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-green-600 hover:text-green-700 hover:bg-green-50 text-xs h-8 px-2"
                            onClick={() => activate(t.id)}
                            disabled={activating}
                          >
                            <Play className="h-3 w-3 mr-1" />
                            Activate
                          </Button>
                        ) : (
                          <span className="text-xs text-muted-foreground">—</span>
                        )}
                      </div>
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

      <CreateTenantDialog open={createOpen} onOpenChange={setCreateOpen} />
    </div>
  );
}
