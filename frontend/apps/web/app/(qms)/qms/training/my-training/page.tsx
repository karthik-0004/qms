"use client"

import type { Route } from "next"
import { useRouter } from "next/navigation"
import { ArrowLeft, BookOpen, Home, Loader2, ExternalLink } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useMyTrainingAssignments, useCourses } from "@/lib/hooks/queries/qms"
import { usePermission } from "@/lib/hooks/usePermission"
import type { TrainingAssignment } from "@/lib/api/services/qms"
import { handleApiError } from "@/lib/api/client"

const STATUS_STYLES: Record<string, { label: string; class: string }> = {
  assigned: { label: "Assigned", class: "bg-blue-100 text-blue-700" },
  in_progress: { label: "In Progress", class: "bg-amber-100 text-amber-700" },
  completed: { label: "Completed", class: "bg-green-100 text-green-700" },
}

export default function MyTrainingPage() {
  const router = useRouter()
  const { hasPermission, isLoading: permLoading } = usePermission()
  const canRead = hasPermission("training:read")
  const canWrite = hasPermission("training:write")

  const { data, isLoading, isError, error } = useMyTrainingAssignments({ page: 1, page_size: 50 })
  const items: TrainingAssignment[] = data?.items ?? []

  const courseIds = [...new Set(items.map((a) => a.course_id))]
  const { data: coursesData } = useCourses({ page_size: 200 })
  const allCourses = coursesData?.items ?? []

  if (permLoading) {
    return <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground"><Loader2 className="h-5 w-5 animate-spin" />Loading...</div>
  }

  if (!canRead) {
    return <p className="p-6 text-destructive text-sm">You do not have permission to view training assignments.</p>
  }

  const courseTitleMap = new Map(allCourses.map((c) => [c.id, c.title]))

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm flex-wrap">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium inline-flex items-center gap-1"><BookOpen className="h-4 w-4" />My training</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">My training</h1>
        <p className="text-muted-foreground text-sm mt-1">Assignments issued to your account.</p>
      </div>

      {isError && <p className="text-destructive text-sm">{handleApiError(error)}</p>}

      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {isLoading ? "Loading..." : `${items.length} assignment(s)`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-4">
          {isLoading ? (
            <div className="space-y-2"><Skeleton className="h-16 w-full" /><Skeleton className="h-16 w-full" /></div>
          ) : items.length === 0 ? (
            <p className="text-sm text-muted-foreground">No assignments found.</p>
          ) : (
            <div className="space-y-2">
              {items.map((a) => {
                const statusCfg = STATUS_STYLES[a.status] ?? { label: a.status, class: "bg-slate-100 text-slate-600" }
                const courseTitle = a.course_title ?? courseTitleMap.get(a.course_id) ?? a.course_id
                return (
                  <div key={a.id} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 rounded-md border px-4 py-3 hover:bg-muted/30 transition-colors">
                    <div className="text-sm min-w-0">
                      <p className="font-medium truncate">{courseTitle}</p>
                      <div className="flex items-center gap-2 mt-1">
                        <span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${statusCfg.class}`}>{statusCfg.label}</span>
                        {a.due_date && <span className="text-xs text-muted-foreground">Due {new Date(a.due_date).toLocaleDateString()}</span>}
                      </div>
                    </div>
                    {canWrite && a.status !== "completed" ? (
                      <Button size="sm" className="gap-1 shrink-0" onClick={() => router.push(`/qms/training/my-training/${a.id}` as Route)}>
                        <ExternalLink className="h-3 w-3" />
                        Start
                      </Button>
                    ) : a.status === "completed" ? (
                      <span className="text-xs text-muted-foreground">{a.score !== null ? `Score: ${a.score}` : "Completed"}</span>
                    ) : null}
                  </div>
                )
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
