"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import {
  customersApi, contractsApi, workOrdersApi,
  techniciansApi, invoicesApi, certificatesApi,
  type CreateContactRequest, type CreateInteractionRequest,
  type CreateLineItemRequest,
} from "@/lib/api/services/ccv";
import { usersApi } from "@/lib/api/services/platform";

// ─── Customers ──────────────────────────────────────────────────────────────

export function useCustomers(params?: Parameters<typeof customersApi.list>[0]) {
  return useQuery({
    queryKey: ["customers", params],
    queryFn: () => customersApi.list(params),
    staleTime: 30_000,
  });
}

export function useCustomer(id: string) {
  return useQuery({
    queryKey: ["customers", id],
    queryFn: () => customersApi.get(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}

export function useCreateCustomer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: customersApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["customers"] }),
  });
}

export function useCustomerContacts(customerId: string) {
  return useQuery({
    queryKey: ["customers", customerId, "contacts"],
    queryFn: () => customersApi.listContacts(customerId),
    enabled: !!customerId,
  });
}

export function useCustomerInteractions(customerId: string) {
  return useQuery({
    queryKey: ["customers", customerId, "interactions"],
    queryFn: () => customersApi.listInteractions(customerId),
    enabled: !!customerId,
  });
}

export function useAddContact(customerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateContactRequest) =>
      customersApi.addContact(customerId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["customers", customerId, "contacts"],
      });
      toast.success("Contact added");
    },
    onError: () => toast.error("Failed to add contact"),
  });
}

export function useLogInteraction(customerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateInteractionRequest) =>
      customersApi.logInteraction(customerId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["customers", customerId, "interactions"],
      });
      toast.success("Interaction logged");
    },
    onError: () => toast.error("Failed to log interaction"),
  });
}

export function useTransitionCustomerStatus(customerId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: { new_status: string }) =>
      customersApi.transitionStatus(customerId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["customers", customerId] });
      queryClient.invalidateQueries({ queryKey: ["customers"] });
      toast.success("Customer status updated");
    },
    onError: () => toast.error("Failed to update customer status"),
  });
}

// ─── Contracts ──────────────────────────────────────────────────────────────

export function useContracts(params?: Parameters<typeof contractsApi.list>[0]) {
  return useQuery({
    queryKey: ["contracts", params],
    queryFn: () => contractsApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateContract() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: contractsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["contracts"] }),
  });
}

export function useContract(id: string) {
  return useQuery({
    queryKey: ["contracts", id],
    queryFn: () => contractsApi.get(id),
    enabled: !!id,
    staleTime: 30_000,
  });
}

export function useContractLineItems(contractId: string) {
  return useQuery({
    queryKey: ["contracts", contractId, "line-items"],
    queryFn: () => contractsApi.listLineItems(contractId),
    enabled: !!contractId,
  });
}

export function useContractHistory(contractId: string) {
  return useQuery({
    queryKey: ["contracts", contractId, "history"],
    queryFn: () => contractsApi.getHistory(contractId),
    enabled: !!contractId,
  });
}

export function useAddLineItem(contractId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: CreateLineItemRequest) => contractsApi.addLineItem(contractId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["contracts", contractId, "line-items"] });
      toast.success("Line item added");
    },
    onError: () => toast.error("Failed to add line item"),
  });
}

// ─── Work Orders ────────────────────────────────────────────────────────────

export function useWorkOrders(params?: Parameters<typeof workOrdersApi.list>[0]) {
  return useQuery({
    queryKey: ["work-orders", params],
    queryFn: () => workOrdersApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateWorkOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: workOrdersApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["work-orders"] }),
  });
}

export function useAssignWorkOrder() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { technician_id: string } }) =>
      workOrdersApi.assign(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["work-orders"] }),
  });
}

// ─── Technicians ────────────────────────────────────────────────────────────

export function useTechnicians(params?: Parameters<typeof techniciansApi.list>[0]) {
  return useQuery({
    queryKey: ["technicians", params],
    queryFn: () => techniciansApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateTechnician() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: techniciansApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["technicians"] }),
  });
}

// ─── Invoices ───────────────────────────────────────────────────────────────

export function useInvoices(params?: Parameters<typeof invoicesApi.list>[0]) {
  return useQuery({
    queryKey: ["invoices", params],
    queryFn: () => invoicesApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateInvoice() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: invoicesApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["invoices"] }),
  });
}

export function useRecordPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { amount: number; payment_method: string; reference?: string } }) =>
      invoicesApi.recordPayment(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["invoices"] }),
  });
}

// ─── Certificates ───────────────────────────────────────────────────────────

export function useCertificates(params?: Parameters<typeof certificatesApi.list>[0]) {
  return useQuery({
    queryKey: ["certificates", params],
    queryFn: () => certificatesApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateCertificate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: certificatesApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["certificates"] }),
  });
}

// ─── Platform Users ─────────────────────────────────────────────────────────

export function usePlatformUsers() {
  return useQuery({
    queryKey: ["platform-users"],
    queryFn: () => usersApi.list(),
    staleTime: 30_000,
  });
}
