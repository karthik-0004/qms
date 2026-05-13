"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import {
  Briefcase,
  Loader2,
  Plus,
  User,
  MessageSquare,
  Calendar,
  ArrowRightLeft,
  Check,
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
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";
import {
  useCustomer,
  useCustomerContacts,
  useCustomerInteractions,
  useAddContact,
  useLogInteraction,
  useTransitionCustomerStatus,
} from "@/lib/hooks/queries/ccv";
import { usePermission } from "@/lib/hooks/usePermission";

const STATUS_CONFIG: Record<string, { label: string; color: string }> = {
  prospect: { label: "Prospect", color: "bg-blue-100 text-blue-700" },
  qualified: { label: "Qualified", color: "bg-amber-100 text-amber-700" },
  customer: { label: "Customer", color: "bg-green-100 text-green-700" },
  inactive: { label: "Inactive", color: "bg-slate-100 text-slate-500" },
  cancelled: { label: "Cancelled", color: "bg-red-100 text-red-600" },
};

const VALID_STATUS_TRANSITIONS: Record<string, string[]> = {
  prospect: ["qualified", "inactive"],
  qualified: ["customer", "inactive"],
  customer: ["inactive"],
  inactive: ["customer"],
};

const INTERACTION_TYPES = ["Call", "Email", "Meeting", "Demo", "Other"];

// Simple Zod-less validation for forms
interface ContactFormValues {
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  title: string;
  is_primary: boolean;
}

interface InteractionFormValues {
  interaction_type: string;
  subject: string;
  body: string;
  interaction_date: string;
}

