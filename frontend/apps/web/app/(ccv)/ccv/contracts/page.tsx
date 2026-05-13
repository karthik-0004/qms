"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
  FileText,
  Search,
  Plus,
  ChevronLeft,
  ChevronRight,
  Loader2,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useContracts, useCreateContract, useCustomers } from "@/lib/hooks/queries/ccv";
import type { Contract } from "@/lib/api/services/ccv";
import { toast } from "sonner";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-slate-100 text-slate-700" },
  under_review: { label: "Under Review", color: "bg-amber-100 text-amber-800" },
  approved: { label: "Approved", color: "bg-blue-100 text-blue-800" },
  active: { label: "Active", color: "bg-green-100 text-green-800" },
  expired: { label: "Expired", color: "bg-slate-100 text-slate-500" },
  terminated: { label: "Terminated", color: "bg-red-100 text-red-700" },
  cancelled: { label: "Cancelled", color: "bg-red-50 text-red-600" },
};

const CONTRACT_TYPES = [
  "service_agreement",
  "maintenance_contract",
  "calibration_contract",
  "validation_contract",
  "supply_agreement",
  "nda",
  "other",
];

const PAGE_SIZE = 10;

export default function ContractsPage() {
  const router = useRouter();
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [page, setPage] = useState(1);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const { data, isLoading: loading } = useContracts({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const { data: customersData } = useCustomers({ page_size: 100 });
  const customers = customersData?.items ?? [];
  const createContract = useCreateContract();

  const contracts: Contract[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = contracts;

  const handleSearch = useCallback((val: string) => {
    setSearch(val);
    setPage(1);
  }, []);

  const [formData, setFormData] = useState({
    title: "",
    customer_id: "",
    contract_type: "service_agreement",
    contract_number: "",
    start_date: "",
    end_date: "",
    total_value: "",
    currency: "USD",
    payment_terms: "",
    description: "",
    notes: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createContract.mutateAsync({
        title: formData.title,
        customer_id: formData.customer_id,
        contract_type: formData.contract_type,
        contract_number: formData.contract_number || undefined,
        start_date: formData.start_date || undefined,
        end_date: formData.end_date || undefined,
        total_value: formData.total_value ? parseFloat(formData.total_value) : undefined,
        currency: formData.currency,
        payment_terms: formData.payment_terms || undefined,
        description: formData.description || undefined,
        notes: formData.notes || undefined,
      });
      toast.success("Contract created successfully");
      setShowCreateDialog(false);
      setFormData({
        title: "",
        customer_id: "",
        contract_type: "service_agreement",
        contract_number: "",
        start_date: "",
        end_date: "",
        total_value: "",
        currency: "USD",
        payment_terms: "",
        description: "",
        notes: "",
      });
    } catch (error) {
      toast.error("Failed to create contract");
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6" />
            Contracts
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Manage service agreements, maintenance contracts, and NDAs
          </p>
        </div>
        <Button size="sm" className="gap-1.5" onClick={() => setShowCreateDialog(true)}>
          <Plus className="h-4 w-4" />
          New Contract
        </Button>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by number, title, customer…"
                className="pl-8"
                value={search}
                onChange={(e) => handleSearch(e.target.value)}
              />
            </div>
            <select
              value={statusFilter}
              onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (
                <option key={k} value={k}>{v.label}</option>
              ))}
            </select>
            <select
              value={typeFilter}
              onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm capitalize"
            >
              <option value="">All Types</option>
              {CONTRACT_TYPES.map((t) => (
                <option key={t} value={t}>{t.replace(/_/g, " ")}</option>
              ))}
            </select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card>
        <CardHeader className="pb-0">
          <CardTitle className="text-sm font-medium text-muted-foreground">
            {loading ? "Loading…" : `${totalItems} contracts`}
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Number</th>
                  <th className="pb-2 pr-4 font-medium">Title</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Customer</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Type</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Value</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden md:table-cell">End Date</th>
                </tr>
              </thead>
              <tbody>
                {loading
                  ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                    <tr key={i} className="border-b">
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-28" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-4 w-40" /></td>
                      <td className="py-3 pr-4 hidden sm:table-cell"><Skeleton className="h-4 w-32" /></td>
                      <td className="py-3 pr-4 hidden md:table-cell"><Skeleton className="h-4 w-24" /></td>
                      <td className="py-3 pr-4 hidden lg:table-cell"><Skeleton className="h-4 w-16" /></td>
                      <td className="py-3 pr-4"><Skeleton className="h-5 w-20 rounded-full" /></td>
                      <td className="py-3 hidden md:table-cell"><Skeleton className="h-4 w-20" /></td>
                    </tr>
                  ))
                  : paginated.map((c) => {
                    const cfg = STATUS_CONFIG[c.status] ?? { label: c.status, color: "" };
                    return (
                      <tr
                        key={c.id}
                        className="border-b last:border-0 hover:bg-muted/30 transition-colors cursor-pointer"
                        onClick={() => router.push(`/ccv/contracts/${c.id}` as any)}
                      >
                        <td className="py-3 pr-4 font-mono font-semibold text-xs">
                          {c.contract_number}
                        </td>
                        <td className="py-3 pr-4 font-medium max-w-[200px] truncate">
                          {c.title}
                        </td>
                        <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">
                          {c.customer?.company_name ?? c.customer_id}
                        </td>
                        <td className="py-3 pr-4 capitalize text-muted-foreground hidden md:table-cell">
                          {c.contract_type.replace(/_/g, " ")}
                        </td>
                        <td className="py-3 pr-4 font-medium hidden lg:table-cell">
                          {c.total_value && c.total_value > 0 ? `$${c.total_value.toLocaleString()}` : "—"}
                        </td>
                        <td className="py-3 pr-4">
                          <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>
                            {cfg.label}
                          </span>
                        </td>
                        <td className="py-3 text-muted-foreground text-xs hidden md:table-cell">
                          {c.end_date ? new Date(c.end_date).toLocaleDateString() : "—"}
                        </td>
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {!loading && totalItems > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">
                Page {page} of {totalPages}
              </p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={page === 1}
                >
                  <ChevronLeft className="h-4 w-4" />
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                  disabled={page === totalPages}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Contract Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Contract</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="contract_number">Contract Number</Label>
                <Input
                  id="contract_number"
                  value={formData.contract_number}
                  onChange={(e) => setFormData({ ...formData, contract_number: e.target.value })}
                  placeholder="Auto-generated if empty"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="customer_id">Customer *</Label>
                <select
                  id="customer_id"
                  value={formData.customer_id}
                  onChange={(e) => setFormData({ ...formData, customer_id: e.target.value })}
                  required
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="">Select a customer...</option>
                  {customers.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.company_name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="contract_type">Contract Type *</Label>
                <select
                  id="contract_type"
                  value={formData.contract_type}
                  onChange={(e) => setFormData({ ...formData, contract_type: e.target.value })}
                  required
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm capitalize"
                >
                  {CONTRACT_TYPES.map((t) => (
                    <option key={t} value={t}>
                      {t.replace(/_/g, " ")}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start_date">Start Date</Label>
                <Input
                  id="start_date"
                  type="date"
                  value={formData.start_date}
                  onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end_date">End Date</Label>
                <Input
                  id="end_date"
                  type="date"
                  value={formData.end_date}
                  onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="total_value">Total Value</Label>
                <Input
                  id="total_value"
                  type="number"
                  step="0.01"
                  value={formData.total_value}
                  onChange={(e) => setFormData({ ...formData, total_value: e.target.value })}
                  placeholder="0.00"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="payment_terms">Payment Terms</Label>
                <Input
                  id="payment_terms"
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                  placeholder="e.g., Net 30"
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description / Scope</Label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Describe the contract scope..."
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full min-h-[60px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Additional notes..."
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowCreateDialog(false)}
                disabled={createContract.isPending}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createContract.isPending}>
                {createContract.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Creating...
                  </>
                ) : (
                  "Create Contract"
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
