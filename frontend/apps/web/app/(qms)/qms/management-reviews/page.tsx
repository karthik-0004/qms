"use client";

import { useState } from "react";
import Link from "next/link";
import { useManagementReviews, useCreateManagementReview } from "@/lib/hooks/queries/qms";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import { ClipboardSignature, Plus } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

const STATUS_COLOR: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-gray-100 text-gray-500",
};

export default function ManagementReviewsPage() {
  const { data: page, isLoading } = useManagementReviews({ page: 1, page_size: 50 });
  const createReview = useCreateManagementReview();
  const [showCreate, setShowCreate] = useState(false);

  const reviews = page?.items ?? [];

  const [form, setForm] = useState({
    review_number: `MR-${new Date().getFullYear()}-${String(Date.now()).slice(-4)}`,
    title: "",
    scheduled_date: "",
    agenda: "",
  });

  async function handleCreate() {
    if (!form.title.trim() || !form.scheduled_date) { toast.error("Title and scheduled date are required"); return; }
    try {
      const created = await createReview.mutateAsync({
        review_number: form.review_number,
        title: form.title,
        scheduled_date: new Date(form.scheduled_date).toISOString(),
        agenda: form.agenda || null,
      });
      toast.success("Management Review created");
      setShowCreate(false);
      window.location.href = `/qms/management-reviews/${created.id}`;
    } catch { toast.error("Failed to create review"); }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-gray-900">Management Reviews</h1>
          <p className="text-sm text-gray-500 mt-1">Schedule and document management review meetings</p>
        </div>
        <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => setShowCreate(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Schedule Review
        </Button>
      </div>

      {/* Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Review #</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Title</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Status</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Scheduled Date</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Completed</th>
              <th className="text-left px-4 py-3 font-medium text-gray-600">Next Review</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {isLoading ? (
              <tr><td colSpan={6} className="px-4 py-10 text-center text-gray-400">Loading…</td></tr>
            ) : reviews.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-12 text-center">
                  <ClipboardSignature className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                  <p className="text-gray-400 text-sm">No management reviews yet</p>
                </td>
              </tr>
            ) : reviews.map((r) => (
              <tr key={r.id} className="hover:bg-gray-50">
                <td className="px-4 py-3">
                  <Link href={`/qms/management-reviews/${r.id}`} className="text-blue-600 hover:underline font-medium">{r.review_number}</Link>
                </td>
                <td className="px-4 py-3">
                  <Link href={`/qms/management-reviews/${r.id}`} className="text-gray-900 hover:text-blue-600">{r.title}</Link>
                </td>
                <td className="px-4 py-3">
                  <Badge className={`text-xs ${STATUS_COLOR[r.status] ?? "bg-gray-100 text-gray-600"}`}>{r.status}</Badge>
                </td>
                <td className="px-4 py-3 text-gray-600">{format(new Date(r.scheduled_date), "MMM d, yyyy")}</td>
                <td className="px-4 py-3 text-gray-500">{r.completed_date ? format(new Date(r.completed_date), "MMM d, yyyy") : "—"}</td>
                <td className="px-4 py-3 text-gray-500">{r.next_review_date ? format(new Date(r.next_review_date), "MMM d, yyyy") : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <Dialog open={showCreate} onOpenChange={setShowCreate}>
        <DialogContent className="max-w-lg">
          <DialogHeader><DialogTitle>Schedule Management Review</DialogTitle></DialogHeader>
          <div className="space-y-4 py-2">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1">
                <Label className="text-xs">Review Number</Label>
                <Input className="h-9 text-sm" value={form.review_number} onChange={(e) => setForm((f) => ({ ...f, review_number: e.target.value }))} />
              </div>
              <div className="space-y-1">
                <Label className="text-xs">Scheduled Date *</Label>
                <Input type="date" className="h-9 text-sm" value={form.scheduled_date} onChange={(e) => setForm((f) => ({ ...f, scheduled_date: e.target.value }))} />
              </div>
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Title *</Label>
              <Input className="h-9 text-sm" placeholder="e.g. Q2 2026 Management Review" value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label className="text-xs">Agenda</Label>
              <Textarea className="text-sm resize-none" rows={4} placeholder="Meeting agenda items…" value={form.agenda} onChange={(e) => setForm((f) => ({ ...f, agenda: e.target.value }))} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowCreate(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={createReview.isPending} onClick={handleCreate}>
              {createReview.isPending ? "Creating…" : "Schedule Review"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
