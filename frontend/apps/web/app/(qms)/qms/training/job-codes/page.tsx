"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, Users, Home, Plus, Search } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useJobCodes, useCreateJobCode } from "@/lib/hooks/queries/qms"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from "@/components/ui/dialog"

export default function JobCodesPage() {
  const router = useRouter()
  const [search, setSearch] = useState("")
  const [dialogOpen, setDialogOpen] = useState(false)
  const [code, setCode] = useState("")
  const [title, setTitle] = useState("")
  const [department, setDepartment] = useState("")
  const [description, setDescription] = useState("")

  const { data: jobCodes, isLoading } = useJobCodes()
  const create = useCreateJobCode()

  const filtered = (jobCodes ?? []).filter((jc) => {
    const q = search.trim().toLowerCase()
    return !q || jc.code.toLowerCase().includes(q) || jc.title.toLowerCase().includes(q) || (jc.department ?? "").toLowerCase().includes(q)
  })

  const handleCreate = () => {
    create.mutate({ code, title, department: department || undefined, description: description || undefined }, {
      onSuccess: () => { toast.success("Job code created"); setDialogOpen(false); setCode(""); setTitle(""); setDepartment(""); setDescription("") },
      onError: (e: any) => toast.error(e?.response?.data?.detail || e?.message || "Failed to create"),
    })
  }

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium flex items-center gap-1"><Users className="h-4 w-4" />Job Codes</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Job Codes</h1>
          <p className="text-muted-foreground text-sm mt-1">Role definitions and training requirements</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild><Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />New Job Code</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Create Job Code</DialogTitle><DialogDescription>Define a new role with training requirements.</DialogDescription></DialogHeader>
            <div className="space-y-3 py-2">
              <div><Label>Code</Label><Input value={code} onChange={(e) => setCode(e.target.value)} placeholder="QC-001" /></div>
              <div><Label>Title</Label><Input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Quality Control Inspector" /></div>
              <div><Label>Department</Label><Input value={department} onChange={(e) => setDepartment(e.target.value)} placeholder="QA" /></div>
              <div><Label>Description</Label><Input value={description} onChange={(e) => setDescription(e.target.value)} /></div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={create.isPending || !code.trim() || !title.trim()}>Create</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="relative">
            <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input placeholder="Search job codes..." className="pl-8" value={search} onChange={(e) => setSearch(e.target.value)} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{isLoading ? "Loading..." : `${filtered.length} job codes`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          {isLoading ? (
            <div className="space-y-2"><Skeleton className="h-12 w-full" /><Skeleton className="h-12 w-full" /></div>
          ) : filtered.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4">No job codes found.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">Code</th>
                    <th className="pb-2 pr-4 font-medium">Title</th>
                    <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Department</th>
                    <th className="pb-2 pr-4 font-medium hidden md:table-cell">Courses</th>
                    <th className="pb-2 pr-4 font-medium hidden md:table-cell">Users</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((jc) => (
                    <tr key={jc.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{jc.code}</td>
                      <td className="py-3 pr-4 font-medium">{jc.title}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{jc.department ?? "—"}</td>
                      <td className="py-3 pr-4 hidden md:table-cell">{jc.course_count}</td>
                      <td className="py-3 pr-4 hidden md:table-cell">{jc.user_count}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${jc.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>{jc.is_active ? "Active" : "Inactive"}</span></td>
                      <td className="py-3 pr-4">
                        <div className="flex gap-1">
                          <Button variant="ghost" size="sm" onClick={() => router.push(`/qms/training/job-codes/${jc.id}`)}>View</Button>
                          <Button variant="ghost" size="sm" onClick={() => router.push(`/qms/training/job-codes/${jc.id}/status`)}>Matrix</Button>
                        </div>
                      </td>
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
