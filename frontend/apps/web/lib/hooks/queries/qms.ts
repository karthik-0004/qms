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

export function useDocumentVersions(documentId: string) {
  return useQuery({
    queryKey: ["documents", documentId, "versions"],
    queryFn: () => documentsApi.getVersions(documentId),
    enabled: !!documentId,
  });
}

export function useDocumentDistribution(documentId: string) {
  return useQuery({
    queryKey: ["documents", documentId, "distribution"],
    queryFn: () => documentsApi.listDistribution(documentId),
    enabled: !!documentId,
  });
}

export function useDocumentsDueForReview(params?: { days_ahead?: number }) {
  return useQuery({
    queryKey: ["documents", "due-for-review", params],
    queryFn: () => documentsApi.dueForReview(params),
    staleTime: 60_000,
  });
}

export function useUpdateDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof documentsApi.update>[1] }) =>
      documentsApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["documents", variables.id] });
    },
  });
}

export function useRejectDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => documentsApi.reject(id, { reason }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["documents", variables.id] });
    },
  });
}

export function useMakeDocumentObsolete() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.makeObsolete(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["documents", id] });
    },
  });
}

export function useApproveDocument() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: Parameters<typeof documentsApi.approve>[1];
    }) => documentsApi.approve(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["documents", variables.id] });
      qc.invalidateQueries({ queryKey: ["documents", variables.id, "versions"] });
    },
  });
}

export function useAddDistributionMember() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, user_id }: { id: string; user_id: string }) =>
      documentsApi.addDistributionMember(id, { user_id }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["documents", variables.id, "distribution"] });
    },
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

export function useQualityEvent(id: string) {
  return useQuery({
    queryKey: ["quality-events", id],
    queryFn: () => qualityEventsApi.get(id),
    enabled: !!id,
  });
}

export function useQualityEventsSummary() {
  return useQuery({
    queryKey: ["quality-events", "summary"],
    queryFn: () => qualityEventsApi.summary(),
    staleTime: 60_000,
  });
}

export function useUpdateQualityEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) => qualityEventsApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["quality-events"] });
      qc.invalidateQueries({ queryKey: ["quality-events", variables.id] });
    },
  });
}

export function useCloseQualityEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, resolution }: { id: string; resolution?: string | null }) =>
      qualityEventsApi.close(id, { resolution }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["quality-events"] });
      qc.invalidateQueries({ queryKey: ["quality-events", variables.id] });
    },
  });
}

export function useDeleteQualityEvent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => qualityEventsApi.delete(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["quality-events"] });
      qc.invalidateQueries({ queryKey: ["quality-events", id] });
    },
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

export function useCAPA(id: string) {
  return useQuery({
    queryKey: ["capas", id],
    queryFn: () => capaApi.get(id),
    enabled: !!id,
  });
}

export function useCAPAActions(capaId: string) {
  return useQuery({
    queryKey: ["capas", capaId, "actions"],
    queryFn: () => capaApi.listActions(capaId),
    enabled: !!capaId,
  });
}

export function useUpdateCAPA() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof capaApi.update>[1] }) => capaApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["capas"] });
      qc.invalidateQueries({ queryKey: ["capas", variables.id] });
    },
  });
}

export function useCloseCAPA() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => capaApi.close(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["capas"] });
      qc.invalidateQueries({ queryKey: ["capas", id] });
    },
  });
}

export function useDeleteCAPA() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => capaApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["capas"] });
    },
  });
}

export function useVerifyCapaEffectiveness() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { verified: boolean; notes?: string | null } }) =>
      capaApi.verifyEffectiveness(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["capas", variables.id] });
    },
  });
}

export function useAddCapaAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      capaId,
      data,
    }: {
      capaId: string;
      data: { action_type: string; description: string; assigned_to?: string | null; due_date?: string | null };
    }) => capaApi.addAction(capaId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["capas", variables.capaId, "actions"] });
    },
  });
}

export function useCompleteCapaAction() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      capaId,
      actionId,
      data,
    }: {
      capaId: string;
      actionId: string;
      data?: { evidence?: string | null };
    }) => capaApi.completeAction(capaId, actionId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["capas", variables.capaId, "actions"] });
    },
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

export function useCourse(id: string) {
  return useQuery({
    queryKey: ["courses", id],
    queryFn: () => trainingApi.get(id),
    enabled: !!id,
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

export function useEquipmentItem(id: string) {
  return useQuery({
    queryKey: ["equipment", id],
    queryFn: () => equipmentApi.get(id),
    enabled: !!id,
  });
}

export function useEquipmentDueCalibration() {
  return useQuery({
    queryKey: ["equipment", "due-for-calibration"],
    queryFn: () => equipmentApi.dueForCalibration(),
    staleTime: 60_000,
  });
}

export function useCalibrateEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      id,
      data,
    }: {
      id: string;
      data: { calibration_date: string; passed: boolean; certificate_file_id?: string | null; notes?: string | null };
    }) => equipmentApi.calibrate(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["equipment"] });
      qc.invalidateQueries({ queryKey: ["equipment", variables.id] });
      qc.invalidateQueries({ queryKey: ["equipment", "due-for-calibration"] });
    },
  });
}

export function useDecommissionEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, reason }: { id: string; reason: string }) => equipmentApi.decommission(id, { reason }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["equipment"] });
      qc.invalidateQueries({ queryKey: ["equipment", variables.id] });
    },
  });
}

export function useUpdateEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof equipmentApi.update>[1] }) =>
      equipmentApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["equipment"] });
      qc.invalidateQueries({ queryKey: ["equipment", variables.id] });
    },
  });
}

export function useDeleteEquipment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => equipmentApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["equipment"] });
    },
  });
}

export function useMyTrainingAssignments(params?: Parameters<typeof trainingApi.listMyAssignments>[0]) {
  return useQuery({
    queryKey: ["training", "my-assignments", params],
    queryFn: () => trainingApi.listMyAssignments(params),
    staleTime: 30_000,
  });
}

export function useCompleteTrainingAssignment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      assignmentId,
      data,
    }: {
      assignmentId: string;
      data: { score?: number | null; notes?: string | null; e_signature?: string | null };
    }) => trainingApi.completeAssignment(assignmentId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["training", "my-assignments"] });
      qc.invalidateQueries({ queryKey: ["training", "overdue"] });
    },
  });
}

export function useTrainingOverdueAssignments() {
  return useQuery({
    queryKey: ["training", "overdue"],
    queryFn: () => trainingApi.listOverdueAssignments(),
    staleTime: 60_000,
  });
}
