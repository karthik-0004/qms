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
import { Skeleton } from "@/components/ui/skeleton";
import { TENANT_ADMIN_LABELS } from "@/constants/tenant-admin";
import {
  useTenants,
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
  active: TENANT_ADMIN_LABELS.tenant_status_active,
  inactive: TENANT_ADMIN_LABELS.tenant_status_inactive,
  suspended: TENANT_ADMIN_LABELS.tenant_status_suspended,
  pending: TENANT_ADMIN_LABELS.tenant_status_pending,
  provisioning: TENANT_ADMIN_LABELS.tenant_status_provisioning,
  provisioning_failed: TENANT_ADMIN_LABELS.tenant_status_provisioning_failed,
};

const TIER_LABEL: Record<string, string> = {
  starter: TENANT_ADMIN_LABELS.tier_starter,
  professional: TENANT_ADMIN_LABELS.tier_professional,
  enterprise: TENANT_ADMIN_LABELS.tier_enterprise,
};

export function TenantsTab() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);

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
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <p className="text-sm text-muted-foreground">
          {isLoading
            ? TENANT_ADMIN_LABELS.list_loading_count
            : `${totalItems} ${TENANT_ADMIN_LABELS.listTitle.toLowerCase()}`}
        </p>
        <Button size="sm" className="gap-1.5 min-h-11 sm:min-h-9" asChild>
          <Link href={"/admin/tenants/new" as Route}>
            <Plus className="h-4 w-4" />
            {TENANT_ADMIN_LABELS.newTenantCta}
          </Link>
        </Button>
      </div>

      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            placeholder={TENANT_ADMIN_LABELS.list_search_placeholder}
            className="pl-8 min-h-11"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label={TENANT_ADMIN_LABELS.list_search_placeholder}
          />
        </div>
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setPage(1);
          }}
          className="h-9 rounded-md border border-input bg-background px-3 text-sm min-h-11 sm:min-h-9"
          aria-label={TENANT_ADMIN_LABELS.list_filter_all_status}
        >
          <option value="">{TENANT_ADMIN_LABELS.list_filter_all_status}</option>
          <option value="active">{TENANT_ADMIN_LABELS.list_filter_active}</option>
          <option value="suspended">{TENANT_ADMIN_LABELS.list_filter_suspended}</option>
          <option value="inactive">{TENANT_ADMIN_LABELS.list_filter_inactive}</option>
        </select>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="pb-2 pr-4 font-medium">{TENANT_ADMIN_LABELS.list_col_tenant}</th>
              <th className="pb-2 pr-4 font-medium hidden sm:table-cell">
                {TENANT_ADMIN_LABELS.list_col_tier}
              </th>
              <th className="pb-2 pr-4 font-medium hidden md:table-cell">
                {TENANT_ADMIN_LABELS.list_col_products}
              </th>
              <th className="pb-2 pr-4 font-medium">{TENANT_ADMIN_LABELS.list_col_status}</th>
              <th className="pb-2 pr-4 font-medium hidden lg:table-cell">
                {TENANT_ADMIN_LABELS.list_col_region}
              </th>
              <th className="pb-2 pr-4 font-medium hidden xl:table-cell">
                {TENANT_ADMIN_LABELS.list_col_created}
              </th>
              <th className="pb-2 font-medium">{TENANT_ADMIN_LABELS.list_col_actions}</th>
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
                        className="group block rounded-md -m-1 p-1 hover:bg-muted/50 min-h-[44px]"
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
                        {TIER_LABEL[t.tier] ??
                          `${t.tier.charAt(0).toUpperCase()}${t.tier.slice(1)}`}
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
                        <Button variant="ghost" size="sm" className="h-11 sm:h-8 px-2 text-xs min-w-[44px] sm:min-w-0" asChild>
                          <Link href={`/admin/tenants/${t.slug}` as Route}>
                            <ExternalLink className="h-3 w-3 mr-1" aria-hidden />
                            {TENANT_ADMIN_LABELS.list_open}
                          </Link>
                        </Button>
                        {t.status === "active" ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600 hover:text-red-700 hover:bg-red-50 text-xs h-11 sm:h-8 px-2 min-w-[44px] sm:min-w-0"
                            onClick={() => suspend(t.id)}
                            disabled={suspending}
                          >
                            <Pause className="h-3 w-3 mr-1 shrink-0" aria-hidden />
                            {TENANT_ADMIN_LABELS.list_suspend}
                          </Button>
                        ) : t.status === "suspended" ? (
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-green-600 hover:text-green-700 hover:bg-green-50 text-xs h-11 sm:h-8 px-2 min-w-[44px] sm:min-w-0"
                            onClick={() => activate(t.id)}
                            disabled={activating}
                          >
                            <Play className="h-3 w-3 mr-1 shrink-0" aria-hidden />
                            {TENANT_ADMIN_LABELS.list_activate}
                          </Button>
                        ) : (
                          <span className="text-xs text-muted-foreground">
                            {TENANT_ADMIN_LABELS.list_no_actions}
                          </span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
          </tbody>
        </table>
      </div>

      {!isLoading && totalItems > PAGE_SIZE && (
        <div className="flex items-center justify-between pt-4 border-t flex-wrap gap-2">
          <p className="text-xs text-muted-foreground">
            {TENANT_ADMIN_LABELS.list_page_prefix} {page} {TENANT_ADMIN_LABELS.list_page_of}{" "}
            {totalPages}
          </p>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              className="min-h-11 min-w-11 sm:min-h-9"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              aria-label={TENANT_ADMIN_LABELS.list_prev_page}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              className="min-h-11 min-w-11 sm:min-h-9"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              aria-label={TENANT_ADMIN_LABELS.list_next_page}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
