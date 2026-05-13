"use client";

import Link from "next/link";
import type { Route } from "next";
import { useEffect } from "react";
import { CalendarClock, FileText } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { useDocumentsDueForReview } from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

export function DocumentsDueReviewWidget() {
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("document:read");
  const { data, isLoading, isError, error } = useDocumentsDueForReview({ days_ahead: 30 });

  useEffect(() => {
    if (isError && error) toast.error(handleApiError(error));
  }, [isError, error]);

  if (permLoading || !canRead) return null;

  if (isError) {
    return (
      <Card className="border-amber-200 bg-amber-50/50 dark:bg-amber-950/20">
        <CardHeader className="pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <CalendarClock className="h-4 w-4" />
            Documents due for review
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm text-muted-foreground">
          Unable to load due-for-review list.
        </CardContent>
      </Card>
    );
  }

  const docs = data ?? [];

  return (
    <Card>
      <CardHeader className="pb-2 flex flex-row items-center justify-between gap-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <CalendarClock className="h-4 w-4" />
          Documents due for review (30 days)
        </CardTitle>
        <Button variant="ghost" size="sm" className="shrink-0 min-h-9" asChild>
          <Link href={"/qms/documents" as Route}>All documents</Link>
        </Button>
      </CardHeader>
      <CardContent className="space-y-2">
        {isLoading ? (
          <div className="space-y-2">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : docs.length === 0 ? (
          <p className="text-sm text-muted-foreground">No documents due for periodic review in this window.</p>
        ) : (
          <ul className="space-y-2">
            {docs.slice(0, 5).map((d) => (
              <li key={d.id}>
                <Link
                  href={`/qms/documents/${d.id}` as Route}
                  className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm hover:bg-muted/60 min-h-11"
                >
                  <FileText className="h-4 w-4 shrink-0 text-muted-foreground" />
                  <span className="font-medium truncate">{d.title}</span>
                  <span className="text-xs text-muted-foreground font-mono shrink-0">{d.doc_number}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
