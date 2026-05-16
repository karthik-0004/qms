"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Home, Plus, Link2, Unlink, Trash2, Users, BookOpen } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useJobCode, useJobCodeCourses, useLinkCourseToJobCode, useUnlinkCourseFromJobCode, useJobCodeAssignees, useAssignUserToJobCode, useUnassignUserFromJobCode, useCourses, useUpdateJobCode } from "@/lib/hooks/queries/qms"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"

export default function JobCodeDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter()
  const { data: jc, isLoading } = useJobCode(params.id)
  const { data: courses, isLoading: coursesLoading } = useJobCodeCourses(params.id)
  const { data: allCourses } = useCourses({ page_size: 200 })
  const { data: assignees } = useJobCodeAssignees(params.id)

  const linkMut = useLinkCourseToJobCode()
  const unlinkMut = useUnlinkCourseFromJobCode()
  const assignMut = useAssignUserToJobCode()
  const unassignMut = useUnassignUserFromJobCode()
  const updateMut = useUpdateJobCode()

  const [linkDialog, setLinkDialog] = useState(false)
  const [selectedCourse, setSelectedCourse] = useState("")
  const [userDialog, setUserDialog] = useState(false)
  const [userId, setUserId] = useState("")

  if (isLoading) return <div className="p-6 max-w-5xl mx-auto space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-32 w-full" /></div>
  if (!jc) return <div className="p-6 max-w-5xl mx-auto"><p className="text-destructive">Job code not found.</p></div>

  const availableCourses = (allCourses?.items ?? []).filter((c) => !courses?.some((l) => l.course_id === c.id))

  const handleLink = () => {
    if (!selectedCourse) return
    linkMut.mutate({ jobCodeId: jc.id, data: { course_id: selectedCourse } }, {
      onSuccess: () => { toast.success("Course linked"); setLinkDialog(false); setSelectedCourse("") },
      onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed"),
    })
  }

  const handleUnlink = (courseId: string) => {
    unlinkMut.mutate({ jobCodeId: jc.id, courseId }, { onSuccess: () => toast.success("Course unlinked") })
  }

  const handleAssignUser = () => {
    if (!userId.trim()) return
    assignMut.mutate({ jobCodeId: jc.id, data: { user_id: userId.trim() } }, {
      onSuccess: () => { toast.success("User assigned"); setUserDialog(false); setUserId("") },
      onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed"),
    })
  }

  const getCourseTitle = (courseId: string) => {
    const link = courses?.find((l) => l.course_id === courseId)
    return link?.course_title ?? courseId
  }

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training/job-codes")} className="h-7 px-2"><Home className="h-4 w-4 mr-1" />Job Codes</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">{jc.code}</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{jc.code}: {jc.title}</h1>
          <p className="text-muted-foreground text-sm mt-1">{jc.department ?? "No department"}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={() => router.push(`/qms/training/job-codes/${jc.id}/status`)}>Status Matrix</Button>
        </div>
      </div>

      {jc.description && (
        <Card>
          <CardHeader><CardTitle>Description</CardTitle></CardHeader>
          <CardContent><p className="text-sm text-muted-foreground">{jc.description}</p></CardContent>
        </Card>
      )}

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2"><BookOpen className="h-4 w-4" />Required Courses ({courses?.length ?? 0})</CardTitle>
          <Button size="sm" variant="outline" className="gap-1" onClick={() => setLinkDialog(true)}><Link2 className="h-3 w-3" />Link Course</Button>
        </CardHeader>
        <CardContent>
          {!courses || courses.length === 0 ? (
            <p className="text-sm text-muted-foreground">No courses linked. Link a course to define training requirements.</p>
          ) : (
            <div className="space-y-2">
              {courses.map((link) => (
                <div key={link.id} className="flex items-center justify-between rounded-md border px-3 py-2">
                  <div className="flex items-center gap-2">
                    <BookOpen className="h-4 w-4 text-muted-foreground" />
                    <p className="text-sm font-medium">{link.course_title ?? link.course_id}</p>
                    {link.is_required && <span className="text-xs bg-amber-100 text-amber-700 px-1.5 py-0.5 rounded">Required</span>}
                  </div>
                  <Button size="sm" variant="ghost" className="text-destructive" onClick={() => handleUnlink(link.course_id)}><Unlink className="h-3 w-3" /></Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2"><Users className="h-4 w-4" />Assignees ({assignees?.length ?? 0})</CardTitle>
          <Button size="sm" variant="outline" className="gap-1" onClick={() => setUserDialog(true)}><Plus className="h-3 w-3" />Assign User</Button>
        </CardHeader>
        <CardContent>
          {!assignees || assignees.length === 0 ? (
            <p className="text-sm text-muted-foreground">No users assigned to this job code.</p>
          ) : (
            <div className="space-y-2">
              {assignees.map((a) => (
                <div key={a.id} className="flex items-center justify-between rounded-md border px-3 py-2">
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <p className="text-sm font-medium">{a.user_id.slice(0, 8)}...</p>
                    {a.is_primary && <span className="text-xs bg-blue-100 text-blue-700 px-1.5 py-0.5 rounded">Primary</span>}
                  </div>
                  <Button size="sm" variant="ghost" className="text-destructive" onClick={() => unassignMut.mutate({ jobCodeId: jc.id, userId: a.user_id }, { onSuccess: () => toast.success("User unassigned") })}><Trash2 className="h-3 w-3" /></Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Dialog open={linkDialog} onOpenChange={setLinkDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Link Course</DialogTitle><DialogDescription>Select a course to add to this job code.</DialogDescription></DialogHeader>
          <div className="py-2">
            <Label>Course</Label>
            <select className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm mt-1" value={selectedCourse} onChange={(e) => setSelectedCourse(e.target.value)}>
              <option value="">Select a course...</option>
              {availableCourses.map((c) => <option key={c.id} value={c.id}>{c.course_code} — {c.title}</option>)}
            </select>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setLinkDialog(false)}>Cancel</Button>
            <Button onClick={handleLink} disabled={!selectedCourse || linkMut.isPending}>Link</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={userDialog} onOpenChange={setUserDialog}>
        <DialogContent>
          <DialogHeader><DialogTitle>Assign User</DialogTitle><DialogDescription>Enter the user ID to assign to this job code.</DialogDescription></DialogHeader>
          <div className="py-2">
            <Label>User ID</Label>
            <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="UUID of the user" className="mt-1" />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setUserDialog(false)}>Cancel</Button>
            <Button onClick={handleAssignUser} disabled={!userId.trim() || assignMut.isPending}>Assign</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
