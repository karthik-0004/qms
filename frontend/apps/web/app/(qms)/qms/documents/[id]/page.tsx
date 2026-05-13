"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Route } from "next";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, FileText, Home, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  useAddDistributionMember,
  useApproveDocument,
  useDocument,
  useDocumentDistribution,
  useDocumentVersions,
  useMakeDocumentObsolete,
  useRejectDocument,
} from "@/lib/hooks/queries/qms";
import { usePermission } from "@/lib/hooks/usePermission";
import { handleApiError } from "@/lib/api/client";
import { documentsApi, trainingApi } from "@/lib/api/services/qms";
import { toast } from "sonner";

type Tab = "overview" | "versions" | "distribution";

export default function DocumentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const id = String(params.id ?? "");
  const { hasPermission } = usePermission();
  const canWrite = hasPermission("document:write");
  const canApprove = hasPermission("document:approve");
  const canAssignTraining = hasPermission("training:assign");

  const [tab, setTab] = useState<Tab>("overview");
  const [rejectOpen, setRejectOpen] = useState(false);
  const [rejectReason, setRejectReason] = useState("");
  const [approveOpen, setApproveOpen] = useState(false);
  const [signature, setSignature] = useState("");
  const [reviewDate, setReviewDate] = useState("");
  const [obsoleteOpen, setObsoleteOpen] = useState(false);
  const [newDistUser, setNewDistUser] = useState("");

  const { data: doc, isLoading, isError, error, refetch } = useDocument(id);
  const { data: versions = [], isLoading: vLoading } = useDocumentVersions(id);
  const { data: distribution = [], isLoading: dLoading, refetch: refetchDist } = useDocumentDistribution(id);

  const rejectMut = useRejectDocument();
  const approveMut = useApproveDocument();
  const obsoleteMut = useMakeDocumentObsolete();
  const addDistMut = useAddDistributionMember();

  const statusLabel = useMemo(() => doc?.status?.replace(/_/g, " ") ?? "", [doc?.status]);

  if (!id) {
    return <p className="p-6 text-muted-foreground">Invalid document.</p>;
  }

  if (isError) {
    return (
      <div className="p-6 space-y-4">
        <p className="text-destructive text-sm">{handleApiError(error)}</p>
        <Button variant="outline" onClick={() => router.push("/qms/documents" as Route)}>
          Back to documents
        </Button>
      </div>
    );
  }

  if (isLoading || !doc) {
    return (
      <div className="flex items-center justify-center min-h-[40vh] gap-2 text-muted-foreground">
        <Loader2 className="h-5 w-5 animate-spin" />
        Loading document…
      </div>
    );
  }

  const onReject = () => {
    if (!rejectReason.trim()) {
      toast.error("Please enter a rejection reason.");
      return;
    }
    rejectMut.mutate(
      { id, reason: rejectReason.trim() },
      {
        onSuccess: () => {
          toast.success("Document rejected and returned to draft.");
          setRejectOpen(false);
          setRejectReason("");
          void refetch();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onApprove = () => {
    if (!signature.trim()) {
      toast.error("E-signature is required.");
      return;
    }
    approveMut.mutate(
      {
        id,
        data: {
          signature: signature.trim(),
          review_date: reviewDate ? new Date(reviewDate).toISOString() : undefined,
        },
      },
      {
        onSuccess: async () => {
          toast.success("Document approved.");
          setApproveOpen(false);
          setSignature("");
          setReviewDate("");
          void refetch();
          if (canAssignTraining) {
            try {
              const dist = await documentsApi.listDistribution(id);
              const userIds = [...new Set(dist.map((d) => d.user_id).filter(Boolean))];
              const coursesRes = await trainingApi.list({ page: 1, page_size: 200 });
              const linked = coursesRes.items.filter((c) => c.document_id === id);
              let assigned = 0;
              for (const course of linked) {
                for (const user_id of userIds) {
                  try {
                    await trainingApi.assign(course.id, { user_id });
                    assigned += 1;
                  } catch {
                    /* duplicate assignment or server rule */
                  }
                }
              }
              if (linked.length && userIds.length) {
                if (assigned > 0) {
                  toast.success(`Training bulk assign: ${assigned} assignment(s) created.`);
                } else {
                  toast("No new training assignments (courses linked to this document, or assignees already assigned).");
                }
              }
            } catch (e) {
              toast.error(handleApiError(e));
            }
          }
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  const onObsolete = () => {
    obsoleteMut.mutate(id, {
      onSuccess: () => {
        toast.success("Document marked obsolete.");
        setObsoleteOpen(false);
        void refetch();
      },
      onError: (e) => toast.error(handleApiError(e)),
    });
  };

  const onAddDistribution = () => {
    if (!newDistUser.trim()) {
      toast.error("Enter a user UUID for the recipient.");
      return;
    }
    addDistMut.mutate(
      { id, user_id: newDistUser.trim() },
      {
        onSuccess: () => {
          toast.success("Recipient added to distribution list.");
          setNewDistUser("");
          void refetchDist();
        },
        onError: (e) => toast.error(handleApiError(e)),
      },
    );
  };

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div className="flex items-center gap-2 text-sm">
        <Button variant="ghost" size="sm" onClick={() => router.push("/dashboard")} className="h-7 px-2">
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button variant="ghost" size="sm" onClick={() => router.push("/qms/documents" as Route)} className="h-7 px-2">
          <Home className="h-4 w-4 mr-1" />
          Documents
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="font-medium truncate">{doc.doc_number}</span>
      </div>

      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6 shrink-0" />
            <span className="break-words">{doc.title}</span>
          </h1>
          <p className="text-muted-foreground text-sm mt-1 font-mono">{doc.doc_number}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          {doc.status === "under_review" && canApprove && (
            <>
              <Button size="sm" variant="outline" onClick={() => setRejectOpen(true)}>
                Reject
              </Button>
              <Button size="sm" onClick={() => setApproveOpen(true)}>
                Approve
              </Button>
            </>
          )}
          {doc.status === "approved" && canApprove && (
            <Button size="sm" variant="destructive" onClick={() => setObsoleteOpen(true)}>
              Make obsolete
            </Button>
          )}
        </div>
      </div>

      <div className="flex flex-wrap gap-2 border-b pb-2">
        {(["overview", "versions", "distribution"] as const).map((t) => (
          <Button
            key={t}
            variant={tab === t ? "secondary" : "ghost"}
            size="sm"
            className="min-h-9 capitalize"
            onClick={() => setTab(t)}
          >
            {t}
          </Button>
        ))}
      </div>

      {tab === "overview" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Overview</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 text-sm">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <p className="text-muted-foreground">Status</p>
                <p className="font-medium capitalize">{statusLabel}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Version</p>
                <p className="font-medium">v{doc.current_version}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Approver (single)</p>
                <p className="font-mono text-xs break-all">{doc.approver_id ?? "—"}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Owner</p>
                <p className="font-mono text-xs break-all">{doc.owner_id ?? "—"}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Review date</p>
                <p className="font-medium">
                  {doc.review_date ? new Date(doc.review_date).toLocaleString() : "—"}
                </p>
              </div>
              <div>
                <p className="text-muted-foreground">Effective date</p>
                <p className="font-medium">
                  {doc.effective_date ? new Date(doc.effective_date).toLocaleString() : "—"}
                </p>
              </div>
            </div>
            {doc.last_rejection_reason && (
              <div className="rounded-md border border-amber-200 bg-amber-50/80 dark:bg-amber-950/30 p-3">
                <p className="text-xs font-medium text-amber-900 dark:text-amber-200">Last rejection reason</p>
                <p className="text-sm mt-1 whitespace-pre-wrap">{doc.last_rejection_reason}</p>
              </div>
            )}
            {doc.description && (
              <div>
                <p className="text-muted-foreground">Description</p>
                <p className="mt-1 whitespace-pre-wrap">{doc.description}</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "versions" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Version history</CardTitle>
          </CardHeader>
          <CardContent>
            {vLoading ? (
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading…
              </p>
            ) : versions.length === 0 ? (
              <p className="text-sm text-muted-foreground">No versions recorded.</p>
            ) : (
              <ul className="space-y-2">
                {versions.map((v) => (
                  <li key={v.id} className="rounded-md border border-border p-3 text-sm">
                    <div className="font-medium">v{v.version}</div>
                    <div className="text-muted-foreground text-xs mt-1">
                      {v.change_summary ?? "—"} · {new Date(v.created_at).toLocaleString()}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      {tab === "distribution" && (
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Distribution list</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {canWrite && (
              <div className="flex flex-col sm:flex-row gap-2 sm:items-end">
                <div className="flex-1 space-y-1">
                  <Label htmlFor="dist-user">User ID (UUID)</Label>
                  <Input
                    id="dist-user"
                    value={newDistUser}
                    onChange={(e) => setNewDistUser(e.target.value)}
                    placeholder="Recipient user UUID"
                    className="font-mono text-xs"
                  />
                </div>
                <Button
                  type="button"
                  className="min-h-9"
                  onClick={onAddDistribution}
                  disabled={addDistMut.isPending}
                >
                  {addDistMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Add recipient"}
                </Button>
              </div>
            )}
            {dLoading ? (
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin" /> Loading…
              </p>
            ) : distribution.length === 0 ? (
              <p className="text-sm text-muted-foreground">No distribution recipients yet.</p>
            ) : (
              <ul className="space-y-2">
                {distribution.map((row) => (
                  <li key={row.id} className="rounded-md border border-border p-2 text-sm font-mono text-xs">
                    User {row.user_id} · added {new Date(row.created_at).toLocaleString()}
                  </li>
                ))}
              </ul>
            )}
          </CardContent>
        </Card>
      )}

      <Dialog open={rejectOpen} onOpenChange={setRejectOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject document</DialogTitle>
            <DialogDescription>Returns the document to draft. A reason is required for the audit trail.</DialogDescription>
          </DialogHeader>
          <div className="space-y-2 py-2">
            <Label htmlFor="rej-reason">Reason</Label>
            <Textarea
              id="rej-reason"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              rows={4}
              placeholder="Explain why this revision cannot be approved…"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={onReject} disabled={rejectMut.isPending}>
              {rejectMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Reject"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={approveOpen} onOpenChange={setApproveOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Approve document</DialogTitle>
            <DialogDescription>Provide your e-signature and optional next review date.</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-2">
            <div className="space-y-1">
              <Label htmlFor="sig">E-signature</Label>
              <Input id="sig" value={signature} onChange={(e) => setSignature(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="rev-d">Next review date (optional)</Label>
              <Input id="rev-d" type="datetime-local" value={reviewDate} onChange={(e) => setReviewDate(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setApproveOpen(false)}>
              Cancel
            </Button>
            <Button onClick={onApprove} disabled={approveMut.isPending}>
              {approveMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Approve"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={obsoleteOpen} onOpenChange={setObsoleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Make document obsolete</DialogTitle>
            <DialogDescription>This can only be done for approved documents. The document will no longer be active.</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setObsoleteOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={onObsolete} disabled={obsoleteMut.isPending}>
              {obsoleteMut.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : "Confirm"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
