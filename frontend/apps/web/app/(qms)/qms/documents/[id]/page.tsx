"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowLeft, FileText, Clock, Users, CheckCircle, Copy,
  AlertTriangle, ThumbsUp, ThumbsDown, Trash2, Eye, Download,
  History, FileUp, Activity,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Skeleton } from "@/components/ui/skeleton";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { useDocument, useDocumentVersions, useApproveDocument, useRejectDocument, useMakeDocumentEffective, useMakeDocumentSuperseded, useMakeDocumentObsolete, useDocumentDistribution, useAddDistributionMember } from "@/lib/hooks/queries/qms";
import { documentsApi } from "@/lib/api/services/qms";
import { auditApi } from "@/lib/api/services/platform";
import type { Document, DocumentVersion, DocumentDistribution, ControlledCopy } from "@/lib/api/services/qms";
import type { AuditEntry } from "@/lib/api/services/platform";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { handleApiError } from "@/lib/api/client";
import { toast } from "sonner";
import { EventTimeline } from "@/components/qms-shared/EventTimeline";
import { StatusBadge } from "@/components/qms-shared/StatusBadge";
import { SignatureDialog } from "@/components/qms-shared/SignatureDialog";
import { cn } from "@/lib/utils";

const DETAIL_LABELS: Record<string, { label: string; icon?: React.ReactNode }> = {
  doc_number: { label: "Document Number", icon: <FileText className="h-4 w-4" /> },
  doc_type: { label: "Type" },
  department: { label: "Department" },
  status: { label: "Status" },
  current_version: { label: "Version", icon: <Clock className="h-4 w-4" /> },
  owner_id: { label: "Owner" },
  approver_id: { label: "Approver" },
  created_by: { label: "Created By" },
  effective_date: { label: "Effective Date" },
  review_date: { label: "Review Date" },
  expiry_date: { label: "Expiry Date" },
  last_rejection_reason: { label: "Last Rejection Reason" },
  is_controlled: { label: "Controlled" },
  authoring_mode: { label: "Authoring Mode" },
  review_interval_days: { label: "Review Interval (days)" },
  next_review_date: { label: "Next Review" },
  obsolete_reason: { label: "Obsolete Reason" },
  tags: { label: "Tags" },
  regulatory_frameworks: { label: "Regulatory Frameworks" },
};

type ActionType = "approve" | "reject" | "acknowledge" | "make-effective" | "make-superseded" | "make-obsolete";

