"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { ArrowLeft, UserCheck, Home, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Skeleton } from "@/components/ui/skeleton"
import { useTrainers, useCreateTrainer, useUpdateTrainer } from "@/lib/hooks/queries/qms"
import { toast } from "sonner"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter, DialogTrigger } from "@/components/ui/dialog"

export default function TrainersPage() {
  const router = useRouter()
  const { data: trainers, isLoading } = useTrainers()
  const create = useCreateTrainer()
  const update = useUpdateTrainer()

  const [dialogOpen, setDialogOpen] = useState(false)
  const [userId, setUserId] = useState("")
  const [qualification, setQualification] = useState("")

  const handleCreate = () => {
    create.mutate({ user_id: userId.trim(), qualification: qualification.trim() || undefined }, {
      onSuccess: () => { toast.success("Trainer registered"); setDialogOpen(false); setUserId(""); setQualification("") },
      onError: (e: any) => toast.error(e?.response?.data?.detail || "Failed"),
    })
  }

  const toggleActive = (trainer: any) => {
    update.mutate({ id: trainer.id, data: { is_active: !trainer.is_active } }, {
      onSuccess: () => toast.success(`Trainer ${trainer.is_active ? "deactivated" : "activated"}`),
    })
  }

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/training")} className="h-7 px-2"><ArrowLeft className="h-4 w-4 mr-1" />Training</Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium flex items-center gap-1"><UserCheck className="h-4 w-4" />Trainers</span>
      </div>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Trainers</h1>
          <p className="text-muted-foreground text-sm mt-1">Registered trainers and instructors</p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild><Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />Register Trainer</Button></DialogTrigger>
          <DialogContent>
            <DialogHeader><DialogTitle>Register Trainer</DialogTitle><DialogDescription>Add a user as a trainer.</DialogDescription></DialogHeader>
            <div className="space-y-3 py-2">
              <div><Label>User ID</Label><Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="UUID" /></div>
              <div><Label>Qualification</Label><Input value={qualification} onChange={(e) => setQualification(e.target.value)} placeholder="Optional qualification" /></div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={create.isPending || !userId.trim()}>Register</Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{isLoading ? "Loading..." : `${(trainers ?? []).length} trainers`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          {isLoading ? (
            <div className="space-y-2"><Skeleton className="h-12 w-full" /><Skeleton className="h-12 w-full" /></div>
          ) : !trainers || trainers.length === 0 ? (
            <p className="text-sm text-muted-foreground py-4">No trainers registered.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-muted-foreground">
                    <th className="pb-2 pr-4 font-medium">User ID</th>
                    <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Qualification</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {trainers.map((t) => (
                    <tr key={t.id} className="border-b last:border-0 hover:bg-muted/30">
                      <td className="py-3 pr-4 font-mono text-xs">{t.user_id.slice(0, 12)}...</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{t.qualification ?? "—"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${t.is_active ? "bg-green-100 text-green-700" : "bg-slate-100 text-slate-500"}`}>{t.is_active ? "Active" : "Inactive"}</span></td>
                      <td className="py-3 pr-4"><Button variant="outline" size="sm" onClick={() => toggleActive(t)}>{t.is_active ? "Deactivate" : "Activate"}</Button></td>
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
