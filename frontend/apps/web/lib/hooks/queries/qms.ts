"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsApi, qualityEventsApi, capaApi, trainingApi, equipmentApi } from "@/lib/api/services/qms";

// ─── Documents ──────────────────────────────────────────────────────────────

export function useDocuments(params?: Parameters<typeof documentsApi.list>[0]) {
  return useQuery({
    queryKey: ["documents", params],
    queryFn: () => documentsApi.list(params),
    staleTime: 30_000,
  });
}

export function useDocument(id: string) {
  return useQuery({
    queryKey: ["documents", id],
    queryFn: () => documentsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: documentsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["documents"] }),
  });
}

// ─── Quality Events ─────────────────────────────────────────────────────────

export function useQualityEvents(params?: Parameters<typeof qualityEventsApi.list>[0]) {
  return useQuery({
    queryKey: ["quality-events", params],
    queryFn: () => qualityEventsApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateQualityEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: qualityEventsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["quality-events"] }),
  });
}

// ─── CAPA ───────────────────────────────────────────────────────────────────

export function useCAPAs(params?: Parameters<typeof capaApi.list>[0]) {
  return useQuery({
    queryKey: ["capas", params],
    queryFn: () => capaApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateCAPA() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: capaApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["capas"] }),
  });
}

// ─── Training ───────────────────────────────────────────────────────────────

export function useCourses(params?: Parameters<typeof trainingApi.list>[0]) {
  return useQuery({
    queryKey: ["courses", params],
    queryFn: () => trainingApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateCourse() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: trainingApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["courses"] }),
  });
}

// ─── Equipment ──────────────────────────────────────────────────────────────

export function useEquipment(params?: Parameters<typeof equipmentApi.list>[0]) {
  return useQuery({
    queryKey: ["equipment", params],
    queryFn: () => equipmentApi.list(params),
    staleTime: 30_000,
  });
}

export function useCreateEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: equipmentApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["equipment"] }),
  });
}
