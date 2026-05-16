"use client";

import { useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import {
  FileText, Plus, Search, ChevronRight, Folder, FolderOpen,
  FolderPlus, Home, SlidersHorizontal, X, Grid3X3, List,
  MoreVertical, ArrowLeft, ChevronLeft,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import {
  Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter,
} from "@/components/ui/dialog";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useDocuments } from "@/lib/hooks/queries/qms";
import { taxonomyApi } from "@/lib/api/services/qms";
import type { Document, Taxonomy, Folder as FolderType } from "@/lib/api/services/qms";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { StatusBadge } from "@/components/qms-shared/StatusBadge";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import { toast } from "sonner";

const PAGE_SIZE = 25;
const STATUS_OPTIONS = [
  { label: "Draft", value: "draft" },
  { label: "Under Review", value: "under_review" },
  { label: "Approved", value: "approved" },
  { label: "Effective", value: "effective" },
  { label: "Superseded", value: "superseded" },
  { label: "Obsolete", value: "obsolete" },
];
const DOC_TYPE_OPTIONS = [
  { label: "SOP", value: "SOP" },
  { label: "Work Instruction", value: "Work Instruction" },
  { label: "Policy", value: "Policy" },
  { label: "Form", value: "Form" },
  { label: "Record", value: "Record" },
  { label: "Manual", value: "Manual" },
  { label: "Template", value: "Template" },
];

type ViewMode = "list" | "grid";

// ─── Navigation state ─────────────────────────────────────────────────────────
type Level = "root" | "taxonomy" | "folder";
interface NavState {
  level: Level;
  taxonomyId: string | null;
  folderId: string | null;
  taxonomyName: string;
  folderName: string;
}

const ROOT_NAV: NavState = { level: "root", taxonomyId: null, folderId: null, taxonomyName: "", folderName: "" };

export default function DocumentsExplorerPage() {
  const router = useRouter();
  const qc = useQueryClient();

  const [nav, setNav] = useState<NavState>(ROOT_NAV);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [docTypeFilter, setDocTypeFilter] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<ViewMode>("list");
  const [showFilters, setShowFilters] = useState(false);
  const [showNewTaxonomy, setShowNewTaxonomy] = useState(false);
  const [showNewFolder, setShowNewFolder] = useState(false);
  const [newName, setNewName] = useState("");

  // Load taxonomy list
  const { data: taxonomies } = useQuery({
    queryKey: ["taxonomies"],
    queryFn: () => taxonomyApi.list(),
    staleTime: 60_000,
  });

  // Load folders when inside a taxonomy
  const { data: folders } = useQuery({
    queryKey: ["taxonomy-folders", nav.taxonomyId],
    queryFn: () => taxonomyApi.listFolders(nav.taxonomyId!),
    enabled: !!nav.taxonomyId && nav.level !== "folder",
    staleTime: 60_000,
  });

  // Load documents — filtered by current location
  const { data, isLoading } = useDocuments({
    search: search || undefined,
    status: statusFilter || undefined,
    doc_type: docTypeFilter || undefined,
    taxonomy_id: nav.level === "taxonomy" ? nav.taxonomyId ?? undefined : undefined,
    folder_id: nav.level === "folder" ? nav.folderId ?? undefined : undefined,
    page,
    page_size: PAGE_SIZE,
  } as Parameters<typeof useDocuments>[0]);

  const createTaxonomy = useMutation({
    mutationFn: (name: string) => taxonomyApi.create({ name }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["taxonomies"] }); toast.success("Category created"); setShowNewTaxonomy(false); setNewName(""); },
    onError: () => toast.error("Failed to create category"),
  });

  const createFolder = useMutation({
    mutationFn: ({ name }: { name: string }) => taxonomyApi.createFolder(nav.taxonomyId!, { name }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["taxonomy-folders", nav.taxonomyId] }); toast.success("Folder created"); setShowNewFolder(false); setNewName(""); },
    onError: () => toast.error("Failed to create folder"),
  });

  const documents: Document[] = data?.items ?? [];
  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  const hasActiveFilters = !!(statusFilter || docTypeFilter || search);

  // Navigate into taxonomy
  function enterTaxonomy(tx: Taxonomy) {
    setNav({ level: "taxonomy", taxonomyId: tx.id, folderId: null, taxonomyName: tx.name, folderName: "" });
    setPage(1);
  }

  // Navigate into folder
  function enterFolder(f: FolderType) {
    setNav((prev) => ({ ...prev, level: "folder", folderId: f.id, folderName: f.name }));
    setPage(1);
  }

  // Navigate up one level
  function navigateUp() {
    if (nav.level === "folder") {
      setNav((prev) => ({ ...prev, level: "taxonomy", folderId: null, folderName: "" }));
    } else {
      setNav(ROOT_NAV);
    }
    setPage(1);
    setSearch("");
  }

  function clearFilters() { setStatusFilter(""); setDocTypeFilter(""); setSearch(""); setPage(1); }

  // Breadcrumb items
  const breadcrumbs = useMemo(() => {
    const bc = [{ label: "All Documents", onClick: () => { setNav(ROOT_NAV); setPage(1); } }];
    if (nav.taxonomyId) bc.push({ label: nav.taxonomyName, onClick: () => { setNav((p) => ({ ...p, level: "taxonomy", folderId: null })); setPage(1); } });
    if (nav.folderId) bc.push({ label: nav.folderName, onClick: () => {} });
    return bc;
  }, [nav]);

  // Root: show taxonomy category cards
  if (nav.level === "root" && !search) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
        <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="mb-6 flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Document Control</h1>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Browse categories or search all documents</p>
            </div>
            <div className="flex items-center gap-2">
              <Button variant="outline" size="sm" onClick={() => setShowNewTaxonomy(true)}>
                <FolderPlus className="mr-1.5 h-4 w-4" />
                New Category
              </Button>
              <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => router.push("/qms/documents/create")}>
                <Plus className="mr-1.5 h-4 w-4" />
                New Document
              </Button>
            </div>
          </div>

          {/* Quick search */}
          <div className="mb-6 relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Search all documents…"
              className="pl-9 h-10 text-sm max-w-lg"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {/* Category cards — Google Drive style */}
          {(taxonomies ?? []).length === 0 ? (
            <div className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-200 py-16 text-center dark:border-gray-700">
              <Folder className="mb-3 h-12 w-12 text-gray-300 dark:text-gray-600" />
              <p className="font-medium text-gray-600 dark:text-gray-400">No categories yet</p>
              <p className="mt-1 text-sm text-gray-400">Create a category to organize your documents</p>
              <Button size="sm" variant="outline" className="mt-4" onClick={() => setShowNewTaxonomy(true)}>
                <FolderPlus className="mr-1.5 h-4 w-4" />
                Create First Category
              </Button>
            </div>
          ) : (
            <>
              <h2 className="mb-3 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Categories</h2>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
                {(taxonomies ?? []).map((tx: Taxonomy) => (
                  <button
                    key={tx.id}
                    onClick={() => enterTaxonomy(tx)}
                    className="group flex flex-col items-center gap-2 rounded-xl border border-gray-200 bg-white p-5 text-center transition-all hover:border-amber-300 hover:shadow-md dark:border-gray-700 dark:bg-gray-900 dark:hover:border-amber-600"
                  >
                    <div className="rounded-lg bg-amber-50 p-3 group-hover:bg-amber-100 dark:bg-amber-900/20 dark:group-hover:bg-amber-900/40">
                      <Folder className="h-8 w-8 text-amber-500" />
                    </div>
                    <span className="text-sm font-medium text-gray-800 dark:text-gray-200 line-clamp-2">{tx.name}</span>
                  </button>
                ))}
                <button
                  onClick={() => setShowNewTaxonomy(true)}
                  className="flex flex-col items-center gap-2 rounded-xl border-2 border-dashed border-gray-200 p-5 text-center transition-all hover:border-blue-300 hover:bg-blue-50 dark:border-gray-700 dark:hover:border-blue-600 dark:hover:bg-blue-900/10"
                >
                  <div className="rounded-lg bg-gray-50 p-3 dark:bg-gray-800">
                    <FolderPlus className="h-8 w-8 text-gray-400" />
                  </div>
                  <span className="text-sm text-gray-500">New Category</span>
                </button>
              </div>

              {/* Recent documents */}
              <div className="mt-8">
                <h2 className="mb-3 text-sm font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Recent Documents</h2>
                <RecentDocuments router={router} />
              </div>
            </>
          )}
        </div>

        {/* Dialogs */}
        <NewNameDialog
          open={showNewTaxonomy}
          onClose={() => { setShowNewTaxonomy(false); setNewName(""); }}
          title="New Category"
          placeholder="e.g. Quality Manual, SOPs, Forms"
          value={newName}
          onChange={setNewName}
          onSubmit={() => createTaxonomy.mutate(newName.trim())}
          isPending={createTaxonomy.isPending}
        />
      </div>
    );
  }

  // Taxonomy or Folder level
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-950">
      <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button variant="ghost" size="sm" onClick={navigateUp} className="h-8 w-8 p-0">
              <ArrowLeft className="h-4 w-4" />
            </Button>
            {/* Breadcrumb */}
            <nav className="flex items-center gap-1 text-sm">
              {breadcrumbs.map((bc, i) => (
                <span key={i} className="flex items-center gap-1">
                  {i > 0 && <ChevronRight className="h-3.5 w-3.5 text-gray-300" />}
                  <button
                    onClick={bc.onClick}
                    className={cn(
                      i < breadcrumbs.length - 1
                        ? "text-blue-600 hover:underline dark:text-blue-400"
                        : "font-semibold text-gray-900 dark:text-white"
                    )}
                  >
                    {i === 0 ? <Home className="inline h-3.5 w-3.5 mr-0.5" /> : null}
                    {bc.label}
                  </button>
                </span>
              ))}
            </nav>
          </div>
          <div className="flex items-center gap-2">
            {nav.level === "taxonomy" && (
              <Button variant="outline" size="sm" onClick={() => setShowNewFolder(true)}>
                <FolderPlus className="mr-1.5 h-4 w-4" />
                New Folder
              </Button>
            )}
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white" onClick={() => router.push("/qms/documents/create")}>
              <Plus className="mr-1.5 h-4 w-4" />
              New Document
            </Button>
          </div>
        </div>

        {/* Toolbar */}
        <div className="mb-3 flex items-center gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <Input
              placeholder="Search here…"
              value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              className="pl-9 h-9 text-sm"
            />
          </div>
          <Button variant="outline" size="sm" onClick={() => setShowFilters(!showFilters)} className={showFilters ? "border-blue-400 text-blue-600" : ""}>
            <SlidersHorizontal className="mr-1 h-4 w-4" />
            Filters
            {hasActiveFilters && <span className="ml-1 h-2 w-2 rounded-full bg-blue-500" />}
          </Button>
          <div className="flex rounded-md border border-gray-200 dark:border-gray-700 overflow-hidden">
            <button onClick={() => setViewMode("list")} className={cn("px-2 py-1.5", viewMode === "list" ? "bg-gray-100 dark:bg-gray-800" : "")}>
              <List className="h-4 w-4" />
            </button>
            <button onClick={() => setViewMode("grid")} className={cn("px-2 py-1.5", viewMode === "grid" ? "bg-gray-100 dark:bg-gray-800" : "")}>
              <Grid3X3 className="h-4 w-4" />
            </button>
          </div>
        </div>

        {showFilters && (
          <Card className="mb-3">
            <CardContent className="flex flex-wrap gap-4 p-3">
              <div className="min-w-[140px]">
                <Label className="text-xs">Status</Label>
                <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800">
                  <option value="">All</option>
                  {STATUS_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>
              <div className="min-w-[140px]">
                <Label className="text-xs">Type</Label>
                <select value={docTypeFilter} onChange={(e) => { setDocTypeFilter(e.target.value); setPage(1); }} className="mt-1 w-full rounded border border-gray-300 bg-white px-2 py-1.5 text-sm dark:border-gray-600 dark:bg-gray-800">
                  <option value="">All</option>
                  {DOC_TYPE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                </select>
              </div>
              {hasActiveFilters && <div className="flex items-end"><button onClick={clearFilters} className="text-xs text-blue-600 hover:text-blue-800">Clear all</button></div>}
            </CardContent>
          </Card>
        )}

        {/* Folders (when inside taxonomy) */}
        {nav.level === "taxonomy" && (folders ?? []).length > 0 && (
          <div className="mb-4">
            <p className="mb-2 text-xs font-medium uppercase tracking-wider text-gray-500 dark:text-gray-400">Folders</p>
            <div className="grid grid-cols-3 gap-3 sm:grid-cols-4 lg:grid-cols-6">
              {(folders ?? []).map((f: FolderType) => (
                <button
                  key={f.id}
                  onClick={() => enterFolder(f)}
                  className="group flex flex-col items-center gap-1.5 rounded-lg border border-gray-200 bg-white p-3 text-center transition-all hover:border-amber-300 hover:shadow-sm dark:border-gray-700 dark:bg-gray-900"
                >
                  <FolderOpen className="h-7 w-7 text-amber-400 group-hover:text-amber-500" />
                  <span className="text-xs font-medium text-gray-700 dark:text-gray-300 line-clamp-2">{f.name}</span>
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Documents table/grid */}
        <DocumentsView
          documents={documents}
          isLoading={isLoading}
          viewMode={viewMode}
          onOpen={(id) => router.push(`/qms/documents/${id}`)}
          emptyMessage={nav.level === "folder" ? "This folder is empty." : "No documents in this category."}
          onNewDocument={() => router.push("/qms/documents/create")}
        />

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-gray-500">{total} documents · Page {page} of {totalPages}</p>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                <ChevronLeft className="h-4 w-4" /> Prev
              </Button>
              <Button variant="outline" size="sm" disabled={page >= totalPages} onClick={() => setPage(page + 1)}>
                Next <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </div>
        )}
      </div>

      {/* New Folder dialog */}
      <NewNameDialog
        open={showNewFolder}
        onClose={() => { setShowNewFolder(false); setNewName(""); }}
        title={`New Folder in "${nav.taxonomyName}"`}
        placeholder="e.g. Microbiology, Chemistry"
        value={newName}
        onChange={setNewName}
        onSubmit={() => createFolder.mutate({ name: newName.trim() })}
        isPending={createFolder.isPending}
      />

      {/* New Category dialog */}
      <NewNameDialog
        open={showNewTaxonomy}
        onClose={() => { setShowNewTaxonomy(false); setNewName(""); }}
        title="New Category"
        placeholder="e.g. Quality Manual, SOPs, Forms"
        value={newName}
        onChange={setNewName}
        onSubmit={() => createTaxonomy.mutate(newName.trim())}
        isPending={createTaxonomy.isPending}
      />
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────────────────────

function RecentDocuments({ router }: { router: ReturnType<typeof useRouter> }) {
  const { data, isLoading } = useDocuments({ page: 1, page_size: 6 } as Parameters<typeof useDocuments>[0]);
  const docs = data?.items ?? [];
  if (isLoading) return <div className="grid grid-cols-3 gap-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 rounded-lg" />)}</div>;
  if (docs.length === 0) return <p className="text-sm text-gray-400">No documents yet.</p>;
  return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
      {docs.map((doc) => (
        <button
          key={doc.id}
          onClick={() => router.push(`/qms/documents/${doc.id}`)}
          className="flex items-center gap-2 rounded-lg border border-gray-200 bg-white p-3 text-left hover:border-blue-200 hover:shadow-sm dark:border-gray-700 dark:bg-gray-900"
        >
          <FileText className="h-5 w-5 shrink-0 text-blue-500" />
          <div className="min-w-0">
            <p className="truncate text-xs font-medium text-gray-800 dark:text-gray-200">{doc.title}</p>
            <p className="text-xs text-gray-400">{doc.doc_number}</p>
          </div>
        </button>
      ))}
    </div>
  );
}

function DocumentsView({
  documents, isLoading, viewMode, onOpen, emptyMessage, onNewDocument,
}: {
  documents: Document[];
  isLoading: boolean;
  viewMode: ViewMode;
  onOpen: (id: string) => void;
  emptyMessage: string;
  onNewDocument: () => void;
}) {
  if (isLoading) return <Card><CardContent className="space-y-2 p-4">{Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}</CardContent></Card>;

  if (documents.length === 0) return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-14 text-center">
        <FileText className="mb-3 h-10 w-10 text-gray-300" />
        <p className="text-gray-500">{emptyMessage}</p>
        <Button size="sm" className="mt-4 bg-blue-600 hover:bg-blue-700 text-white" onClick={onNewDocument}>
          <Plus className="mr-1.5 h-4 w-4" /> New Document
        </Button>
      </CardContent>
    </Card>
  );

  if (viewMode === "grid") return (
    <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 xl:grid-cols-4">
      {documents.map((doc) => (
        <button
          key={doc.id}
          onClick={() => onOpen(doc.id)}
          className="group rounded-lg border border-gray-200 bg-white p-3 text-left shadow-sm transition-all hover:border-blue-300 hover:shadow-md dark:border-gray-700 dark:bg-gray-900"
        >
          <div className="mb-2 flex items-start justify-between">
            <div className="rounded bg-blue-50 p-1.5 dark:bg-blue-900/20">
              <FileText className="h-5 w-5 text-blue-600" />
            </div>
            <StatusBadge status={doc.status} />
          </div>
          <p className="truncate text-sm font-medium text-gray-900 dark:text-white">{doc.title}</p>
          <p className="mt-0.5 text-xs text-gray-500">{doc.doc_number} · v{doc.current_version}</p>
        </button>
      ))}
    </div>
  );

  return (
    <Card>
      <CardContent className="p-0">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200 bg-gray-50 dark:border-gray-700 dark:bg-gray-900">
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Doc #</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Title</th>
                <th className="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 sm:table-cell">Type</th>
                <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500">Status</th>
                <th className="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 md:table-cell">Version</th>
                <th className="hidden px-4 py-3 text-left text-xs font-medium uppercase tracking-wider text-gray-500 lg:table-cell">Updated</th>
                <th className="w-10 px-2 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
              {documents.map((doc) => (
                <tr key={doc.id} className="group cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-900" onClick={() => onOpen(doc.id)}>
                  <td className="px-4 py-3 font-mono text-xs text-blue-600 dark:text-blue-400">{doc.doc_number}</td>
                  <td className="max-w-xs px-4 py-3">
                    <div className="flex items-center gap-2">
                      <FileText className="h-4 w-4 shrink-0 text-gray-400" />
                      <span className="truncate font-medium text-gray-900 dark:text-white">{doc.title}</span>
                    </div>
                  </td>
                  <td className="hidden px-4 py-3 sm:table-cell">
                    <Badge variant="outline" className="text-xs">{doc.doc_type}</Badge>
                  </td>
                  <td className="px-4 py-3"><StatusBadge status={doc.status} /></td>
                  <td className="hidden px-4 py-3 text-gray-600 dark:text-gray-400 md:table-cell">v{doc.current_version}</td>
                  <td className="hidden px-4 py-3 text-xs text-gray-500 lg:table-cell">
                    {doc.updated_at ? format(new Date(doc.updated_at), "MMM d, yyyy") : "—"}
                  </td>
                  <td className="px-2 py-3">
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                        <Button variant="ghost" size="sm" className="h-7 w-7 p-0 opacity-0 group-hover:opacity-100">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem onClick={(e) => { e.stopPropagation(); onOpen(doc.id); }}>Open</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function NewNameDialog({
  open, onClose, title, placeholder, value, onChange, onSubmit, isPending,
}: {
  open: boolean;
  onClose: () => void;
  title: string;
  placeholder: string;
  value: string;
  onChange: (v: string) => void;
  onSubmit: () => void;
  isPending: boolean;
}) {
  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent className="max-w-sm">
        <DialogHeader><DialogTitle>{title}</DialogTitle></DialogHeader>
        <div className="space-y-3 py-2">
          <div className="space-y-1">
            <Label className="text-xs">Name *</Label>
            <Input
              className="h-9 text-sm"
              placeholder={placeholder}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter" && value.trim()) onSubmit(); }}
              autoFocus
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={onClose}>Cancel</Button>
          <Button
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 text-white"
            disabled={!value.trim() || isPending}
            onClick={onSubmit}
          >
            {isPending ? "Creating…" : "Create"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
