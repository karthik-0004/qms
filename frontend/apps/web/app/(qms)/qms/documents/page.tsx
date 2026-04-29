"use client";

import { useState, lazy, Suspense } from "react";
import { useRouter } from "next/navigation";
import { FileText, Plus, Search, ChevronLeft, ChevronRight, ArrowLeft, Home } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { useDocuments, useCreateDocument } from "@/lib/hooks/queries/qms";
import type { Document } from "@/lib/api/services/qms";
import { toast } from "sonner";

const Dialog = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.Dialog })));
const DialogContent = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogContent })));
const DialogDescription = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogDescription })));
const DialogFooter = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogFooter })));
const DialogHeader = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogHeader })));
const DialogTitle = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogTitle })));
const DialogTrigger = lazy(() => import("@/components/ui/dialog").then(m => ({ default: m.DialogTrigger })));

const STATUS_COLORS: Record<string, string> = {
  draft: "bg-gray-100 text-gray-700",
  under_review: "bg-yellow-100 text-yellow-700",
  approved: "bg-green-100 text-green-700",
  obsolete: "bg-red-100 text-red-700",
};

const PAGE_SIZE = 20;

export default function DocumentsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("");
  const [page, setPage] = useState(1);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [formData, setFormData] = useState({
    title: "",
    doc_type: "SOP",
    content: "",
  });

  const { data, isLoading } = useDocuments({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const createDocument = useCreateDocument();

  const documents: Document[] = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    createDocument.mutate(
      {
        title: formData.title,
        doc_type: formData.doc_type,
        content: formData.content,
      },
      {
        onSuccess: () => {
          toast.success("Document created successfully");
          setDialogOpen(false);
          setFormData({ title: "", doc_type: "SOP", content: "" });
        },
        onError: (error: any) => {
          const errorMessage = error?.response?.data?.detail || error?.message || "Failed to create document";
          toast.error(errorMessage);
          console.error("Error creating document:", error);
        },
      }
    );
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Breadcrumb Navigation */}
      <div className="flex items-center gap-2 text-sm">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
        <span className="text-muted-foreground">/</span>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => router.push("/dashboard")}
          className="h-7 px-2 text-muted-foreground hover:text-foreground"
        >
          <Home className="h-4 w-4 mr-1" />
          Home
        </Button>
        <span className="text-muted-foreground">/</span>
        <span className="text-foreground font-medium">Document Control</span>
      </div>

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Document Control
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage SOPs, work instructions, and quality documents
          </p>
        </div>
        <Suspense fallback={<Button size="sm" className="gap-1.5"><Plus className="h-4 w-4" />New Document</Button>}>
          <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
            <DialogTrigger asChild>
              <Button size="sm" className="gap-1.5">
                <Plus className="h-4 w-4" />
                New Document
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Document</DialogTitle>
                <DialogDescription>
                  Create a new document for SOPs, work instructions, or quality documents.
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleSubmit}>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Title</Label>
                    <Input
                      id="title"
                      value={formData.title}
                      onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                      placeholder="Document title"
                      required
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="doc_type">Document Type</Label>
                    <select
                      id="doc_type"
                      value={formData.doc_type}
                      onChange={(e) => setFormData({ ...formData, doc_type: e.target.value })}
                      className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                    >
                      <option value="SOP">SOP</option>
                      <option value="Work Instruction">Work Instruction</option>
                      <option value="Policy">Policy</option>
                      <option value="Form">Form</option>
                      <option value="Record">Record</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="content">Content</Label>
                    <Input
                      id="content"
                      value={formData.content}
                      onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                      placeholder="Document content or description"
                      required
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={createDocument.isPending}>
                    {createDocument.isPending ? "Creating..." : "Create Document"}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>
        </Suspense>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search documents..."
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                className="pl-8"
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">All Statuses</option>
              {Object.entries(STATUS_COLORS).map(([k, v]) => (
                <option key={k} value={k}>{k.replace("_", " ")}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Documents Table */}
      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {isLoading ? "Loading…" : `${total} documents`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Doc #</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Type</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Version</th>
                  <th className="pb-2 font-medium hidden md:table-cell">Updated</th>
                </tr>
              </thead>
              <tbody>
                {isLoading ? (
                  Array.from({ length: 5 }).map((_, i) => (
                    <tr key={i} className="border-b">
                      {Array.from({ length: 6 }).map((_, j) => (
                        <td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-24" /></td>
                      ))}
                    </tr>
                  ))
                ) : documents.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-12 text-center text-muted-foreground">
                      No documents found. Create your first document to get started.
                    </td>
                  </tr>
                ) : (
                  documents.map((doc) => (
                    <tr
                      key={doc.id}
                      className="border-b last:border-0 hover:bg-muted/30 cursor-pointer transition-colors"
                    >
                      <td className="py-3 pr-4 font-mono text-xs text-muted-foreground">{doc.document_number}</td>
                      <td className="py-3 pr-4 font-medium">{doc.title}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{doc.doc_type}</td>
                      <td className="py-3 pr-4">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium capitalize ${STATUS_COLORS[doc.status] ?? "bg-gray-100 text-gray-700"}`}>
                          {doc.status.replace("_", " ")}
                        </span>
                      </td>
                      <td className="py-3 pr-4 text-muted-foreground hidden md:table-cell">v{doc.version}</td>
                      <td className="py-3 text-muted-foreground text-xs hidden md:table-cell">
                        {new Date(doc.updated_at).toLocaleDateString()}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!isLoading && totalPages > 1 && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">Page {page} of {totalPages} · {total} results</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
