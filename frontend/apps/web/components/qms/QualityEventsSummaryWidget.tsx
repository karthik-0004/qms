"use client";

import Link from "next/link";
import type { Route } from "next";
import { useEffect } from "react";
import { AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useQualityEventsSummary } from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

export function QualityEventsSummaryWidget() {
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("quality_event:read");
  const { data, isLoading, isError, error } = useQualityEventsSummary();

  useEffect(() => {
    if (isError && error) toast.error(handleApiError(error));
  }, [isError, error]);

  if (permLoading || !canRead) return null;

  if (isError) {
    return (
      <Card className="border-amber-200 bg-amber-50/50 dark:bg-amber-950/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            Quality events summary
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">Unable to load summary.</CardContent>
      </Card>
    );
  }

  const rows = data?.by_status ? Object.entries(data.by_status) : [];

  return (
    <Card>
      <CardHeader className="pb-2 flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <AlertTriangle className="h-4 w-4" />
          Quality events by status
        </CardTitle>
        <Button variant="ghost" size="sm" className="shrink-0 min-h-9" asChild>
          <Link href={"/qms/quality-events" as Route}>All events</Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-8 w-full" />
          </div>
        ) : rows.length === 0 ? (
          <p className="text-sm text-muted-foreground">No quality event counts available.</p>
        ) : (
          <ul className="space-y-1.5 text-sm">
            {rows.map(([status, count]) => (
              <li key={status} className="flex justify-between gap-2 rounded-md border border-border px-3 py-2 min-h-11 items-center">
                <span className="capitalize text-muted-foreground">{status.replace(/_/g, " ")}</span>
                <span className="font-semibold tabular-nums">{count}</span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
