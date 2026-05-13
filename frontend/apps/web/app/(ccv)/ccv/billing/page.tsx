"use client";

import { useState } from "react";
import { DollarSign, Plus, Search, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { useInvoices, useCreateInvoice, useCustomers, useContracts, useWorkOrders } from "@/lib/hooks/queries/ccv";
import type { Invoice } from "@/lib/api/services/ccv";
import { toast } from "sonner";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-slate-100 text-slate-700" },
  sent: { label: "Sent", color: "bg-blue-100 text-blue-700" },
  partially_paid: { label: "Partial", color: "bg-amber-100 text-amber-700" },
  paid: { label: "Paid", color: "bg-green-100 text-green-700" },
  overdue: { label: "Overdue", color: "bg-red-100 text-red-700" },
  cancelled: { label: "Cancelled", color: "bg-slate-100 text-slate-500" },
  void: { label: "Void", color: "bg-slate-100 text-slate-400" },
};

const PAGE_SIZE = 10;

export default function BillingPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("");
  const [page, setPage] = useState(1);
  const [showCreateDialog, setShowCreateDialog] = useState(false);

  const { data, isLoading: loading } = useInvoices({
    search: search || undefined,
    status: statusFilter || undefined,
    page,
    page_size: PAGE_SIZE,
  });

  const { data: customersData } = useCustomers({ page_size: 100 });
  const { data: contractsData } = useContracts({ page_size: 100 });
  const { data: workOrdersData } = useWorkOrders({ page_size: 100 });
  const customers = customersData?.items ?? [];
  const contracts = contractsData?.items ?? [];
  const workOrders = workOrdersData?.items ?? [];
  const createInvoice = useCreateInvoice();

  const invoices: Invoice[] = data?.items ?? [];
  const totalItems = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(totalItems / PAGE_SIZE));
  const paginated = invoices;

  const fmt = (n: number | undefined | null) => n != null ? `$${n.toLocaleString()}` : "—";

  const [formData, setFormData] = useState({
    customer_id: "",
    contract_id: "",
    work_order_id: "",
    invoice_number: "",
    due_date: "",
    currency: "USD",
    tax_rate: "0",
    payment_terms: "",
    notes: "",
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await createInvoice.mutateAsync({
        customer_id: formData.customer_id,
        contract_id: formData.contract_id || undefined,
        work_order_id: formData.work_order_id || undefined,
        invoice_number: formData.invoice_number || undefined,
        due_date: formData.due_date || undefined,
        currency: formData.currency,
        tax_rate: parseFloat(formData.tax_rate),
        payment_terms: formData.payment_terms || undefined,
        notes: formData.notes || undefined,
      });
      toast.success("Invoice created successfully");
      setShowCreateDialog(false);
      setFormData({
        customer_id: "",
        contract_id: "",
        work_order_id: "",
        invoice_number: "",
        due_date: "",
        currency: "USD",
        tax_rate: "0",
        payment_terms: "",
        notes: "",
      });
    } catch (error) {
      toast.error("Failed to create invoice");
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <DollarSign className="h-6 w-6" />
            Billing
          </h1>
          <p className="text-muted-foreground text-sm mt-1">Invoice generation, payment tracking, and billing lifecycle</p>
        </div>
        <Button size="sm" className="gap-1.5" onClick={() => setShowCreateDialog(true)}><Plus className="h-4 w-4" />New Invoice</Button>
      </div>

      <Card>
        <CardContent className="pt-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="relative flex-1">
              <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
              <Input placeholder="Search invoices..." className="pl-8" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} />
            </div>
            <select value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }} className="h-9 rounded-md border border-input bg-background px-3 text-sm">
              <option value="">All Statuses</option>
              {Object.entries(STATUS_CONFIG).map(([k, v]) => (<option key={k} value={k}>{v.label}</option>))}
            </select>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="pb-0"><CardTitle className="text-sm font-medium text-muted-foreground">{loading ? "Loading…" : `${totalItems} invoices`}</CardTitle></CardHeader>
        <CardContent className="pt-2">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-muted-foreground">
                  <th className="pb-2 pr-4 font-medium">Invoice #</th>
                  <th className="pb-2 pr-4 font-medium hidden sm:table-cell">Customer</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Total</th>
                  <th className="pb-2 pr-4 font-medium hidden lg:table-cell">Paid</th>
                  <th className="pb-2 pr-4 font-medium hidden md:table-cell">Due</th>
                  <th className="pb-2 pr-4 font-medium">Status</th>
                  <th className="pb-2 font-medium hidden lg:table-cell">Due Date</th>
                </tr>
              </thead>
              <tbody>
                {loading ? Array.from({ length: PAGE_SIZE }).map((_, i) => (
                  <tr key={i} className="border-b">{Array.from({ length: 7 }).map((_, j) => (<td key={j} className="py-3 pr-4"><Skeleton className="h-4 w-20" /></td>))}</tr>
                )) : paginated.map((inv) => {
                  const cfg = STATUS_CONFIG[inv.status] ?? { label: inv.status, color: "" };
                  return (
                    <tr key={inv.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                      <td className="py-3 pr-4 font-mono font-semibold text-xs">{inv.invoice_number}</td>
                      <td className="py-3 pr-4 text-muted-foreground hidden sm:table-cell">{inv.customer_id}</td>
                      <td className="py-3 pr-4 font-medium hidden md:table-cell">{fmt(inv.total_amount)}</td>
                      <td className="py-3 pr-4 text-green-600 hidden lg:table-cell">{fmt(inv.amount_paid)}</td>
                      <td className="py-3 pr-4 font-medium hidden md:table-cell">{inv.amount_due > 0 ? fmt(inv.amount_due) : "—"}</td>
                      <td className="py-3 pr-4"><span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.color}`}>{cfg.label}</span></td>
                      <td className="py-3 text-muted-foreground text-xs hidden lg:table-cell">{inv.due_date ? new Date(inv.due_date).toLocaleDateString() : "—"}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {!loading && totalItems > PAGE_SIZE && (
            <div className="flex items-center justify-between mt-4 pt-4 border-t">
              <p className="text-xs text-muted-foreground">Page {page} of {totalPages}</p>
              <div className="flex gap-2">
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}><ChevronLeft className="h-4 w-4" /></Button>
                <Button variant="outline" size="sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}><ChevronRight className="h-4 w-4" /></Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Create Invoice Dialog */}
      <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Create New Invoice</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleSubmit} className="space-y-4">
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
                <Label htmlFor="invoice_number">Invoice Number</Label>
                <Input
                  id="invoice_number"
                  value={formData.invoice_number}
                  onChange={(e) => setFormData({ ...formData, invoice_number: e.target.value })}
                  placeholder="Auto-generated if empty"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="contract_id">Contract</Label>
                <select
                  id="contract_id"
                  value={formData.contract_id}
                  onChange={(e) => setFormData({ ...formData, contract_id: e.target.value })}
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="">Select a contract (optional)...</option>
                  {contracts.map((c) => (
                    <option key={c.id} value={c.id}>
                      {c.contract_number} - {c.title}
                    </option>
                  ))}
                </select>
              </div>
              <div className="space-y-2">
                <Label htmlFor="work_order_id">Work Order</Label>
                <select
                  id="work_order_id"
                  value={formData.work_order_id}
                  onChange={(e) => setFormData({ ...formData, work_order_id: e.target.value })}
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="">Select a work order (optional)...</option>
                  {workOrders.map((wo) => (
                    <option key={wo.id} value={wo.id}>
                      {wo.work_order_number} - {wo.title}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  id="due_date"
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="currency">Currency</Label>
                <select
                  id="currency"
                  value={formData.currency}
                  onChange={(e) => setFormData({ ...formData, currency: e.target.value })}
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="USD">USD</option>
                  <option value="EUR">EUR</option>
                  <option value="GBP">GBP</option>
                  <option value="CAD">CAD</option>
                  <option value="AUD">AUD</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="tax_rate">Tax Rate (%)</Label>
                <Input
                  id="tax_rate"
                  type="number"
                  step="0.1"
                  value={formData.tax_rate}
                  onChange={(e) => setFormData({ ...formData, tax_rate: e.target.value })}
                  placeholder="0"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="payment_terms">Payment Terms</Label>
                <Input
                  id="payment_terms"
                  value={formData.payment_terms}
                  onChange={(e) => setFormData({ ...formData, payment_terms: e.target.value })}
                  placeholder="Net 30, Net 60, etc."
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes</Label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                placeholder="Additional notes for the invoice..."
              />
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => setShowCreateDialog(false)}
                disabled={createInvoice.isPending}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={createInvoice.isPending}>
                {createInvoice.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Creating...
                  </>
                ) : (
                  "Create Invoice"
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
}