export default function CustomerDetailPage() {
  const params = useParams();
  const customerId = params.id as string;
  const { hasPermission } = usePermission();
  const canWrite = hasPermission("crm:write");

  const [activeTab, setActiveTab] = useState("overview");
  const [addContactOpen, setAddContactOpen] = useState(false);
  const [logInteractionOpen, setLogInteractionOpen] = useState(false);
  const [changeStatusOpen, setChangeStatusOpen] = useState(false);

  const { data: customer, isLoading: customerLoading } = useCustomer(customerId);
  const { data: contacts, isLoading: contactsLoading } = useCustomerContacts(customerId);
  const { data: interactions, isLoading: interactionsLoading } = useCustomerInteractions(customerId);

  const addContact = useAddContact(customerId);
  const logInteraction = useLogInteraction(customerId);
  const transitionStatus = useTransitionCustomerStatus(customerId);

  const contactForm = useForm<ContactFormValues>({
    defaultValues: {
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      title: "",
      is_primary: false,
    },
  });

  const interactionForm = useForm<InteractionFormValues>({
    defaultValues: {
      interaction_type: "Call",
      subject: "",
      body: "",
      interaction_date: new Date().toISOString().split("T")[0],
    },
  });

  const statusForm = useForm<{ new_status: string }>({
    defaultValues: {
      new_status: "",
    },
  });

  const onSubmitContact = async (values: ContactFormValues) => {
    try {
      await addContact.mutateAsync({
        first_name: values.first_name.trim(),
        last_name: values.last_name.trim(),
        email: values.email.trim() || null,
        phone: values.phone.trim() || null,
        title: values.title.trim() || null,
        is_primary: values.is_primary,
      });
      setAddContactOpen(false);
      contactForm.reset();
    } catch (e) {
      toast.error("Failed to add contact");
    }
  };

  const onSubmitInteraction = async (values: InteractionFormValues) => {
    try {
      await logInteraction.mutateAsync({
        interaction_type: values.interaction_type,
        subject: values.subject.trim(),
        body: values.body.trim() || null,
      });
      setLogInteractionOpen(false);
      interactionForm.reset();
    } catch (e) {
      toast.error("Failed to log interaction");
    }
  };

  const onSubmitStatusChange = async (values: { new_status: string }) => {
    try {
      await transitionStatus.mutateAsync({ new_status: values.new_status });
      setChangeStatusOpen(false);
      statusForm.reset();
    } catch (e) {
      toast.error("Failed to update status");
    }
  };

  const validNextStatuses = customer
    ? VALID_STATUS_TRANSITIONS[customer.status] || []
    : [];

  if (customerLoading) {
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

  if (!customer) {
    return (
      <div className="space-y-6 p-6 max-w-7xl mx-auto">
        <p className="text-muted-foreground">Customer not found.</p>
      </div>
    );
  }

  const statusCfg = STATUS_CONFIG[customer.status] ?? { label: customer.status, color: "" };

  return (
    <div className="space-y-6 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
            <Briefcase className="h-6 w-6" />
            {customer.company_name}
          </h1>
          <div className="flex items-center gap-2 mt-2">
            <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${statusCfg.color}`}>
              {statusCfg.label}
            </span>
            {customer.industry && (
              <span className="text-muted-foreground text-sm">{customer.industry}</span>
            )}
          </div>
        </div>
        {canWrite && validNextStatuses.length > 0 && (
          <Button
            variant="outline"
            size="sm"
            className="gap-1.5"
            onClick={() => setChangeStatusOpen(true)}
          >
            <ArrowRightLeft className="h-4 w-4" />
            Change Status
          </Button>
        )}
      </div>

      {/* Status Change Dialog */}
      <Dialog open={changeStatusOpen} onOpenChange={setChangeStatusOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Change Customer Status</DialogTitle>
            <DialogDescription>
              Current status: <strong>{statusCfg.label}</strong>
            </DialogDescription>
          </DialogHeader>
          <form onSubmit={statusForm.handleSubmit(onSubmitStatusChange)} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="new_status">New Status</Label>
              <select
                id="new_status"
                className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
                {...statusForm.register("new_status")}
              >
                <option value="">Select status...</option>
                {validNextStatuses.map((status) => (
                  <option key={status} value={status}>
                    {STATUS_CONFIG[status]?.label || status}
                  </option>
                ))}
              </select>
            </div>
            <DialogFooter>
              <Button type="button" variant="outline" onClick={() => setChangeStatusOpen(false)}>
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={transitionStatus.isPending || !statusForm.watch("new_status")}
              >
                {transitionStatus.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Updating...
                  </>
                ) : (
                  "Update Status"
                )}
              </Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="contacts">
            <User className="h-4 w-4 mr-1" />
            Contacts
          </TabsTrigger>
          <TabsTrigger value="interactions">
            <MessageSquare className="h-4 w-4 mr-1" />
            Interactions
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Company Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm text-muted-foreground">Email</p>
                  <p className="text-sm font-medium">{customer.email ?? "—"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Phone</p>
                  <p className="text-sm font-medium">{customer.phone ?? "—"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Website</p>
                  <p className="text-sm font-medium">{customer.website ?? "—"}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Industry</p>
                  <p className="text-sm font-medium">{customer.industry ?? "—"}</p>
                </div>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Address</p>
                <p className="text-sm font-medium">
                  {customer.address
                    ? `${customer.address}${customer.city ? `, ${customer.city}` : ""}${
                        customer.state ? `, ${customer.state}` : ""
                      }${customer.country ? `, ${customer.country}` : ""} ${
                        customer.postal_code ?? ""
                      }`
                    : "—"}
                </p>
              </div>
              {customer.notes && (
                <div>
                  <p className="text-sm text-muted-foreground">Notes</p>
                  <p className="text-sm font-medium">{customer.notes}</p>
                </div>
              )}
              {customer.tags && customer.tags.length > 0 && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Tags</p>
                  <div className="flex flex-wrap gap-1">
                    {customer.tags.map((tag: string) => (
                      <Badge key={tag} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Contacts Tab */}
        <TabsContent value="contacts" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Contacts</h2>
            {canWrite && (
              <Button size="sm" className="gap-1.5" onClick={() => setAddContactOpen(true)}>
                <Plus className="h-4 w-4" />
                Add Contact
              </Button>
            )}
          </div>

          {/* Add Contact Dialog */}
          <Dialog open={addContactOpen} onOpenChange={setAddContactOpen}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Add Contact</DialogTitle>
                <DialogDescription>Add a new contact to this customer.</DialogDescription>
              </DialogHeader>
              <form onSubmit={contactForm.handleSubmit(onSubmitContact)} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="first_name">First Name *</Label>
                    <Input
                      id="first_name"
                      {...contactForm.register("first_name", { required: true })}
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="last_name">Last Name *</Label>
                    <Input
                      id="last_name"
                      {...contactForm.register("last_name", { required: true })}
                    />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" {...contactForm.register("email")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="phone">Phone</Label>
                  <Input id="phone" type="tel" {...contactForm.register("phone")} />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="title">Job Title</Label>
                  <Input id="title" {...contactForm.register("title")} />
                </div>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="is_primary"
                    checked={contactForm.watch("is_primary")}
                    onCheckedChange={(checked) =>
                      contactForm.setValue("is_primary", checked as boolean)
                    }
                  />
                  <Label htmlFor="is_primary" className="text-sm font-normal">
                    Primary Contact
                  </Label>
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setAddContactOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={
                      addContact.isPending ||
                      !contactForm.watch("first_name") ||
                      !contactForm.watch("last_name")
                    }
                  >
                    {addContact.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Adding...
                      </>
                    ) : (
                      "Add Contact"
                    )}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Contacts Table */}
          <Card>
            <CardContent className="pt-4">
              {contactsLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !contacts || contacts.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <User className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No contacts yet. Add the first contact.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-2 pr-4 font-medium">Name</th>
                        <th className="pb-2 pr-4 font-medium">Email</th>
                        <th className="pb-2 pr-4 font-medium">Phone</th>
                        <th className="pb-2 pr-4 font-medium">Job Title</th>
                        <th className="pb-2 font-medium">Primary</th>
                      </tr>
                    </thead>
                    <tbody>
                      {contacts.map((contact) => (
                        <tr key={contact.id} className="border-b last:border-0">
                          <td className="py-3 pr-4 font-medium">
                            {contact.first_name} {contact.last_name}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground">
                            {contact.email ?? "—"}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground">
                            {contact.phone ?? contact.mobile ?? "—"}
                          </td>
                          <td className="py-3 pr-4 text-muted-foreground">
                            {contact.title ?? "—"}
                          </td>
                          <td className="py-3">
                            {contact.is_primary && (
                              <Badge variant="default" className="text-xs">
                                <Check className="h-3 w-3 mr-1" />
                                Primary
                              </Badge>
                            )}
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

        {/* Interactions Tab */}
        <TabsContent value="interactions" className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold">Interactions</h2>
            {canWrite && (
              <Button size="sm" className="gap-1.5" onClick={() => setLogInteractionOpen(true)}>
                <Plus className="h-4 w-4" />
                Log Interaction
              </Button>
            )}
          </div>

          {/* Log Interaction Dialog */}
          <Dialog open={logInteractionOpen} onOpenChange={setLogInteractionOpen}>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>Log Interaction</DialogTitle>
                <DialogDescription>Record a new interaction with this customer.</DialogDescription>
              </DialogHeader>
              <form onSubmit={interactionForm.handleSubmit(onSubmitInteraction)} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="interaction_type">Interaction Type *</Label>
                  <select
                    id="interaction_type"
                    className="w-full h-9 rounded-md border border-input bg-background px-3 text-sm"
                    {...interactionForm.register("interaction_type")}
                  >
                    {INTERACTION_TYPES.map((type) => (
                      <option key={type} value={type}>
                        {type}
                      </option>
                    ))}
                  </select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="subject">Subject *</Label>
                  <Input
                    id="subject"
                    {...interactionForm.register("subject", { required: true })}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="interaction_date">Date</Label>
                  <Input
                    id="interaction_date"
                    type="date"
                    {...interactionForm.register("interaction_date")}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="body">Notes</Label>
                  <textarea
                    id="body"
                    className="w-full min-h-[80px] rounded-md border border-input bg-background px-3 py-2 text-sm"
                    {...interactionForm.register("body")}
                  />
                </div>
                <DialogFooter>
                  <Button type="button" variant="outline" onClick={() => setLogInteractionOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    type="submit"
                    disabled={logInteraction.isPending || !interactionForm.watch("subject")}
                  >
                    {logInteraction.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin mr-2" />
                        Saving...
                      </>
                    ) : (
                      "Log Interaction"
                    )}
                  </Button>
                </DialogFooter>
              </form>
            </DialogContent>
          </Dialog>

          {/* Interactions Table */}
          <Card>
            <CardContent className="pt-4">
              {interactionsLoading ? (
                <div className="space-y-2">
                  {Array.from({ length: 3 }).map((_, i) => (
                    <Skeleton key={i} className="h-12 w-full" />
                  ))}
                </div>
              ) : !interactions || interactions.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <MessageSquare className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>No interactions logged yet.</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b text-left text-muted-foreground">
                        <th className="pb-2 pr-4 font-medium">Date</th>
                        <th className="pb-2 pr-4 font-medium">Type</th>
                        <th className="pb-2 pr-4 font-medium">Subject</th>
                        <th className="pb-2 pr-4 font-medium">Logged By</th>
                        <th className="pb-2 font-medium">Notes</th>
                      </tr>
                    </thead>
                    <tbody>
                      {[...interactions]
                        .sort(
                          (a, b) =>
                            new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
                        )
                        .map((interaction) => (
                          <tr key={interaction.id} className="border-b last:border-0">
                            <td className="py-3 pr-4 text-muted-foreground">
                              {new Date(interaction.created_at).toLocaleDateString()}
                            </td>
                            <td className="py-3 pr-4">
                              <Badge variant="outline" className="text-xs capitalize">
                                {interaction.interaction_type}
                              </Badge>
                            </td>
                            <td className="py-3 pr-4 font-medium">{interaction.subject}</td>
                            <td className="py-3 pr-4 text-muted-foreground text-xs">
                              {interaction.created_by.slice(0, 8)}...
                            </td>
                            <td className="py-3 text-muted-foreground text-sm max-w-[200px] truncate">
                              {interaction.body ?? "—"}
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
