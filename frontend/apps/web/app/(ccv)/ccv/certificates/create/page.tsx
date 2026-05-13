"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Shield, Loader2, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { toast } from "sonner";
import { useCreateCertificate } from "@/lib/hooks/queries/ccv";
import { useCustomers } from "@/lib/hooks/queries/ccv";

const createCertificateSchema = z.object({
  title: z.string().min(1, "Title is required"),
  certificate_number: z.string().min(1, "Certificate number is required"),
  certificate_type: z.string().min(1, "Certificate type is required"),
  customer_id: z.string().uuid("Please select a valid customer"),
  issue_date: z.string().min(1, "Issue date is required"),
  expiry_date: z.string().optional(),
  description: z.string().optional(),
});

type CreateCertificateFormValues = z.infer<typeof createCertificateSchema>;

export default function CreateCertificatePage() {
  const router = useRouter();
  const createCertificate = useCreateCertificate();
  const { data: customersData, isLoading: customersLoading } = useCustomers();

  const form = useForm<CreateCertificateFormValues>({
    resolver: zodResolver(createCertificateSchema),
    defaultValues: {
      title: "",
      certificate_number: "",
      certificate_type: "",
      customer_id: "",
      issue_date: new Date().toISOString().split('T')[0],
      expiry_date: "",
      description: "",
    },
  });

  const customers = customersData?.items ?? [];

  const onSubmit = async (values: CreateCertificateFormValues) => {
    try {
      await createCertificate.mutateAsync({
        title: values.title.trim(),
        certificate_number: values.certificate_number.trim(),
        certificate_type: values.certificate_type.trim(),
        customer_id: values.customer_id,
        issue_date: values.issue_date,
        expiry_date: values.expiry_date || undefined,
        description: values.description?.trim() || undefined,
      });
      toast.success("Certificate created successfully");
      router.push("/ccv/certificates");
    } catch (e) {
      toast.error("Failed to create certificate");
    }
  };

  return (
    <div className="space-y-6 p-6 max-w-3xl mx-auto">
      <div className="flex items-center gap-2">
        <Button variant="ghost" size="sm" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4 mr-1" />
          Back
        </Button>
      </div>

      <div>
        <h1 className="text-2xl font-bold tracking-tight flex items-center gap-2">
          <Shield className="h-6 w-6" />
          New Certificate
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Create a new calibration, qualification, or compliance certificate
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Certificate Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="customer_id">
                Customer <span className="text-destructive">*</span>
              </Label>
              {customersLoading ? (
                <div className="h-10 w-full bg-muted animate-pulse rounded-md" />
              ) : (
                <>
                  <select
                    id="customer_id"
                    className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                    {...form.register("customer_id")}
                  >
                    <option value="">Select a customer...</option>
                    {customers.map((customer) => (
                      <option key={customer.id} value={customer.id}>
                        {customer.company_name}
                      </option>
                    ))}
                  </select>
                  {form.formState.errors.customer_id && (
                    <p className="text-xs text-destructive">
                      {form.formState.errors.customer_id.message}
                    </p>
                  )}
                </>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="certificate_number">Certificate Number *</Label>
                <Input
                  id="certificate_number"
                  placeholder="e.g., CAL-2024-001"
                  {...form.register("certificate_number")}
                />
                {form.formState.errors.certificate_number && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.certificate_number.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="certificate_type">Certificate Type *</Label>
                <select
                  id="certificate_type"
                  className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                  {...form.register("certificate_type")}
                >
                  <option value="">Select type...</option>
                  <option value="calibration">Calibration</option>
                  <option value="qualification">Qualification</option>
                  <option value="compliance">Compliance</option>
                  <option value="training">Training</option>
                </select>
                {form.formState.errors.certificate_type && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.certificate_type.message}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                placeholder="e.g., Annual Equipment Calibration"
                {...form.register("title")}
              />
              {form.formState.errors.title && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.title.message}
                </p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="issue_date">Issue Date *</Label>
                <Input
                  id="issue_date"
                  type="date"
                  {...form.register("issue_date")}
                />
                {form.formState.errors.issue_date && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.issue_date.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="expiry_date">Expiry Date</Label>
                <Input
                  id="expiry_date"
                  type="date"
                  {...form.register("expiry_date")}
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                placeholder="Additional details about the certificate..."
                className="min-h-[100px]"
                {...form.register("description")}
              />
            </div>

            <div className="flex gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={createCertificate.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createCertificate.isPending}
              >
                {createCertificate.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Creating...
                  </>
                ) : (
                  "Create Certificate"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