export default function DocumentDetailPage({ params }: { params: { id: string } }) {
  const router = useRouter();
  const qc = useQueryClient();
  const documentId = params.id;

  const { data: doc, isLoading, error } = useDocument(documentId);
  const { data: versions } = useDocumentVersions(documentId);
  const { data: distribution } = useDocumentDistribution(documentId);

  const approveDoc = useApproveDocument();
  const rejectDoc = useRejectDocument();
  const makeEffective = useMakeDocumentEffective();
  const makeSuperseded = useMakeDocumentSuperseded();
  const makeObsolete = useMakeDocumentObsolete();

  const [activeTab, setActiveTab] = useState("overview");
  const [signatureDialog, setSignatureDialog] = useState<{ open: boolean; action: ActionType }>({ open: false, action: "approve" });
  const [rejectReason, setRejectReason] = useState("");
  const [rejectDialogOpen, setRejectDialogOpen] = useState(false);
  const [obsoleteDialogOpen, setObsoleteDialogOpen] = useState(false);
  const [newMemberId, setNewMemberId] = useState("");

  const addMember = useAddDistributionMember();

  // Audit trail for History tab
  const { data: auditData } = useQuery({
    queryKey: ["audit", "document", documentId],
    queryFn: () => auditApi.list({ resource_id: documentId, page_size: 100 }),
    enabled: !!documentId,
  });

  // Controlled copies
  const { data: controlledCopies } = useQuery({
    queryKey: ["controlled-copies", documentId],
    queryFn: () => documentsApi.listControlledCopies(documentId),
    enabled: !!documentId,
  });

  // Initiate revision
  const initiateRevision = useMutation({
    mutationFn: () =>
      documentsApi.createVersion(documentId, { change_type: "major", change_summary: "Initiated revision" }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["documents", documentId] });
      qc.invalidateQueries({ queryKey: ["documents", documentId, "versions"] });
      toast.success("Revision initiated");
    },
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 p-6">
        <Skeleton className="h-8 w-64 mb-4" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  if (error || !doc) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="mx-auto h-10 w-10 text-red-400 mb-3" />
          <p className="text-gray-600 dark:text-gray-400">Document not found</p>
          <Button variant="outline" className="mt-4" onClick={() => router.push("/qms/documents")}>
            Back to Documents
          </Button>
        </div>
      </div>
    );
  }

  const auditEvents = auditData?.items ?? [];
  const ccList: ControlledCopy[] = controlledCopies ?? [];
  const distList: DocumentDistribution[] = distribution ?? [];

  const handleSignatureSubmit = async (action: ActionType, signature: string) => {
    try {
      if (action === "approve") {
        await approveDoc.mutateAsync({ id: documentId, data: { signature } });
        toast.success("Document approved");
      } else if (action === "acknowledge") {
        await documentsApi.acknowledge(documentId, { signature });
        toast.success("Document acknowledged");
        qc.invalidateQueries({ queryKey: ["documents", documentId] });
      } else if (action === "make-effective") {
        await makeEffective.mutateAsync(documentId);
        toast.success("Document released as effective");
      } else if (action === "make-superseded") {
        await makeSuperseded.mutateAsync(documentId);
        toast.success("Document marked superseded");
      }
      setSignatureDialog({ open: false, action: "approve" });
    } catch (err) {
      handleApiError(err, `Failed to ${action}`);
    }
  };

  const handleReject = async () => {
    try {
      await rejectDoc.mutateAsync({ id: documentId, reason: rejectReason });
      toast.success("Document rejected");
      setRejectDialogOpen(false);
      setRejectReason("");
    } catch (err) {
      handleApiError(err, "Failed to reject document");
    }
  };

  const handleMakeObsolete = async () => {
    try {
      await makeObsolete.mutateAsync(documentId);
      toast.success("Document marked obsolete");
      setObsoleteDialogOpen(false);
    } catch (err) {
      handleApiError(err, "Failed to mark obsolete");
    }
  };

  const handleAddMember = async () => {
    if (!newMemberId) return;
    try {
      await addMember.mutateAsync({ id: documentId, user_id: newMemberId });
      setNewMemberId("");
      toast.success("Distribution member added");
    } catch (err) {
      handleApiError(err, "Failed to add member");
    }
  };

  const canApprove = doc.status === "under_review";
  const canReject = doc.status === "under_review";
  const canMakeEffective = doc.status === "approved";
  const canMakeSuperseded = doc.status === "effective";
  const canMakeObsolete = ["approved", "effective", "superseded"].includes(doc.status);
  const canInitiateRevision = ["approved", "effective"].includes(doc.status);
  const canAcknowledge = ["effective", "approved"].includes(doc.status);

  const infoCardFields = useMemo(() => [
    { label: "Document Number", value: doc.doc_number, icon: "FileText" },
    { label: "Type", value: doc.doc_type },
    { label: "Department", value: doc.department },
    { label: "Vault", value: doc.vault || "qa_draft" },
    { label: "Status", value: doc.status, badge: true },
    { label: "Version", value: `v${doc.current_version}` },
    { label: "Owner", value: doc.owner_id },
    { label: "Approver", value: doc.approver_id },
    { label: "Created By", value: doc.created_by },
    { label: "Effective Date", value: doc.effective_date ? new Date(doc.effective_date).toLocaleDateString() : "-" },
    { label: "Review Date", value: doc.review_date ? new Date(doc.review_date).toLocaleDateString() : "-" },
    { label: "Expiry Date", value: doc.expiry_date ? new Date(doc.expiry_date).toLocaleDateString() : "-" },
    { label: "Authoring Mode", value: doc.authoring_mode },
    { label: "Review Interval", value: doc.review_interval_days ? `${doc.review_interval_days} days` : "-" },
    { label: "Next Review", value: doc.next_review_date ? new Date(doc.next_review_date).toLocaleDateString() : "-" },
    { label: "Category Path", value: doc.category_path || "-" },
    { label: "Controlled", value: doc.is_controlled ? "Yes" : "No" },
    { label: "Obsolete Reason", value: doc.obsolete_reason || "-" },
    { label: "Last Rejection", value: doc.last_rejection_reason || "-" },
    { label: "Tags", value: doc.tags?.length ? doc.tags.join(", ") : "-" },
    { label: "Regulatory Frameworks", value: doc.regulatory_frameworks?.length ? doc.regulatory_frameworks.join(", ") : "-" },
    { label: "Description", value: doc.description || "-" },
  ], [doc]);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <div className="mb-4 flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
          <Button variant="ghost" size="sm" className="h-7 px-2" onClick={() => router.push("/qms/documents")}>
            <ArrowLeft className="mr-1 h-4 w-4" />
            Documents
          </Button>
          <span>/</span>
          <span className="font-mono text-gray-700 dark:text-gray-300">{doc.doc_number}</span>
        </div>

        {/* Title + actions */}
        <div className="mb-6 flex flex-wrap items-start justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="rounded-lg bg-blue-100 p-2 dark:bg-blue-900/50">
              <FileText className="h-6 w-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-gray-100">{doc.title}</h1>
              <div className="mt-1 flex items-center gap-3 text-sm text-gray-500 dark:text-gray-400">
                <span className="font-mono">{doc.doc_number}</span>
                <StatusBadge status={doc.status} />
              </div>
            </div>
          </div>

          {/* Action buttons */}
          <div className="flex flex-wrap gap-2">
            {canApprove && (
              <>
                <Button variant="default" onClick={() => setSignatureDialog({ open: true, action: "approve" })}>
                  <ThumbsUp className="mr-1.5 h-4 w-4" />
                  Approve
                </Button>
                <Button variant="destructive" onClick={() => setRejectDialogOpen(true)}>
                  <ThumbsDown className="mr-1.5 h-4 w-4" />
                  Reject
                </Button>
              </>
            )}
            {canMakeEffective && (
              <Button onClick={() => setSignatureDialog({ open: true, action: "make-effective" })}>
                <CheckCircle className="mr-1.5 h-4 w-4" />
                Make Effective
              </Button>
            )}
            {canMakeSuperseded && (
              <Button variant="secondary" onClick={() => setSignatureDialog({ open: true, action: "make-superseded" })}>
                <Copy className="mr-1.5 h-4 w-4" />
                Make Superseded
              </Button>
            )}
            {canMakeObsolete && (
              <Button variant="outline" onClick={() => setObsoleteDialogOpen(true)}>
                <Trash2 className="mr-1.5 h-4 w-4" />
                Make Obsolete
              </Button>
            )}
            {canAcknowledge && (
              <Button variant="outline" onClick={() => setSignatureDialog({ open: true, action: "acknowledge" })}>
                <CheckCircle className="mr-1.5 h-4 w-4" />
                Acknowledge
              </Button>
            )}
            {canInitiateRevision && (
              <Button
                variant="default"
                onClick={() => initiateRevision.mutate()}
                disabled={initiateRevision.isPending}
              >
                <FileUp className="mr-1.5 h-4 w-4" />
                New Revision
              </Button>
            )}
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="mb-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="content">Content</TabsTrigger>
            <TabsTrigger value="versions">Versions</TabsTrigger>
            <TabsTrigger value="distribution">Distribution</TabsTrigger>
            <TabsTrigger value="acknowledgments">Acknowledgments</TabsTrigger>
            <TabsTrigger value="controlled-copies">Controlled Copies</TabsTrigger>
            <TabsTrigger value="history">History</TabsTrigger>
            <TabsTrigger value="details">Details</TabsTrigger>
          </TabsList>

          <TabsContent value="overview">
            <Card>
              <CardHeader><CardTitle className="text-lg">Overview</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {infoCardFields.slice(0, 12).map((f) => (
                    <div key={f.label}>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{f.label}</p>
                      <p className="mt-0.5 text-sm text-gray-900 dark:text-gray-100">
                        {f.badge ? <StatusBadge status={f.value} /> : f.value || "-"}
                      </p>
                    </div>
                  ))}
                </div>
                <Separator />
                <div>
                  <p className="text-xs font-medium text-gray-500 dark:text-gray-400">Description</p>
                  <p className="mt-0.5 text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap">
                    {doc.description || "No description"}
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="content">
            <Card>
              <CardHeader><CardTitle className="text-lg">Content</CardTitle></CardHeader>
              <CardContent>
                {doc.authoring_mode === "editor" && doc.html_snapshot ? (
                  <div
                    className="prose prose-sm dark:prose-invert max-w-none"
                    dangerouslySetInnerHTML={{ __html: doc.html_snapshot }}
                  />
                ) : doc.file_id ? (
                  <div className="flex flex-col items-center gap-4 py-8">
                    <FileText className="h-12 w-12 text-gray-300 dark:text-gray-600" />
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      File stored with ID: {doc.file_id}
                    </p>
                    <Button variant="outline" asChild>
                      <a href={`/api/files/${doc.file_id}`} target="_blank" rel="noopener noreferrer">
                        <Download className="mr-1.5 h-4 w-4" />
                        Download File
                      </a>
                    </Button>
                  </div>
                ) : (
                  <p className="text-sm text-gray-400 dark:text-gray-500">No content available</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="versions">
            <Card>
              <CardHeader><CardTitle className="text-lg">Version History</CardTitle></CardHeader>
              <CardContent>
                {versions && versions.length > 0 ? (
                  <div className="space-y-4">
                    {versions.map((v: DocumentVersion) => (
                      <div
                        key={v.id}
                        className="flex items-start justify-between rounded-lg border p-4 dark:border-gray-700"
                      >
                        <div>
                          <p className="font-medium text-gray-900 dark:text-gray-100">
                            v{v.version}
                          </p>
                          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                            {v.change_summary || "No change summary"}
                          </p>
                          {v.approved_by && (
                            <p className="mt-1 text-xs text-gray-400">
                              Approved by {v.approved_by} on {v.approved_at ? new Date(v.approved_at).toLocaleDateString() : "-"}
                            </p>
                          )}
                        </div>
                        <p className="text-xs text-gray-400">
                          {new Date(v.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">No version history</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="distribution">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Distribution List</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="mb-4 flex items-center gap-2">
                  <Input
                    placeholder="User ID to add..."
                    value={newMemberId}
                    onChange={(e) => setNewMemberId(e.target.value)}
                    className="max-w-xs"
                  />
                  <Button size="sm" onClick={handleAddMember} disabled={!newMemberId}>
                    Add
                  </Button>
                </div>
                {distList.length > 0 ? (
                  <div className="space-y-2">
                    {distList.map((m: DocumentDistribution) => (
                      <div
                        key={m.id}
                        className="flex items-center justify-between rounded border px-3 py-2 text-sm dark:border-gray-700"
                      >
                        <span className="font-mono text-gray-700 dark:text-gray-300">{m.user_id}</span>
                        <span className="text-xs text-gray-400">
                          Added {new Date(m.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">No distribution members</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="acknowledgments">
            <Card>
              <CardHeader><CardTitle className="text-lg">Acknowledgments</CardTitle></CardHeader>
              <CardContent>
                <p className="text-sm text-gray-400">Acknowledgment data will appear here.</p>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="controlled-copies">
            <Card>
              <CardHeader><CardTitle className="text-lg">Controlled Copies</CardTitle></CardHeader>
              <CardContent>
                {ccList.length > 0 ? (
                  <div className="space-y-2">
                    {ccList.map((cc: ControlledCopy) => (
                      <div
                        key={cc.id}
                        className="flex items-center justify-between rounded border px-3 py-2 text-sm dark:border-gray-700"
                      >
                        <div>
                          <span className="font-medium">{cc.copy_number}</span>
                          <span className="ml-2 text-gray-500">{cc.issued_to}</span>
                        </div>
                        <Badge variant={cc.status === "active" ? "default" : "secondary"}>
                          {cc.status}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-gray-400">No controlled copies issued</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="history">
            <Card>
              <CardHeader><CardTitle className="text-lg">Event History</CardTitle></CardHeader>
              <CardContent>
                {auditEvents.length > 0 ? (
                  <EventTimeline events={auditEvents.map((e: AuditEntry) => ({
                    id: e.id,
                    action: e.action,
                    actor: e.user_id || "system",
                    timestamp: e.created_at,
                    description: e.action,
                  }))} />
                ) : (
                  <p className="text-sm text-gray-400">No audit events recorded yet</p>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="details">
            <Card>
              <CardHeader><CardTitle className="text-lg">All Fields</CardTitle></CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                  {infoCardFields.map((f) => (
                    <div key={f.label}>
                      <p className="text-xs font-medium text-gray-500 dark:text-gray-400">{f.label}</p>
                      <p className="mt-0.5 text-sm text-gray-900 dark:text-gray-100 break-all">
                        {f.badge ? <StatusBadge status={f.value} /> : f.value || "-"}
                      </p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>

      {/* Signature Dialog */}
      <SignatureDialog
        open={signatureDialog.open}
        onOpenChange={(open) => setSignatureDialog({ ...signatureDialog, open })}
        title={
          signatureDialog.action === "approve" ? "Approve Document" :
          signatureDialog.action === "acknowledge" ? "Acknowledge Document" :
          signatureDialog.action === "make-effective" ? "Release as Effective" :
          signatureDialog.action === "make-superseded" ? "Mark Superseded" : "Signature Required"
        }
        description={
          signatureDialog.action === "approve" ? "Enter your e-signature passphrase to approve this document." :
          signatureDialog.action === "acknowledge" ? "Enter your e-signature passphrase to acknowledge this document." :
          signatureDialog.action === "make-effective" ? "Enter your e-signature to release this document as effective." :
          signatureDialog.action === "make-superseded" ? "Enter your e-signature to mark this document as superseded." : ""
        }
        meaning="I have reviewed this document and agree with its contents. This constitutes my legally binding electronic signature."
        onConfirm={(signature) => handleSignatureSubmit(signatureDialog.action, signature)}
        isLoading={approveDoc.isPending}
      />

      {/* Reject Dialog */}
      <Dialog open={rejectDialogOpen} onOpenChange={setRejectDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Document</DialogTitle>
            <DialogDescription>Provide a reason for rejection.</DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="reject-reason">Reason *</Label>
            <Textarea
              id="reject-reason"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="Explain why the document is being rejected..."
              rows={3}
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleReject} disabled={!rejectReason.trim()}>
              Reject
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Make Obsolete Dialog */}
      <Dialog open={obsoleteDialogOpen} onOpenChange={setObsoleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Mark Obsolete</DialogTitle>
            <DialogDescription>Are you sure you want to mark this document as obsolete?</DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setObsoleteDialogOpen(false)}>Cancel</Button>
            <Button variant="destructive" onClick={handleMakeObsolete}>Mark Obsolete</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
