"use client";

import Link from "next/link";
import type { Route } from "next";
import { Building2, ChevronLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { TenantsTab } from "../tenants-admin-tab";

export default function AdminTenantsPage() {
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-start gap-3">
          <Button variant="outline" size="icon" className="shrink-0 min-h-11 min-w-11" asChild>
            <Link href={"/super-admin" as Route} aria-label="Back to admin overview">
              <ChevronLeft className="h-4 w-4" />
            </Link>
          </Button>
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-10 h-10 rounded-xl bg-blue-600 flex items-center justify-center shrink-0">
              <Building2 className="h-5 w-5 text-white" />
            </div>
            <div className="min-w-0">
              <h1 className="text-2xl font-bold tracking-tight">Tenants</h1>
              <p className="text-muted-foreground text-sm">
                Provision tenants and open a workspace by URL slug.
              </p>
            </div>
          </div>
        </div>
      </div>

      <TenantsTab />
    </div>
  );
}
