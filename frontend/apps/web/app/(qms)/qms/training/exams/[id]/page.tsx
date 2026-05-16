"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, FileText, Home, Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useExam, useExamQuestions, useAddExamQuestion } from "@/lib/hooks/queries/qms"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"

export default function ExamDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { data: exam, isLoading } = useExam(params.id)
  const { data: questions, isLoading: qLoading } = useExamQuestions(params.id)
  const addQ = useAddExamQuestion()

  const [qDialog, setQDialog] = useState(false)
  const [qText, setQText] = useState("")
  const [options, setOptions] = useState(["", "", "", ""])
  const [correctAnswer, setCorrectAnswer] = useState("0")

  if (isLoading) return <div className="p-6 max-w-5xl mx-auto space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-32 w-full" /></div>
  if (!exam) return <div className="p-6 max-w-5xl mx-auto"><p className="text-destructive">Exam not found.</p></div>

  const handleAddQuestion = () => {
    if (!qText.trim() || options.some((o) => !o.trim())) {
      toast.error("All fields are required")
      return
    }
    addQ.mutate({
      examId: exam.id,
      data: {
        question_text: qText.trim(),
        options: options.map((o) => o.trim()),
        correct_answer: correctAnswer,
        sort_order: (questions ?? []).length,
      },
    }, {
      onSuccess: () => { toast.success("Question added"); setQDialog(false); setQText(""); setOptions(["", "", "", ""]); setCorrectAnswer("0") },
      onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed"),
    })
  }

  const updateOption = (index: number, value: string) => {
    const next = [...options]
    next[index] = value
    setOptions(next)
  }

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training/exams")} className="h-7 px-2"><Home className="h-4 w-4 mr-1" />Exams</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">{exam.title}</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6" />
            {exam.title}
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Passing score: {exam.passing_score}% · {exam.duration_minutes ? `${exam.duration_minutes} min` : "No time limit"} · {exam.question_count} questions
          </p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Questions ({(questions ?? []).length})</CardTitle>
          <Button size="sm" className="gap-1" onClick={() => setQDialog(true)}><Plus className="h-3 w-3" />Add Question</Button>
        </CardHeader>
        <CardContent>
          {qLoading ? (
            <div className="space-y-2"><Skeleton className="h-16 w-full" /><Skeleton className="h-16 w-full" /></div>
          ) : !questions || questions.length === 0 ? (
            <p className="text-sm text-muted-foreground">No questions yet. Add a question to get started.</p>
          ) : (
            <div className="space-y-4">
              {questions.map((q, i) => (
                <div key={q.id} className="rounded-md border p-3">
                  <p className="text-sm font-medium mb-2">Q{i + 1}. {q.question_text}</p>
                  <div className="space-y-1 ml-4">
                    {q.options.map((opt, oi) => (
                      <p key={oi} className={`text-xs ${q.correct_answer === String(oi) ? "text-green-600 font-semibold" : "text-muted-foreground"}`}>
                        {String.fromCharCode(65 + oi)}. {opt} {q.correct_answer === String(oi) && "✓"}
                      </p>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={qDialog} onOpenChange={setQDialog}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Add Question</DialogTitle><DialogDescription>Enter the question text and answer options.</DialogDescription></DialogHeader>
          <div className="space-y-3 py-2">
            <div><Label>Question Text</Label><textarea className="flex w-full rounded-md border border-input bg-background px-3 py-2 text-sm mt-1 min-h-[60px]" value={qText} onChange={(e) => setQText(e.target.value)} placeholder="Enter question..." /></div>
            {options.map((opt, i) => (
              <div key={i} className="flex items-center gap-2">
                <input type="radio" name="correct" checked={correctAnswer === String(i)} onChange={() => setCorrectAnswer(String(i))} className="h-4 w-4" />
                <span className="text-xs font-medium w-4">{String.fromCharCode(65 + i)}.</span>
                <Input value={opt} onChange={(e) => updateOption(i, e.target.value)} placeholder={`Option ${String.fromCharCode(65 + i)}`} className="flex-1" />
              </div>
            ))}
            <p className="text-xs text-muted-foreground">Select the radio button next to the correct answer.</p>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setQDialog(false)}>Cancel</Button>
            <Button onClick={handleAddQuestion} disabled={addQ.isPending || !qText.trim()}>Add</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
