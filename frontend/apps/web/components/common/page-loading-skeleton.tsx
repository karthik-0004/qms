import { Skeleton } from "@/components/ui/skeleton";

/** Shown during segment navigation so the UI does not feel frozen. */
export function PageLoadingSkeleton() {
  return (
    <div className="space-y-6 p-1" aria-busy="true" aria-label="Loading page">
      <div className="space-y-2">
        <Skeleton className="h-8 w-48 max-w-full" />
        <Skeleton className="h-4 w-96 max-w-full" />
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full" />
        <Skeleton className="h-32 w-full sm:col-span-2 lg:col-span-1" />
      </div>
      <Skeleton className="h-64 w-full" />
    </div>
  );
}
