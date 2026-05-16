"use client"

import { useRouter } from "next/navigation"
import { GraduationCap, BookOpen, ClipboardCheck, Users, FileText, Award, AlertTriangle, Clock, BarChart3, RefreshCw, UserCheck } from "lucide-react"
import { DashboardTiles } from "@/components/qms-shared/DashboardTiles"
import { ModuleHeader } from "@/components/qms-shared/ModuleHeader"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Skeleton } from "@/components/ui/skeleton"
import { useTrainingDashboardStats } from "@/lib/hooks/queries/qms"

export default function TrainingDashboardPage() {
  const router = useRouter()
  const { data: stats, isLoading } = useTrainingDashboardStats()

  const tiles = [
    { id: "courses", icon: <BookOpen className="h-5 w-5" />, label: "Courses", count: stats?.total_courses, description: "Active training courses", onClick: () => router.push("/qms/training/courses") },
    { id: "my-training", icon: <ClipboardCheck className="h-5 w-5" />, label: "My Training", count: stats?.total_assignments !== undefined ? stats.total_assignments - stats.completed_assignments : undefined, description: "Pending assignments", onClick: () => router.push("/qms/training/my-training") },
    { id: "completed", icon: <Award className="h-5 w-5" />, label: "Completed", count: stats?.completed_assignments, description: "Completed assignments", onClick: () => router.push("/qms/training/my-training") },
    { id: "in-progress", icon: <RefreshCw className="h-5 w-5" />, label: "In Progress", count: stats?.in_progress_assignments, description: "Assignments in progress", onClick: () => router.push("/qms/training/my-training?status=in_progress") },
    { id: "overdue", icon: <AlertTriangle className="h-5 w-5" />, label: "Overdue", count: stats?.overdue_assignments, description: "Past due date", onClick: () => router.push("/qms/training/my-training?status=overdue") },
    { id: "pending", icon: <Clock className="h-5 w-5" />, label: "Pending", count: stats?.pending_assignments, description: "Not yet started", onClick: () => router.push("/qms/training/my-training?status=assigned") },
    { id: "job-codes", icon: <Users className="h-5 w-5" />, label: "Job Codes", count: stats?.total_job_codes, description: "Defined roles", onClick: () => router.push("/qms/training/job-codes") },
    { id: "compliance", icon: <BarChart3 className="h-5 w-5" />, label: "Compliance", count: stats ? Math.round(stats.overall_compliance_pct) : undefined, description: "Overall compliance %", onClick: () => router.push("/qms/training/job-codes") },
    { id: "recertifications", icon: <RefreshCw className="h-5 w-5" />, label: "Upcoming Recert.", count: stats?.upcoming_recertifications, description: "Due within 30 days", onClick: () => router.push("/qms/training/my-training") },
    { id: "trainers", icon: <UserCheck className="h-5 w-5" />, label: "Trainers", count: stats?.total_trainers, description: "Registered trainers", onClick: () => router.push("/qms/training/trainers") },
    { id: "exams", icon: <FileText className="h-5 w-5" />, label: "Exams", description: "Manage exams", onClick: () => router.push("/qms/training/exams") },
  ]

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <ModuleHeader
        icon={<GraduationCap className="h-6 w-6" />}
        title="Training Dashboard"
        description="Training courses, assignments, job codes, exams, and compliance tracking"
      />

      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          {Array.from({ length: 11 }).map((_, i) => (
            <Skeleton key={i} className="h-28 rounded-xl" />
          ))}
        </div>
      ) : (
        <DashboardTiles tiles={tiles} columns={4} />
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Users with Overdue</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats?.users_with_overdue ?? "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Overall Compliance</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats ? `${Math.round(stats.overall_compliance_pct)}%` : "—"}</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Assignments</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold">{stats?.total_assignments ?? "—"}</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
