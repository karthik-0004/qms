"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useForm } from "react-hook-form";
import {
  FileText,
  Loader2,
  Plus,
  List,
  History,
  DollarSign,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";
import {
  useContract,
  useContractLineItems,
  useContractHistory,
  useAddLineItem,
} from "@/lib/hooks/queries/ccv";
import { usePermission } from "@/lib/hooks/usePermission";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  draft: { label: "Draft", color: "bg-slate-100 text-slate-700" },
  under_review: { label: "Under Review", color: "bg-amber-100 text-amber-800" },
  approved: { label: "Approved", color: "bg-blue-100 text-blue-800" },
  active: { label: "Active", color: "bg-green-100 text-green-800" },
  expired: { label: "Expired", color: "bg-slate-100 text-slate-500" },
  terminated: { label: "Terminated", color: "bg-red-100 text-red-700" },
  cancelled: { label: "Cancelled", color: "bg-red-50 text-red-600" },
};

// Editable contract statuses for line items
const EDITABLE_STATUSES = ["draft", "under_review", "approved"];

interface LineItemFormValues {
  description: string;
  quantity: number;
  unit_price: number;
  unit: string;
}

export default function ContractDetailPage() {
  const params = useParams();
  const contractId = params.id as string;
  const { hasPermission } = usePermission();
  const canWrite = hasPermission("contract:write");

  const [activeTab, setActiveTab] = useState("overview");
  const [addLineItemOpen, setAddLineItemOpen] = useState(false);

  const { data: contract, isLoading: contractLoading } = useContract(contractId);
  const { data: lineItems, isLoading: lineItemsLoading } = useContractLineItems(contractId);
  const { data: history, isLoading: historyLoading } = useContractHistory(contractId);

  const addLineItem = useAddLineItem(contractId);

  const lineItemForm = useForm<LineItemFormValues>({
    defaultValues: {
      description: "",
      quantity: 1,
      unit_price: 0,
      unit: "",
    },
  });

  const onSubmitLineItem = async (values: LineItemFormValues) => {
    try {
      await addLineItem.mutateAsync({
        description: values.description.trim(),
        quantity: Number(values.quantity),
        unit_price: Number(values.unit_price),
        unit: values.unit.trim() || null,
      });
      setAddLineItemOpen(false);
      lineItemForm.reset();
    } catch (e) {
      toast.error("Failed to add line item");
    }
  };

  const totalValue = lineItems?.reduce((sum, item) => sum + item.total_price, 0) ?? 0;
  const canEditLineItems = contract && EDITABLE_STATUSES.includes(contract.status);

  if (contractLoading) {
    return (
      <div className="space-y-6 p-6 max-w-7xl mx-auto">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-4 w-48" />
        <Card>
          <CardContent className="p-6">
            <Skeleton className="h-32 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!contract) {
    return (
      <div className="space-y-6 p-6 max-w-7xl mx-auto">
        <p className="text-muted-foreground">Contract not found.</p>
      </div>
    );
  }

  const statusCfg = STATUS_CONFIG[contract.status] ?? { label: contract.status, color: "" };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <FileText className="h-6 w-6" />
            {contract.title}
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusCfg.color}`}>
              {statusCfg.label}
            </span>
            <span className="text-muted-foreground text-sm font-mono">{contract.contract_number}</span>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="line-items">
            <List className="h-4 w-4 mr-1" />
            Line Items
          </TabsTrigger>
          <TabsTrigger value="history">
            <History className="h-4 w-4 mr-1" />
            History
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Contract Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Contract Type</p>
                  <p className="text-sm font-medium capitalize">{contract.contract_type.replace(/_/g, " ")}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Customer ID</p>
                  <p className="text-sm font-medium font-mono">{contract.customer_id}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Start Date</p>
                  <p className="text-sm font-medium">
                    {contract.start_date ? new Date(contract.start_date).toLocaleDateString() : "—"}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">End Date</p>
                  <p className="text-sm font-medium">
                    {contract.end_date ? new Date(contract.end_date).toLocaleDateString() : "—"}
                  </p>
                </div>
              </div>
              {contract.description && (
                <div>
                  <p className="text-sm text-muted-foreground">Description</p>
                  <p className="text-sm font-medium">{contract.description}</p>
                </div>
              )}
              {contract.payment_terms && (
                <div>
                  <p className="text-sm text-muted-foreground">Payment Terms</p>
                  <p className="text-sm font-medium">{contract.payment_terms}</p>
                </div>
              )}
              {contract.approved_at && (
                <div>
                  <p className="text-sm text-muted-foreground">Approved</p>
                  <p className="text-sm font-medium">
                    {new Date(contract.approved_at).toLocaleDateString()}
                    {contract.approved_by && ` by ${contract.approved_by.slice(0, 8)}...`}
                  </p>
                </div>
              )}
              {contract.signed_at && (
                <div>
                  <p className="text-sm text-muted-foreground">Signed</p>
                  <p className="text-sm font-medium">
                    {new Date(contract.signed_at).toLocaleDateString()}
                    {contract.signed_by && ` by ${contract.signed_by.slice(0, 8)}...`}
                  </p>
                </div>
              )}
              {contract.notes && (
                <div>
                  <p className="text-sm text-muted-foreground">Notes</p>
                  <p className="text-sm font-medium">{contract.notes}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Line Items Tab */}
        <TabsContent value="line-items" className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold">Line Items</h2>
              <Badge variant="secondary" className="font-mono">
                <DollarSign className="h-3 w-3 mr-1" />
                Total: {totalValue.toLocaleString(undefined, { style: "currency", currency: contract.currency })}
              </Badge>
            </div>
            {canWrite && canEditLineItems && (
              <Button size="sm" className="gap-1.5" onClick={() => setAddLineItemOpen(true)}>
                <Plus className="h-4 w-4" />
                Add Line Item
              </Button>
            )}
          </div>

          {/* Add Line Item Dialog */}
          <Dialog open={addLineItemOpen} onOpenChange={setAddLineItemOpen}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add Line Item</DialogTitle>
                <DialogDescription>Add a new line item to this contract.</DialogDescription>
              </DialogHeader>
              <form onSubmit={lineItemForm.handleSubmit(onSubmitLineItem)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="description">Description *</Label>
                  <Input
                    id="description"
                    {...lineItemForm.register("description", { required: true })}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="quantity">Quantity *</Label>
                    <Input
                      id="quantity"
                      type="number"
                      min="1"
                      step="1"
                      {...lineItemForm.register("quantity", { required: true, min: 1 })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="unit">Unit</Label>
                    <Input
                      id="unit"
                      placeholder="e.g., hours, items"
                      {...lineItemForm.register("unit")}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="unit_price">Unit Price *</Label>
                  <Input
                    id="unit_price"
                    type="number"
                    min="0"
                    step="0.01"
                    {...lineItemForm.register("unit_price", { required: true, min: 0 })}
                  />
                </div>
                <div className="p-3 bg-muted rounded-md">
                  <p className="text-sm text-muted-foreground">
                    Total:{" "}
                    <strong>
                      {(
                        (Number(lineItemForm.watch("quantity") || 0) *
                        Number(lineItemForm.watch("unit_price") || 0))
                      ).toLocaleString(undefined, { style: "currency", currency: contract.currency })}
                    </strong>
                  </p>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setAddLineItemOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={
                      addLineItem.isPending ||
                      !lineItemForm.watch("description") ||
                      !lineItemForm.watch("unit_price")
                    }
                  >
                    {addLineItem.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Adding...
                      </>
                    ) : (
                      "Add Line Item"
                    )}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Line Items Table */}
          <Card>
            <CardContent className="pt-4">
              {lineItemsLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !lineItems || lineItems.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <List className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No line items yet.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-2 pr-4 font-medium">Description</th>
                        <th className="pb-2 pr-4 font-medium">Service Type</th>
                        <th className="pb-2 pr-4 font-medium text-right">Qty</th>
                        <th className="pb-2 pr-4 font-medium text-right">Unit Price</th>
                        <th className="pb-2 font-medium text-right">Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {lineItems.map((item) => (
                        <tr key={item.id} className="border-b last:border-0">
                          <td className="py-3 pr-4 font-medium">{item.description}</td>
                          <td className="py-3 pr-4 text-muted-foreground">{item.unit ?? "—"}</td>
                          <td className="py-3 pr-4 text-right">{item.quantity}</td>
                          <td className="py-3 pr-4 text-right">
                            {item.unit_price.toLocaleString(undefined, {
                              style: "currency",
                              currency: contract.currency,
                            })}
                          </td>
                          <td className="py-3 text-right font-medium">
                            {item.total_price.toLocaleString(undefined, {
                              style: "currency",
                              currency: contract.currency,
                            })}
                          </td>
                        </tr>
                      ))}
                      <tr className="border-t-2 border-muted">
                        <td className="py-3 pr-4 font-bold" colSpan={4}>Total Contract Value</td>
                        <td className="py-3 text-right font-bold">
                          {totalValue.toLocaleString(undefined, {
                            style: "currency",
                            currency: contract.currency,
                          })}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* History Tab */}
        <TabsContent value="history" className="space-y-4">
          <h2 className="text-lg font-semibold">Contract History</h2>

          <Card>
            <CardContent className="pt-4">
              {historyLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !history || history.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <History className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No history recorded yet.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-2 pr-4 font-medium">Date</th>
                        <th className="pb-2 pr-4 font-medium">From Status</th>
                        <th className="pb-2 pr-4 font-medium">To Status</th>
                        <th className="pb-2 pr-4 font-medium">Changed By</th>
                        <th className="pb-2 font-medium">Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...history]
                        .sort(
                          (a, b) =>
                            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                        )
                        .map((entry) => (
                          <tr key={entry.id} className="border-b last:border-0">
                            <td className="py-3 pr-4 text-muted-foreground">
                              {new Date(entry.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 pr-4">
                              {entry.from_status ? (
                                <Badge variant="outline" className="text-xs capitalize">
                                  {entry.from_status.replace(/_/g, " ")}
                                </Badge>
                              ) : (
                                <span className="text-muted-foreground">—</span>
                              )}
                            </td>
                            <td className="py-3 pr-4">
                              <Badge variant="default" className="text-xs capitalize">
                                {entry.to_status.replace(/_/g, " ")}
                              </Badge>
                            </td>
                            <td className="py-3 pr-4 text-muted-foreground text-xs font-mono">
                              {entry.changed_by.slice(0, 8)}...
                            </td>
                            <td className="py-3 text-muted-foreground text-sm max-w-[200px] truncate">
                              {entry.comment ?? "—"}
                            </td>
                          </tr>
                        ))}
                    </tbody>
                  </table>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
