"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useManagementReview, useUpdateManagementReview, useCompleteManagementReview } from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { ChevronLeft, CheckCircle2, ClipboardList, FileText, Users } from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

const STATUS_COLOR: Record<string, string> = {
  scheduled: "bg-blue-100 text-blue-700",
  in_progress: "bg-yellow-100 text-yellow-700",
  completed: "bg-green-100 text-green-700",
  cancelled: "bg-gray-100 text-gray-500",
};

type Tab = "overview" | "minutes" | "outcomes" | "actions";

const TABS = [
  { key: "overview" as Tab, label: "Overview", icon: FileText },
  { key: "minutes" as Tab, label: "Minutes", icon: ClipboardList },
  { key: "outcomes" as Tab, label: "Outcomes", icon: CheckCircle2 },
  { key: "actions" as Tab, label: "Action Items", icon: Users },
];

export default function ManagementReviewDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>("overview");

  const { data: review, isLoading } = useManagementReview(id);
  const updateReview = useUpdateManagementReview();
  const completeReview = useCompleteManagementReview();

  if (isLoading) return <div className="p-6 flex items-center justify-center h-64"><div className="text-gray-400 text-sm">Loading…</div></div>;
  if (!review) return <div className="p-6 text-red-500">Review not found.</div>;

  async function patch(data: Record<string, unknown>) {
    try { await updateReview.mutateAsync({ id, data }); }
    catch { toast.error("Failed to save"); }
  }

  async function handleComplete() {
    try {
      await completeReview.mutateAsync(id);
      toast.success("Review marked as completed");
    } catch { toast.error("Failed to complete review"); }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-gray-200 bg-white">
        <div className="flex items-start gap-4">
          <Link href="/qms/management-reviews">
            <Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />Reviews</Button>
          </Link>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-lg font-semibold text-gray-900 truncate">{review.title}</h1>
              <Badge className={`text-xs shrink-0 ${STATUS_COLOR[review.status] ?? "bg-gray-100 text-gray-600"}`}>{review.status}</Badge>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{review.review_number} · Scheduled {format(new Date(review.scheduled_date), "PPP")}</p>
          </div>
          {review.status !== "completed" && (
            <Button size="sm" onClick={handleComplete} disabled={completeReview.isPending} className="bg-green-600 hover:bg-green-700 text-white shrink-0">
              <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
              {completeReview.isPending ? "Completing…" : "Mark Complete"}
            </Button>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white px-6">
        <div className="flex">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button key={key} onClick={() => setActiveTab(key)}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors ${activeTab === key ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
            >
              <Icon className="w-4 h-4" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === "overview" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Review Info</CardTitle></CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-2 py-1.5 border-b border-gray-100">
                  <span className="text-xs text-gray-500 w-36 shrink-0">Number</span>
                  <span className="text-sm">{review.review_number}</span>
                </div>
                <div className="flex items-start gap-2 py-1.5 border-b border-gray-100">
                  <span className="text-xs text-gray-500 w-36 shrink-0">Scheduled</span>
                  <span className="text-sm">{format(new Date(review.scheduled_date), "PPP")}</span>
                </div>
                <div className="flex items-start gap-2 py-1.5 border-b border-gray-100">
                  <span className="text-xs text-gray-500 w-36 shrink-0">Completed</span>
                  <span className="text-sm">{review.completed_date ? format(new Date(review.completed_date), "PPP") : "—"}</span>
                </div>
                <div className="flex items-start gap-2 py-1.5 border-b border-gray-100">
                  <span className="text-xs text-gray-500 w-36 shrink-0">Facilitator</span>
                  <span className="text-sm">{review.facilitator_id ?? "—"}</span>
                </div>
                <div className="flex items-start gap-2 py-1.5">
                  <span className="text-xs text-gray-500 w-36 shrink-0">Next Review</span>
                  <span className="text-sm">{review.next_review_date ? format(new Date(review.next_review_date), "PPP") : "—"}</span>
                </div>
              </CardContent>
            </Card>
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Agenda</CardTitle></CardHeader>
              <CardContent>
                <Textarea rows={8} className="text-sm resize-none" placeholder="Meeting agenda…" defaultValue={review.agenda ?? ""} onBlur={(e) => patch({ agenda: e.target.value || null })} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "minutes" && (
          <div className="max-w-3xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Meeting Minutes</CardTitle></CardHeader>
              <CardContent>
                <Textarea rows={12} className="text-sm resize-none" placeholder="Record the meeting minutes here…" defaultValue={review.minutes ?? ""} onBlur={(e) => patch({ minutes: e.target.value || null })} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "outcomes" && (
          <div className="max-w-3xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Review Outcomes</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-3">Document the key outcomes, decisions, and conclusions from this management review.</p>
                <Textarea rows={8} className="text-sm resize-none" placeholder="Key outcomes and decisions…" defaultValue={Array.isArray(review.outcomes) ? review.outcomes.join("\n") : ""} onBlur={(e) => patch({ outcomes: e.target.value ? e.target.value.split("\n") : [] })} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "actions" && (
          <div className="max-w-3xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Action Items</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-3">Track follow-up actions assigned during the management review.</p>
                <Textarea rows={8} className="text-sm resize-none" placeholder="Action items (one per line)…" defaultValue={Array.isArray(review.action_items) ? review.action_items.join("\n") : ""} onBlur={(e) => patch({ action_items: e.target.value ? e.target.value.split("\n") : [] })} />
                <div className="mt-4 space-y-2">
                  <Label className="text-xs text-gray-500">Next Review Date</Label>
                  <Input type="date" className="h-9 text-sm max-w-xs" defaultValue={review.next_review_date ? review.next_review_date.slice(0, 10) : ""} onBlur={(e) => patch({ next_review_date: e.target.value ? new Date(e.target.value).toISOString() : null })} />
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
