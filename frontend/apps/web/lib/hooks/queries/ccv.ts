"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  customersApi, contractsApi, workOrdersApi,
  techniciansApi, invoicesApi, certificatesApi,
} from "@/lib/api/services/ccv";

// ─── Customers ──────────────────────────────────────────────────────────────

export function useCustomers(params?: Parameters<typeof customersApi.list>[0]) {
  return useQuery({
    queryKey: ["customers", params],
    queryFn: () => customersApi.list(params),
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
