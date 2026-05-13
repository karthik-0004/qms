"use client";

import type { Route } from "next";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { ArrowLeft, BookOpen, Home, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { useCompleteTrainingAssignment, useCourse, useMyTrainingAssignments } from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import type { TrainingAssignment } from "@/lib/api/services/qms";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";

function CompleteTrainingDialog({
  assignment,
  open,
  onOpenChange,
}: {
  assignment: TrainingAssignment | null;
  open: boolean;
  onOpenChange: (v: boolean) => void;
}) {
  const courseId = assignment?.course_id ?? "";
  const { data: course, isLoading: courseLoading } = useCourse(courseId);
  const completeMut = useCompleteTrainingAssignment();
  const [score, setScore] = useState<string>("");
  const [notes, setNotes] = useState("");
  const [sig, setSig] = useState("");

  const requiresSig = course?.requires_certification === true;

  const onSubmit = () => {
    if (!assignment) return;
    if (requiresSig && !sig.trim()) {
      toast.error("E-signature is required for certified courses.");
      return;
    }
    const n = score.trim() === "" ? undefined : Number(score);
    if (score.trim() !== "" && Number.isNaN(n)) {
      toast.error("Score must be a number.");
      return;
    }
    completeMut.mutate(
      {
        assignmentId: assignment.id,
        data: {
          score: n ?? null,
          notes: notes.trim() || null,
          e_signature: requiresSig ? sig.trim() : null,
        },
      },
      {
        onSuccess: () => {
          toast.success("Training marked complete.");
          onOpenChange(false);
          setScore("");
          setNotes("");
          setSig("");
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Complete training</DialogTitle>
          <DialogDescription>
            {courseLoading ? "Loading course…" : course?.title ?? "Course"}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-3 py-2">
          <div>
            <Label htmlFor="sc">Score (optional)</Label>
            <Input id="sc" inputMode="numeric" value={score} onChange={(e) => setScore(e.target.value)} className="mt-1" />
          </div>
          <div>
            <Label htmlFor="nt">Notes</Label>
            <Textarea id="nt" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} className="mt-1" />
          </div>
          {requiresSig && (
            <div>
              <Label htmlFor="es">E-signature (required)</Label>
              <Input id="es" value={sig} onChange={(e) => setSig(e.target.value)} className="mt-1" autoComplete="off" />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            Cancel
          </Button>
          <Button onClick={onSubmit} disabled={completeMut.isPending || courseLoading}>
            {completeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Submit"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

export default function MyTrainingPage() {
  const router = useRouter();
  const { hasPermission, isLoading: permLoading } = usePermission();
  const canRead = hasPermission("training:read");
  const canWrite = hasPermission("training:write");

  const { data, isLoading, isError, error } = useMyTrainingAssignments({ page: 1, page_size: 50 });
  const items = data?.items ?? [];

  const [dialogAssignment, setDialogAssignment] = useState<TrainingAssignment | null>(null);

  if (permLoading) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading…
      </div>
    );
  }

  if (!canRead) {
    return <p className="p-6 text-destructive text-sm">You do not have permission to view training assignments.</p>;
  }

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm flex-wrap">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")} className="h-7 px-2">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training" as Route)} className="h-7 px-2">
          <Home className="h-4 w-4 mr-1" />
          Training
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium inline-flex items-center gap-1">
          <BookOpen className="h-4 w-4" />
          My training
        </span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">My training</h1>
        <p className="text-muted-foreground text-sm mt-1">Assignments issued to your account.</p>
      </div>

      {isError && (
        <p className="text-destructive text-sm">{handleApiError(error)}</p>
      )}

      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {isLoading ? "Loading…" : `${items.length} assignment(s)`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No assignments found.</p>
          ) : (
            <ul className="space-y-2">
              {items.map((a) => (
                <li
                  key={a.id}
                  className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-md border border-border px-3 py-3"
                >
                  <div className="text-sm min-w-0">
                    <p className="font-mono text-xs text-muted-foreground">Course {a.course_id}</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Due {a.due_date ? new Date(a.due_date).toLocaleDateString() : "—"} · Status {a.status}
                    </p>
                  </div>
                  {canWrite && a.status !== "completed" && (
                    <Button
                      size="sm"
                      className="min-h-11 shrink-0"
                      onClick={() => setDialogAssignment(a)}
                    >
                      Complete
                    </Button>
                  )}
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <CompleteTrainingDialog
        assignment={dialogAssignment}
        open={!!dialogAssignment}
        onOpenChange={(v) => {
          if (!v) setDialogAssignment(null);
        }}
      />
    </div>
  );
}
