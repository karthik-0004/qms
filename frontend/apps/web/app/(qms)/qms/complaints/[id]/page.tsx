"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  useComplaint,
  useUpdateComplaint,
  useCloseComplaint,
  useDeleteComplaint,
  useRespondToComplaint,
} from "@/lib/hooks/queries/qms";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@/components/ui/dialog";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import {
  ChevronLeft,
  CheckCircle2,
  Trash2,
  MessageSquare,
  User,
  Package,
  Search,
  FileText,
  ShieldCheck,
  Send,
} from "lucide-react";
import { format } from "date-fns";
import { toast } from "sonner";

// ── Status helpers ────────────────────────────────────────────────────────────

const WORKFLOW_STEPS = ["open", "investigating", "responded", "closed"];

const STATUS_COLOR: Record<string, string> = {
  open: "bg-blue-100 text-blue-700",
  investigating: "bg-yellow-100 text-yellow-700",
  responded: "bg-green-100 text-green-700",
  closed: "bg-gray-100 text-gray-600",
};

const SEVERITY_COLOR: Record<string, string> = {
  critical: "bg-red-100 text-red-700",
  major: "bg-orange-100 text-orange-700",
  minor: "bg-yellow-100 text-yellow-700",
  observation: "bg-blue-100 text-blue-700",
};

// ── Sub-components ────────────────────────────────────────────────────────────

