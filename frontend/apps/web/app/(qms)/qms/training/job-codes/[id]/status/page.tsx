"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, Home, BarChart3 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { MatrixGrid } from "@/components/qms-shared/MatrixGrid"
import { useJobCode, useJobCodeStatusMatrix } from "@/lib/hooks/queries/qms"

export default function JobCodeStatusMatrixPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { data: jc, isLoading: jcLoading } = useJobCode(params.id)
  const { data: matrix, isLoading: matrixLoading } = useJobCodeStatusMatrix(params.id)

  if (jcLoading) return <div className="p-6 max-w-7xl mx-auto space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-96 w-full" /></div>
  if (!jc) return <div className="p-6 max-w-7xl mx-auto"><p className="text-destructive">Job code not found.</p></div>

  const columns = (matrix && matrix.length > 0 ? matrix[0].courses : []).map((c) => ({
    id: c.course_id,
    label: c.course_title,
  }))

  const rows = (matrix ?? []).map((row) => {
    const cells: Record<string, "complete" | "in_progress" | "overdue" | "waiting" | "pending" | "none"> = {}
    row.courses.forEach((c) => {
      if (c.status === "completed" && c.passed) {
        cells[c.course_id] = "complete"
      } else if (c.status === "in_progress") {
        cells[c.course_id] = "in_progress"
      } else if (c.status === "assigned" && c.due_date && new Date(c.due_date) < new Date()) {
        cells[c.course_id] = "overdue"
      } else if (c.status === "assigned") {
        cells[c.course_id] = "pending"
      } else {
        cells[c.course_id] = "none"
      }
    })
    return {
      id: row.user_id,
      label: row.user_name ?? row.user_id.slice(0, 12) + "...",
      cells,
    }
  })

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training/job-codes")} className="h-7 px-2"><Home className="h-4 w-4 mr-1" />Job Codes</Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push(`/qms/training/job-codes/${jc.id}`)} className="h-7 px-2">{jc.code}</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium flex items-center gap-1"><BarChart3 className="h-4 w-4" />Status Matrix</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">{jc.code}: {jc.title}</h1>
        <p className="text-muted-foreground text-sm mt-1">Training compliance status matrix</p>
      </div>

      <Card>
        <CardHeader><CardTitle>Compliance Matrix</CardTitle></CardHeader>
        <CardContent>
          {matrixLoading ? (
            <Skeleton className="h-96 w-full" />
          ) : !matrix || matrix.length === 0 ? (
            <p className="text-sm text-muted-foreground">No users assigned to this job code yet.</p>
          ) : (
            <MatrixGrid
              columns={columns}
              rows={rows}
              columnLabel="User"
            />
          )}
        </CardContent>
      </Card>
    </div>
  )
}
