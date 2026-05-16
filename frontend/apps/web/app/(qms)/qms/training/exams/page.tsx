"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, FileText, Home, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useExams, useCreateExam, useCourses } from "@/lib/hooks/queries/qms"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from "@/components/ui/dialog"

export default function ExamsPage() {
  const router = useRouter()
  const { data: exams, isLoading } = useExams()
  const { data: coursesData } = useCourses({ page_size: 200 })
  const create = useCreateExam()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [title, setTitle] = useState("")
  const [courseId, setCourseId] = useState("")
  const [passingScore, setPassingScore] = useState(80)
  const [durationMinutes, setDurationMinutes] = useState("")

  const courses = coursesData?.items ?? []

  const handleCreate = () => {
    create.mutate({
      course_id: courseId,
      title,
      passing_score: passingScore,
      duration_minutes: durationMinutes ? parseInt(durationMinutes) : undefined,
    }, {
      onSuccess: () => { toast.success("Exam created"); setDialogOpen(false); setTitle(""); setCourseId(""); setPassingScore(80); setDurationMinutes("") },
      onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed"),
    })
  }

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium flex items-center gap-1"><FileText className="h-4 w-4" />Exams</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Exams</h1>
          <p className="text-muted-foreground text-sm mt-1">Exam definitions and question banks</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild><Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />New Exam</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Create Exam</DialogTitle><DialogDescription>Define a new exam for a course.</DialogDescription></DialogHeader>
            <div className="space-y-3 py-2">
              <div><Label>Title</Label><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Exam title" /></div>
              <div><Label>Course</Label><select className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1" value={courseId} onChange={(e) => setCourseId(e.target.value)}><option value="">Select course...</option>{courses.map((c) => <option key={c.id} value={c.id}>{c.course_code} — {c.title}</option>)}</select></div>
              <div><Label>Passing Score (%)</Label><Input type="number" min={0} max={100} value={passingScore} onChange={(e) => setPassingScore(parseInt(e.target.value) || 0)} /></div>
              <div><Label>Duration (minutes)</Label><Input type="number" min={0} value={durationMinutes} onChange={(e) => setDurationMinutes(e.target.value)} placeholder="Optional" /></div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={create.isPending || !title.trim() || !courseId}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{isLoading ? "Loading..." : `${(exams ?? []).length} exams`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          {isLoading ? (
            <div className="space-y-2"><Skeleton className="h-12 w-full" /><Skeleton className="h-12 w-full" /></div>
          ) : !exams || exams.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4">No exams defined.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Title</th>
                    <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Questions</th>
                    <th className="pb-2 pr-4 font-medium hidden md:table-cell">Passing Score</th>
                    <th className="pb-2 pr-4 font-medium hidden md:table-cell">Duration</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {exams.map((exam) => (
                    <tr key={exam.id} className="border-b last:border-0 hover:bg-muted/30 cursor-pointer" onClick={() => router.push(`/qms/training/exams/${exam.id}`)}>
                      <td className="py-3 pr-4 font-medium">{exam.title}</td>
                      <td className="py-3 pr-4 hidden sm:table-cell">{exam.question_count}</td>
                      <td className="py-3 pr-4 hidden md:table-cell">{exam.passing_score}%</td>
                      <td className="py-3 pr-4 hidden md:table-cell">{exam.duration_minutes ? `${exam.duration_minutes}min` : "—"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${exam.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>{exam.is_active ? "Active" : "Inactive"}</span></td>
                      <td className="py-3 pr-4"><Button variant="ghost" size="sm" onClick={(e) => { e.stopPropagation(); router.push(`/qms/training/exams/${exam.id}`) }}>Edit</Button></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
