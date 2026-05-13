"use client";

import Link from "next/link";
import type { Route } from "next";
import { useEffect } from "react";
import { Wrench } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useEquipmentDueCalibration } from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

export function EquipmentDueCalibrationWidget() {
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("equipment:read");
  const { data, isLoading, isError, error } = useEquipmentDueCalibration();

  useEffect(() => {
    if (isError && error) toast.error(handleApiError(error));
  }, [isError, error]);

  if (permLoading || !canRead) return null;

  if (isError) {
    return (
      <Card className="border-amber-200 bg-amber-50/50 dark:bg-amber-950/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Wrench className="h-4 w-4" />
            Equipment due for calibration
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">Unable to load calibration queue.</CardContent>
      </Card>
    );
  }

  const items = data ?? [];

  return (
    <Card>
      <CardHeader className="pb-2 flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Wrench className="h-4 w-4" />
          Equipment due for calibration
        </CardTitle>
        <Button variant="ghost" size="sm" className="shrink-0 min-h-9" asChild>
          <Link href={"/qms/equipment" as Route}>All equipment</Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">No equipment is currently due for calibration.</p>
        ) : (
          <ul className="space-y-2">
            {items.slice(0, 5).map((eq) => (
              <li key={eq.id}>
                <Link
                  href={`/qms/equipment/${eq.id}` as Route}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-1 rounded-md border border-border px-3 py-2 text-sm hover:bg-muted/60 min-h-11"
                >
                  <span className="font-medium truncate">{eq.name}</span>
                  <span className="text-xs text-muted-foreground font-mono shrink-0">{eq.asset_tag}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
