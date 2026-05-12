"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Building2, Plus, Search, ChevronLeft, ChevronRight, MoreHorizontal } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { useCompanies } from "@/lib/hooks/queries/platform";
import { usePermission } from "@/lib/hooks/usePermission";
import { useSession } from "next-auth/react";
import type { Company } from "@/lib/api/services/platform";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  active: { label: "Active", color: "bg-green-100 text-green-700" },
  inactive: { label: "Inactive", color: "bg-slate-100 text-slate-500" },
};

const PAGE_SIZE = 10;

export default function CompaniesPage() {
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const router = useRouter();
  const { isCompanyAdmin } = usePermission();
  const { data: session } = useSession();

  // company_admin can only see their own company — redirect them straight there
  useEffect(() => {
    if (isCompanyAdmin) {
      const companyId = (session?.user as Record<string, unknown> | undefined)?.company_id as string | null | undefined;
      if (companyId) {
        router.replace(`/settings/companies/${companyId}`);
      }
    }
  }, [isCompanyAdmin, session, router]);

  // Don't render the list for company_admin — they're being redirected
  const { data, isLoading } = useCompanies(
    isCompanyAdmin ? undefined : { page, page_size: PAGE_SIZE },
  );

  const companies: Company[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));

  // Show loading skeleton while company_admin is being redirected
  if (isCompanyAdmin) {
    return (
      <div className="space-y-4 max-w-7xl mx-auto">
        {Array.from({ length: 3 }).map((_, i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  const filtered = search
    ? companies.filter(
        (c) =>
          c.name.toLowerCase().includes(search.toLowerCase()) ||
          c.email.toLowerCase().includes(search.toLowerCase()) ||
          c.company_code.toLowerCase().includes(search.toLowerCase()),
      )
    : companies;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Building2 className="h-6 w-6" />
            Companies
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage companies and their admin users within this tenant.
          </p>
        </div>
        <Button size="sm" className="gap-1.5" asChild>
          <Link href="/settings/companies/new">
            <Plus className="h-4 w-4" />
            New Company
          </Link>
        </Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search by name, email, or code…"
              className="pl-8"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {isLoading ? "Loading…" : `${totalItems} companies`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Company</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Code</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Employee Limit</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Created</th>
                  <th className="pb-2 font-medium w-10"></th>
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
                  : filtered.map((company) => {
                      const sCfg = STATUS_CONFIG[company.status] ?? { label: company.status, color: "" };
                      return (
                        <tr
                          key={company.id}
                          className="border-b last:border-0 hover:bg-muted/30 transition-colors"
                        >
                          <td className="py-3 pr-4">
                            <div>
                              <p className="font-medium">{company.name}</p>
                              <p className="text-xs text-muted-foreground">{company.email}</p>
                            </div>
                          </td>
                          <td className="py-3 pr-4 hidden sm:table-cell font-mono text-xs text-muted-foreground">
                            {company.company_code}
                          </td>
                          <td className="py-3 pr-4">
                            <span
                              className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${sCfg.color}`}
                            >
                              {sCfg.label}
                            </span>
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground text-xs hidden md:table-cell">
                            {company.employee_limit}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground text-xs hidden lg:table-cell">
                            {new Date(company.created_at).toLocaleDateString()}
                          </td>
                          <td className="py-3">
                            <Button variant="ghost" size="sm" asChild>
                              <Link href={`/settings/companies/${company.id}`}>
                                <MoreHorizontal className="h-4 w-4" />
                              </Link>
                            </Button>
                          </td>
                        </tr>
                      );
                    })}
              </tbody>
            </table>
          </div>
          {!isLoading && totalItems > PAGE_SIZE && (
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
    </div>
  );
}
