"use client"

import { useRouter } from "next/navigation"
import { ArrowLeft, BookOpen, Home, FileText, Clock, Target, Award, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useCourse, useExams } from "@/lib/hooks/queries/qms"
import { StatusBadge } from "@/components/qms-shared/StatusBadge"
import { DateInfoGrid } from "@/components/qms-shared/DateInfoGrid"

export default function CourseDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { data: course, isLoading } = useCourse(params.id)
  const { data: exams } = useExams({ course_id: params.id })

  if (isLoading) {
    return <div className="p-6 max-w-5xl mx-auto space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-32 w-full" /></div>
  }

  if (!course) {
    return <div className="p-6 max-w-5xl mx-auto"><p className="text-destructive">Course not found.</p></div>
  }

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training/courses")} className="h-7 px-2"><Home className="h-4 w-4 mr-1" />Courses</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">{course.course_code}</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <BookOpen className="h-6 w-6" />
            {course.title}
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Code: {course.course_code}</p>
        </div>
        <StatusBadge status={course.is_active ? "active" : "inactive"} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground flex items-center gap-1"><Target className="h-3 w-3" />Passing Score</CardTitle></CardHeader>
          <CardContent><p className="text-lg font-bold">{course.passing_score}%</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground flex items-center gap-1"><Clock className="h-3 w-3" />Duration</CardTitle></CardHeader>
          <CardContent><p className="text-lg font-bold">{course.duration_hours ? `${course.duration_hours}h` : "—"}</p></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-xs text-muted-foreground flex items-center gap-1"><Award className="h-3 w-3" />Certification</CardTitle></CardHeader>
          <CardContent><p className="text-lg font-bold">{course.requires_certification ? "Required" : "Not required"}</p></CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Details</CardTitle></CardHeader>
        <CardContent>
          <DateInfoGrid
            items={[
              { label: "Department", value: course.department ?? "—" },
              { label: "Course Type", value: course.course_type.replace(/_/g, " ") },
              { label: "Mandatory", value: course.is_mandatory ? "Yes" : "No" },
              { label: "Recurrence", value: course.recurrence_days ? `${course.recurrence_days} days` : "—" },
              { label: "Document ID", value: course.document_id ?? "—" },
              { label: "Created By", value: course.created_by },
            ]}
          />
        </CardContent>
      </Card>

      {course.description && (
        <Card>
          <CardHeader><CardTitle>Description</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground whitespace-pre-wrap">{course.description}</p></CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2"><FileText className="h-4 w-4" />Exams ({exams?.length ?? 0})</CardTitle>
          <Button size="sm" variant="outline" onClick={() => router.push(`/qms/training/exams`)}>Manage Exams</Button>
        </CardHeader>
        <CardContent>
          {!exams || exams.length === 0 ? (
            <p className="text-sm text-muted-foreground">No exams linked to this course.</p>
          ) : (
            <div className="space-y-2">
              {exams.map((exam) => (
                <div key={exam.id} className="flex items-center justify-between rounded-md border px-3 py-2">
                  <div>
                    <p className="text-sm font-medium">{exam.title}</p>
                    <p className="text-xs text-muted-foreground">{exam.question_count} questions · Passing: {exam.passing_score}%</p>
                  </div>
                  <Button size="sm" variant="ghost" onClick={() => router.push(`/qms/training/exams/${exam.id}`)}>View</Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
