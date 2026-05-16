"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Home, BookOpen, FileText, ClipboardCheck, Eye, Edit3, CheckCircle, Loader2, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Skeleton } from "@/components/ui/skeleton"
import { useQuery } from "@tanstack/react-query"
import { useCourse, useMyTrainingAssignments, useCompleteTrainingAssignment, useExams, useStartExamAttempt, useSubmitExamAttempt } from "@/lib/hooks/queries/qms"
import { documentsApi } from "@/lib/api/services/qms"
import { toast } from "sonner"
import { WorkflowStepBar } from "@/components/qms-shared/WorkflowStepBar"

const STEPS = [
  { id: "intro", label: "Introduction", icon: BookOpen },
  { id: "materials", label: "Materials", icon: FileText },
  { id: "exam", label: "Exam", icon: ClipboardCheck },
  { id: "overview", label: "Overview", icon: Eye },
  { id: "signoff", label: "Sign Off", icon: CheckCircle },
]

export default function TrainingTaskWizardPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const assignmentId = params.id

  const { data: allAssignments, isLoading: aLoading } = useMyTrainingAssignments({ page: 1, page_size: 200 })
  const assignment = allAssignments?.items?.find((a) => a.id === assignmentId)

  const { data: course, isLoading: cLoading } = useCourse(assignment?.course_id ?? "")
  const { data: exams } = useExams({ course_id: assignment?.course_id })
  const completeMut = useCompleteTrainingAssignment()
  const startExamMut = useStartExamAttempt()
  const submitExamMut = useSubmitExamAttempt()

  const [step, setStep] = useState(0)
  const [score, setScore] = useState("")
  const [notes, setNotes] = useState("")
  const [sig, setSig] = useState("")
  const [examAnswers, setExamAnswers] = useState<Record<string, string>>({})
  const [examAttemptId, setExamAttemptId] = useState<string | null>(null)
  const [examSubmitted, setExamSubmitted] = useState(false)
  const [examResult, setExamResult] = useState<{ score: number; passed: boolean; total: number } | null>(null)

  const { data: docContent } = useQuery({
    queryKey: ["document-content", course?.document_id],
    queryFn: () => documentsApi.getContent(course!.document_id!),
    enabled: !!course?.document_id,
    staleTime: 300_000,
  })

  const isLoading = aLoading || cLoading
  const exam = exams?.[0] ?? null
  const requiresSig = course?.requires_certification === true
  const isCompleted = assignment?.status === "completed"

  if (isLoading) {
    return <div className="p-6 max-w-4xl mx-auto space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-64 w-full" /></div>
  }

  if (!assignment) {
    return <div className="p-6 max-w-4xl mx-auto"><p className="text-destructive">Assignment not found.</p></div>
  }

  if (isCompleted) {
    return (
      <div className="space-y-6 p-6 max-w-4xl mx-auto">
        <div className="flex items-center gap-2 text-sm">
          <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training/my-training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />My Training</Button>
        </div>
        <Card>
          <CardContent className="pt-8 text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-3" />
            <h2 className="text-xl font-bold">Training Completed</h2>
            <p className="text-muted-foreground text-sm mt-1">
              You have already completed this training on{" "}
              {assignment.completed_at ? new Date(assignment.completed_at).toLocaleDateString() : "—"}.
            </p>
            {assignment.score !== null && (
              <p className="text-sm mt-2">Score: {assignment.score} · {assignment.passed ? "Passed" : "Failed"}</p>
            )}
            <Button className="mt-4" onClick={() => router.push("/qms/training/my-training")}>Back to My Training</Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  const handleStartExam = async () => {
    if (!exam) return
    try {
      const attempt = await startExamMut.mutateAsync(exam.id)
      setExamAttemptId(attempt.id)
      toast.success("Exam started")
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Failed to start exam")
    }
  }

  const handleSubmitExam = async () => {
    if (!examAttemptId) return
    const unanswered = exam?.questions?.filter((q) => !examAnswers[q.id]) ?? []
    if (unanswered.length > 0) {
      toast.error(`Please answer all questions (${unanswered.length} unanswered)`)
      return
    }
    try {
      const result = await submitExamMut.mutateAsync({ attemptId: examAttemptId, data: { answers: examAnswers } })
      setExamSubmitted(true)
      const total = exam?.questions?.length ?? 1
      setExamResult({ score: result.score ?? 0, passed: result.passed ?? false, total })
      toast.success(result.passed ? "Exam passed!" : "Exam failed")
    } catch (e: any) {
      toast.error(e?.response?.data?.detail || "Failed to submit exam")
    }
  }

  const handleComplete = () => {
    const n = score.trim() === "" ? undefined : Number(score)
    if (score.trim() !== "" && Number.isNaN(n)) { toast.error("Score must be a number."); return }
    if (requiresSig && !sig.trim()) { toast.error("E-signature is required."); return }
    if (exam && !examSubmitted) { toast.error("Please complete the exam before signing off."); return }

    completeMut.mutate({
      assignmentId: assignment.id,
      data: {
        score: n ?? examResult?.score ?? null,
        notes: notes.trim() || null,
        e_signature: requiresSig ? sig.trim() : null,
      },
    }, {
      onSuccess: () => {
        toast.success("Training completed!")
        router.push("/qms/training/my-training")
      },
      onError: (e) => toast.error(e?.response?.data?.detail || "Failed"),
    })
  }

  const contentHtml = typeof docContent === "string" ? docContent : (docContent as any)?.html_snapshot ?? (docContent as any)?.content ?? null

  const canAdvance = (index: number): boolean => {
    if (index === 0) return true
    if (index === 1) return true
    if (index === 2) return !exam || examSubmitted
    if (index === 3) return true
    return true
  }

  return (
    <div className="space-y-6 p-6 max-w-4xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training/my-training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />My Training</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">{course?.title ?? "Training Task"}</span>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight">{course?.title ?? "Training"}</h1>
        <p className="text-muted-foreground text-sm mt-1">
          {course?.course_code} · {course?.department ?? "No department"}
          {assignment?.due_date && ` · Due: ${new Date(assignment.due_date).toLocaleDateString()}`}
        </p>
      </div>

      <WorkflowStepBar steps={STEPS} currentStep={step} />

      <Card>
        <CardContent className="pt-6">
          {/* Step 0: Introduction */}
          {step === 0 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">Introduction</h2>
              </div>
              <p className="text-sm text-muted-foreground">{course?.description ?? "No description available."}</p>
              <div className="grid grid-cols-2 gap-4 pt-2">
                <div className="rounded-md border p-3">
                  <p className="text-xs text-muted-foreground">Type</p>
                  <p className="text-sm font-medium capitalize">{course?.course_type.replace(/_/g, " ")}</p>
                </div>
                <div className="rounded-md border p-3">
                  <p className="text-xs text-muted-foreground">Duration</p>
                  <p className="text-sm font-medium">{course?.duration_hours ? `${course.duration_hours}h` : "Self-paced"}</p>
                </div>
                <div className="rounded-md border p-3">
                  <p className="text-xs text-muted-foreground">Mandatory</p>
                  <p className="text-sm font-medium">{course?.is_mandatory ? "Yes" : "No"}</p>
                </div>
                <div className="rounded-md border p-3">
                  <p className="text-xs text-muted-foreground">Certification</p>
                  <p className="text-sm font-medium">{course?.requires_certification ? "Required" : "Not required"}</p>
                </div>
              </div>
            </div>
          )}

          {/* Step 1: Materials */}
          {step === 1 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">Training Materials</h2>
              </div>
              {course?.document_id ? (
                contentHtml ? (
                  <div className="rounded-md border p-4 max-h-[60vh] overflow-y-auto prose prose-sm dark:prose-invert" dangerouslySetInnerHTML={{ __html: contentHtml }} />
                ) : (
                  <div className="flex items-center gap-2 text-muted-foreground">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">Loading document content...</span>
                  </div>
                )
              ) : (
                <div className="rounded-md border border-dashed p-6 text-center">
                  <FileText className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">No document linked to this course.</p>
                  <p className="text-xs text-muted-foreground mt-1">Contact your trainer if you expected reference materials.</p>
                </div>
              )}
            </div>
          )}

          {/* Step 2: Exam */}
          {step === 2 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <ClipboardCheck className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">Exam</h2>
              </div>
              {!exam ? (
                <div className="rounded-md border border-dashed p-6 text-center">
                  <ClipboardCheck className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">No exam required for this course.</p>
                </div>
              ) : examSubmitted && examResult ? (
                <div className="text-center py-4">
                  {examResult.passed ? (
                    <CheckCircle className="h-10 w-10 text-green-500 mx-auto mb-2" />
                  ) : (
                    <AlertTriangle className="h-10 w-10 text-amber-500 mx-auto mb-2" />
                  )}
                  <p className="text-lg font-bold">{examResult.passed ? "Passed!" : "Failed"}</p>
                  <p className="text-sm text-muted-foreground">Score: {examResult.score}/{examResult.total * 100} ({Math.round((examResult.score / (examResult.total * 100)) * 100)}%)</p>
                </div>
              ) : examAttemptId ? (
                <div className="space-y-4">
                  {exam.questions?.map((q, qi) => (
                    <div key={q.id} className="rounded-md border p-3">
                      <p className="text-sm font-medium mb-2">Q{qi + 1}. {q.question_text}</p>
                      <div className="space-y-2">
                        {q.options.map((opt, oi) => (
                          <label key={oi} className="flex items-center gap-2 cursor-pointer text-sm">
                            <input
                              type="radio"
                              name={`q-${q.id}`}
                              checked={examAnswers[q.id] === String(oi)}
                              onChange={() => setExamAnswers((prev) => ({ ...prev, [q.id]: String(oi) }))}
                              className="h-4 w-4"
                            />
                            {String.fromCharCode(65 + oi)}. {opt}
                          </label>
                        ))}
                      </div>
                    </div>
                  ))}
                  <div className="flex justify-end pt-2">
                    <Button onClick={handleSubmitExam} disabled={submitExamMut.isPending}>
                      {submitExamMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                      Submit Exam
                    </Button>
                  </div>
                </div>
              ) : (
                <div className="text-center py-4">
                  <ClipboardCheck className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm mb-4">This course has an exam with {exam.question_count} questions. Passing score: {exam.passing_score}%.</p>
                  <Button onClick={handleStartExam} disabled={startExamMut.isPending}>
                    {startExamMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                    Start Exam
                  </Button>
                </div>
              )}
            </div>
          )}

          {/* Step 3: Overview */}
          {step === 3 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Eye className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">Overview</h2>
              </div>
              <p className="text-sm text-muted-foreground">Review what you have learned in this training session.</p>
              <div className="space-y-3">
                <div className="rounded-md border p-3 flex items-center gap-3">
                  <BookOpen className="h-5 w-5 text-green-500" />
                  <div><p className="text-sm font-medium">Introduction Reviewed</p><p className="text-xs text-muted-foreground">Course overview completed</p></div>
                  <CheckCircle className="h-4 w-4 text-green-500 ml-auto" />
                </div>
                <div className="rounded-md border p-3 flex items-center gap-3">
                  <FileText className="h-5 w-5 text-green-500" />
                  <div><p className="text-sm font-medium">Materials Reviewed</p><p className="text-xs text-muted-foreground">Training content accessed</p></div>
                  <CheckCircle className="h-4 w-4 text-green-500 ml-auto" />
                </div>
                <div className="rounded-md border p-3 flex items-center gap-3">
                  <ClipboardCheck className={`h-5 w-5 ${examSubmitted || !exam ? "text-green-500" : "text-muted-foreground"}`} />
                  <div><p className="text-sm font-medium">Exam {!exam ? "Not Required" : examSubmitted ? "Completed" : "Pending"}</p><p className="text-xs text-muted-foreground">{exam ? (examSubmitted ? `Score: ${examResult?.score}` : "Not yet started") : "No exam for this course"}</p></div>
                  {(!exam || examSubmitted) && <CheckCircle className="h-4 w-4 text-green-500 ml-auto" />}
                </div>
              </div>
            </div>
          )}

          {/* Step 4: Sign Off */}
          {step === 4 && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="h-5 w-5 text-primary" />
                <h2 className="text-lg font-semibold">Sign Off</h2>
              </div>
              <p className="text-sm text-muted-foreground">Complete the training by providing your score and signature.</p>
              <div className="space-y-3 max-w-md">
                <div>
                  <Label htmlFor="score">Score (%{, optional)</Label>
                  <Input id="score" inputMode="numeric" value={score} onChange={(e) => setScore(e.target.value)} placeholder="e.g. 85" />
                </div>
                <div>
                  <Label htmlFor="notes">Notes</Label>
                  <Textarea id="notes" value={notes} onChange={(e) => setNotes(e.target.value)} rows={2} placeholder="Any additional notes..." />
                </div>
                {requiresSig && (
                  <div>
                    <Label htmlFor="sig">E-signature (required)</Label>
                    <Input id="sig" value={sig} onChange={(e) => setSig(e.target.value)} placeholder="Type your full name" autoComplete="off" />
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between mt-8 pt-4 border-t">
            <Button variant="outline" size="sm" onClick={() => setStep((s) => Math.max(0, s - 1))} disabled={step === 0}>
              Previous
            </Button>
            <p className="text-xs text-muted-foreground">{step + 1} of {STEPS.length}</p>
            {step < STEPS.length - 1 ? (
              <Button size="sm" onClick={() => setStep((s) => Math.min(STEPS.length - 1, s + 1))} disabled={!canAdvance(step)}>
                Next
              </Button>
            ) : (
              <Button size="sm" onClick={handleComplete} disabled={completeMut.isPending}>
                {completeMut.isPending ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                Complete Training
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