function StepBar({ status }: { status: string }) {
  const idx = WORKFLOW_STEPS.indexOf(status);
  const SHORT: Record<string, string> = { open: "Open", investigating: "Investigating", responded: "Responded", closed: "Closed" };
  return (
    <div className="flex items-center gap-0">
      {WORKFLOW_STEPS.map((s, i) => (
        <div key={s} className="flex items-center">
          <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-semibold border-2 transition-colors ${i < idx ? "bg-green-500 border-green-500 text-white" : i === idx ? "bg-blue-600 border-blue-600 text-white" : "bg-white border-gray-300 text-gray-400"}`}>
            {i < idx ? "✓" : i + 1}
          </div>
          <span className={`ml-1 text-xs font-medium hidden sm:block ${i === idx ? "text-blue-600" : i < idx ? "text-green-600" : "text-gray-400"}`}>
            {SHORT[s]}
          </span>
          {i < WORKFLOW_STEPS.length - 1 && <div className={`w-10 h-0.5 mx-1.5 ${i < idx ? "bg-green-400" : "bg-gray-200"}`} />}
        </div>
      ))}
    </div>
  );
}

function InfoRow({ label, value, onEdit }: { label: string; value: string | null | undefined; onEdit?: (v: string) => void }) {
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(value ?? "");

  if (editing && onEdit) {
    return (
      <div className="flex items-center gap-2 py-2 border-b border-gray-100 last:border-0">
        <span className="text-xs text-gray-500 w-36 shrink-0">{label}</span>
        <Input autoFocus className="h-7 text-sm flex-1" value={draft} onChange={(e) => setDraft(e.target.value)}
          onBlur={() => { onEdit(draft); setEditing(false); }}
          onKeyDown={(e) => { if (e.key === "Enter") { onEdit(draft); setEditing(false); } else if (e.key === "Escape") setEditing(false); }}
        />
      </div>
    );
  }

  return (
    <div className={`flex items-start gap-2 py-2 border-b border-gray-100 last:border-0 ${onEdit ? "cursor-pointer hover:bg-gray-50 rounded px-1 -mx-1" : ""}`} onClick={() => onEdit && setEditing(true)}>
      <span className="text-xs text-gray-500 w-36 shrink-0 pt-0.5">{label}</span>
      <span className="text-sm text-gray-900 flex-1">{value || <span className="text-gray-400 italic">—</span>}</span>
    </div>
  );
}

// ── Tabs ─────────────────────────────────────────────────────────────────────

type Tab = "about" | "details" | "investigation" | "root_cause" | "response" | "resolution" | "escalation";

const TABS: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: "about", label: "About", icon: User },
  { key: "details", label: "Details", icon: Package },
  { key: "investigation", label: "Investigation", icon: Search },
  { key: "root_cause", label: "Root Cause", icon: FileText },
  { key: "response", label: "Response", icon: Send },
  { key: "resolution", label: "Resolution", icon: CheckCircle2 },
  { key: "escalation", label: "CAPA Escalation", icon: ShieldCheck },
];

// ── Page ─────────────────────────────────────────────────────────────────────

export default function ComplaintDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<Tab>("about");
  const [showDelete, setShowDelete] = useState(false);
  const [showRespond, setShowRespond] = useState(false);
  const [responseText, setResponseText] = useState("");

  const { data: complaint, isLoading } = useComplaint(id);
  const updateComplaint = useUpdateComplaint();
  const deleteComplaint = useDeleteComplaint();
  const respondToComplaint = useRespondToComplaint();

  if (isLoading) return <div className="p-6 flex items-center justify-center h-64"><div className="text-gray-400 text-sm">Loading complaint…</div></div>;
  if (!complaint) return <div className="p-6 text-red-500 text-sm">Complaint not found.</div>;

  async function patch(data: Record<string, unknown>) {
    try { await updateComplaint.mutateAsync({ id, data }); }
    catch { toast.error("Failed to save"); }
  }

  async function handleDelete() {
    try {
      await deleteComplaint.mutateAsync(id);
      toast.success("Complaint deleted");
      router.push("/qms/complaints");
    } catch { toast.error("Failed to delete"); }
  }

  async function handleRespond() {
    if (!responseText.trim()) { toast.error("Response text is required"); return; }
    try {
      await respondToComplaint.mutateAsync({ id, response_text: responseText });
      toast.success("Response recorded");
      setShowRespond(false);
    } catch { toast.error("Failed to submit response"); }
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-gray-200 bg-white">
        <div className="flex items-start gap-4">
          <Link href="/qms/complaints">
            <Button variant="ghost" size="sm" className="-ml-2"><ChevronLeft className="w-4 h-4 mr-1" />Complaints</Button>
          </Link>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <h1 className="text-lg font-semibold text-gray-900 truncate">{complaint.complaint_number}</h1>
              <Badge className={`text-xs shrink-0 ${SEVERITY_COLOR[complaint.severity] ?? ""}`}>{complaint.severity}</Badge>
              <Badge className={`text-xs shrink-0 ${STATUS_COLOR[complaint.status] ?? ""}`}>{complaint.status}</Badge>
            </div>
            <p className="text-xs text-gray-500 mt-0.5">{complaint.category ?? "—"} · Received {format(new Date(complaint.received_at), "PPP")}</p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Button size="sm" onClick={() => setShowRespond(true)} className="bg-blue-600 hover:bg-blue-700 text-white">
              <Send className="w-3.5 h-3.5 mr-1.5" />
              Respond
            </Button>
            <Button size="sm" variant="outline" className="text-red-600 border-red-200 hover:bg-red-50" onClick={() => setShowDelete(true)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        </div>
        <div className="mt-4">
          <StepBar status={complaint.status} />
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 bg-white px-6">
        <div className="flex gap-0 overflow-x-auto">
          {TABS.map(({ key, label, icon: Icon }) => (
            <button key={key} onClick={() => setActiveTab(key)}
              className={`flex items-center gap-1.5 px-3 py-3 text-sm font-medium border-b-2 whitespace-nowrap transition-colors ${activeTab === key ? "border-blue-600 text-blue-600" : "border-transparent text-gray-500 hover:text-gray-700"}`}
            >
              <Icon className="w-3.5 h-3.5" />
              {label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-auto p-6">
        {activeTab === "about" && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 max-w-4xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Customer</CardTitle></CardHeader>
              <CardContent>
                <InfoRow label="Customer Name" value={complaint.customer_name} onEdit={(v) => patch({ customer_name: v || null })} />
                <InfoRow label="Received Via" value={complaint.received_via} onEdit={(v) => patch({ received_via: v || "email" })} />
                <InfoRow label="Received At" value={format(new Date(complaint.received_at), "PPP")} />
              </CardContent>
            </Card>
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Classification</CardTitle></CardHeader>
              <CardContent>
                <InfoRow label="Number" value={complaint.complaint_number} />
                <InfoRow label="Severity" value={complaint.severity} onEdit={(v) => patch({ severity: v || "minor" })} />
                <InfoRow label="Category" value={complaint.category} onEdit={(v) => patch({ category: v || null })} />
                <InfoRow label="Status" value={complaint.status} />
                <InfoRow label="Investigator" value={complaint.investigator_id} onEdit={(v) => patch({ investigator_id: v || null })} />
                <InfoRow label="CAPA ID" value={complaint.capa_id} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "details" && (
          <div className="max-w-3xl space-y-6">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Description</CardTitle></CardHeader>
              <CardContent>
                <Textarea rows={6} className="text-sm resize-none" placeholder="Full complaint description…" defaultValue={complaint.description} onBlur={(e) => patch({ description: e.target.value })} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "investigation" && (
          <div className="max-w-3xl space-y-4">
            <p className="text-sm text-gray-500">Use this area to document investigation findings. Update root cause in the Root Cause tab once identified.</p>
            <Card className="border border-gray-200">
              <CardContent className="pt-4">
                <div className="space-y-3">
                  <div className="space-y-1">
                    <Label className="text-xs text-gray-500">Status</Label>
                    <Select value={complaint.status} onValueChange={(v) => patch({ status: v })}>
                      <SelectTrigger className="h-9 text-sm"><SelectValue /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="open">Open</SelectItem>
                        <SelectItem value="investigating">Investigating</SelectItem>
                        <SelectItem value="responded">Responded</SelectItem>
                        <SelectItem value="closed">Closed</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "root_cause" && (
          <div className="max-w-3xl space-y-6">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Root Cause</CardTitle></CardHeader>
              <CardContent>
                <Textarea rows={6} className="text-sm resize-none" placeholder="Document the identified root cause…" defaultValue={complaint.root_cause ?? ""} onBlur={(e) => patch({ root_cause: e.target.value || null })} />
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "response" && (
          <div className="max-w-3xl space-y-6">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Customer Response</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                {complaint.response_text ? (
                  <>
                    <div className="bg-green-50 border border-green-200 rounded p-3">
                      <p className="text-xs text-green-700 font-medium mb-1">Response sent</p>
                      <p className="text-sm text-gray-800">{complaint.response_text}</p>
                    </div>
                    {complaint.response_sent_at && (
                      <p className="text-xs text-gray-500">Sent: {format(new Date(complaint.response_sent_at), "PPP p")}</p>
                    )}
                  </>
                ) : (
                  <div className="text-center py-8 text-gray-400 text-sm">
                    <Send className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p>No response recorded yet</p>
                    <Button variant="outline" size="sm" className="mt-3" onClick={() => setShowRespond(true)}>
                      Record Response
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "resolution" && (
          <div className="max-w-3xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">Resolution Summary</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-500 mb-3">Mark this complaint as resolved once the root cause has been addressed and the customer has been notified.</p>
                <Button size="sm" className="bg-green-600 hover:bg-green-700 text-white" disabled={complaint.status === "closed"} onClick={() => patch({ status: "closed" })}>
                  <CheckCircle2 className="w-3.5 h-3.5 mr-1.5" />
                  {complaint.status === "closed" ? "Closed" : "Mark Closed"}
                </Button>
              </CardContent>
            </Card>
          </div>
        )}

        {activeTab === "escalation" && (
          <div className="max-w-3xl">
            <Card className="border border-gray-200">
              <CardHeader className="pb-3"><CardTitle className="text-sm font-semibold">CAPA Escalation</CardTitle></CardHeader>
              <CardContent>
                {complaint.capa_id ? (
                  <div className="bg-purple-50 border border-purple-200 rounded p-3">
                    <p className="text-xs text-purple-700 font-medium">Escalated to CAPA</p>
                    <Link href={`/qms/capa/${complaint.capa_id}`} className="text-sm text-blue-600 hover:underline">
                      View CAPA {complaint.capa_id}
                    </Link>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-400 text-sm">
                    <ShieldCheck className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                    <p>Not escalated to CAPA</p>
                    <p className="text-xs mt-1">If this complaint requires systemic corrective action, escalate to CAPA</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        )}
      </div>

      {/* Respond Dialog */}
      <Dialog open={showRespond} onOpenChange={setShowRespond}>
        <DialogContent className="max-w-md">
          <DialogHeader><DialogTitle>Record Customer Response</DialogTitle></DialogHeader>
          <div className="space-y-3 py-2">
            <p className="text-sm text-gray-600">Document the response sent to the customer regarding this complaint.</p>
            <Textarea rows={4} className="text-sm resize-none" placeholder="Response text…" value={responseText} onChange={(e) => setResponseText(e.target.value)} />
          </div>
          <DialogFooter>
            <Button variant="outline" size="sm" onClick={() => setShowRespond(false)}>Cancel</Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" disabled={respondToComplaint.isPending} onClick={handleRespond}>
              {respondToComplaint.isPending ? "Saving…" : "Record Response"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirm */}
      <AlertDialog open={showDelete} onOpenChange={setShowDelete}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete Complaint?</AlertDialogTitle>
            <AlertDialogDescription>This will permanently delete <strong>{complaint.complaint_number}</strong>. This cannot be undone.</AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction className="bg-red-600 hover:bg-red-700" onClick={handleDelete}>Delete</AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
