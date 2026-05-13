"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { HardHat, Loader2, ArrowLeft, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Skeleton } from "@/components/ui/skeleton";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { toast } from "sonner";
import { useCreateTechnician, usePlatformUsers } from "@/lib/hooks/queries/ccv";

const createTechnicianSchema = z.object({
  user_id: z.string().uuid("Please select a valid platform user"),
  first_name: z.string().min(1, "First name is required"),
  last_name: z.string().min(1, "Last name is required"),
  email: z.string().email("Valid email is required"),
  phone: z.string().optional(),
  service_area: z.string().optional(),
  specializations: z.string().optional(),
  employee_number: z.string().optional(),
});

type CreateTechnicianFormValues = z.infer<typeof createTechnicianSchema>;

export default function CreateTechnicianPage() {
  const router = useRouter();
  const [selectedUser, setSelectedUser] = useState<{ id: string; first_name: string; last_name: string; email: string } | null>(null);

  const { data: usersData, isLoading: usersLoading, error: usersError } = usePlatformUsers();
  const createTechnician = useCreateTechnician();

  const form = useForm<CreateTechnicianFormValues>({
    resolver: zodResolver(createTechnicianSchema),
    defaultValues: {
      user_id: "",
      first_name: "",
      last_name: "",
      email: "",
      phone: "",
      service_area: "",
      specializations: "",
      employee_number: "",
    },
  });

  const users = usersData?.items ?? [];

  const handleUserSelect = (userId: string) => {
    const user = users.find((u) => u.id === userId);
    if (user) {
      setSelectedUser(user);
      form.setValue("user_id", user.id);
      form.setValue("first_name", user.first_name ?? "");
      form.setValue("last_name", user.last_name ?? "");
      form.setValue("email", user.email ?? "");
    }
  };

  const onSubmit = async (values: CreateTechnicianFormValues) => {
    try {
      await createTechnician.mutateAsync({
        user_id: values.user_id,
        first_name: values.first_name.trim(),
        last_name: values.last_name.trim(),
        email: values.email.trim(),
        phone: values.phone?.trim() || undefined,
        service_area: values.service_area?.trim() || undefined,
        specializations: values.specializations
          ? values.specializations.split(",").map((s) => s.trim()).filter(Boolean)
          : [],
        employee_number: values.employee_number?.trim() || undefined,
      });
      toast.success("Technician registered successfully");
      router.push("/ccv/technicians");
    } catch (e) {
      toast.error("Failed to register technician");
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
          <HardHat className="h-6 w-6" />
          Register Technician
        </h1>
        <p className="text-muted-foreground text-sm mt-1">
          Create a new technician profile linked to a platform user
        </p>
      </div>

      {usersError && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Failed to load platform users. Please try again.
          </AlertDescription>
        </Alert>
      )}

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Technician Information</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            {/* Platform User Select */}
            <div className="space-y-2">
              <Label htmlFor="user_id">
                Platform User <span className="text-destructive">*</span>
              </Label>
              {usersLoading ? (
                <Skeleton className="h-10 w-full" />
              ) : (
                <>
                  <select
                    id="user_id"
                    className="w-full h-10 rounded-md border border-input bg-background px-3 text-sm"
                    {...form.register("user_id")}
                    onChange={(e) => handleUserSelect(e.target.value)}
                    value={form.watch("user_id")}
                  >
                    <option value="">Select a platform user...</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.first_name} {user.last_name} ({user.email})
                      </option>
                    ))}
                  </select>
                  {form.formState.errors.user_id && (
                    <p className="text-xs text-destructive">
                      {form.formState.errors.user_id.message}
                    </p>
                  )}
                  <p className="text-xs text-muted-foreground">
                    The technician must be linked to an existing platform user account.
                  </p>
                </>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="first_name">First Name *</Label>
                <Input
                  id="first_name"
                  {...form.register("first_name")}
                />
                {form.formState.errors.first_name && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.first_name.message}
                  </p>
                )}
              </div>
              <div className="space-y-2">
                <Label htmlFor="last_name">Last Name *</Label>
                <Input
                  id="last_name"
                  {...form.register("last_name")}
                />
                {form.formState.errors.last_name && (
                  <p className="text-xs text-destructive">
                    {form.formState.errors.last_name.message}
                  </p>
                )}
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email *</Label>
              <Input
                id="email"
                type="email"
                {...form.register("email")}
              />
              {form.formState.errors.email && (
                <p className="text-xs text-destructive">
                  {form.formState.errors.email.message}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input id="phone" type="tel" {...form.register("phone")} />
            </div>

            <div className="space-y-2">
              <Label htmlFor="service_area">Service Area</Label>
              <Input
                id="service_area"
                placeholder="e.g., Northeast Region"
                {...form.register("service_area")}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="specializations">Specializations</Label>
              <Input
                id="specializations"
                placeholder="Comma-separated list (e.g., HVAC, Electrical, Plumbing)"
                {...form.register("specializations")}
              />
              <p className="text-xs text-muted-foreground">
                Enter specializations separated by commas
              </p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="employee_number">Employee Number</Label>
              <Input
                id="employee_number"
                placeholder="Auto-generated if left blank"
                {...form.register("employee_number")}
              />
            </div>

            <div className="flex gap-4 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={createTechnician.isPending}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={createTechnician.isPending || !form.watch("user_id")}
              >
                {createTechnician.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    Registering...
                  </>
                ) : (
                  "Register Technician"
                )}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
