"use client";

import Link from "next/link";
import type { Route } from "next";
import { useEffect } from "react";
import { GraduationCap } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useTrainingOverdueAssignments } from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

export function TrainingOverdueWidget() {
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("training:read");
  const { data, isLoading, isError, error } = useTrainingOverdueAssignments();

  useEffect(() => {
    if (isError && error) toast.error(handleApiError(error));
  }, [isError, error]);

  if (permLoading || !canRead) return null;

  if (isError) {
    return (
      <Card className="border-amber-200 bg-amber-50/50 dark:bg-amber-950/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <GraduationCap className="h-4 w-4" />
            Overdue training
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">Unable to load overdue assignments.</CardContent>
      </Card>
    );
  }

  const items = data ?? [];

  return (
    <Card>
      <CardHeader className="pb-2 flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <GraduationCap className="h-4 w-4" />
          Overdue training (you)
        </CardTitle>
        <Button variant="ghost" size="sm" className="shrink-0 min-h-9" asChild>
          <Link href={"/qms/training/my-training" as Route}>My training</Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : items.length === 0 ? (
          <p className="text-sm text-muted-foreground">You have no overdue training assignments.</p>
        ) : (
          <ul className="space-y-2">
            {items.slice(0, 5).map((a) => (
              <li key={a.id}>
                <Link
                  href={"/qms/training/my-training" as Route}
                  className="flex flex-col gap-0.5 rounded-md border border-border px-3 py-2 text-sm hover:bg-muted/60 min-h-11"
                >
                  <span className="font-medium">
                    {a.course_title?.trim() ? a.course_title : "Overdue assignment"}
                  </span>
                  <span className="text-xs text-muted-foreground">
                    Due {a.due_date ? new Date(a.due_date).toLocaleDateString() : "—"} ·{" "}
                    <span className="font-mono">{a.id.slice(0, 8)}…</span>
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
