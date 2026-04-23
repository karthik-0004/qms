"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { platesApi, imagesApi, aiRunsApi, jobsApi, qaReviewsApi } from "@/lib/api/services/em";

// ─── Plates ─────────────────────────────────────────────────────────────────

export function usePlates(params?: Parameters<typeof platesApi.list>[0]) {
  return useQuery({
    queryKey: ["plates", params],
    queryFn: () => platesApi.list(params),
    staleTime: 30_000,
  });
}

export function usePlate(id: string) {
  return useQuery({
    queryKey: ["plates", id],
    queryFn: () => platesApi.get(id),
    enabled: !!id,
  });
}

export function useRegisterPlate() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: platesApi.register,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["plates"] }),
  });
}

// ─── Images ─────────────────────────────────────────────────────────────────

export function usePlateImages(plateId: string) {
  return useQuery({
    queryKey: ["plate-images", plateId],
    queryFn: () => imagesApi.listByPlate(plateId),
    enabled: !!plateId,
  });
}

// ─── AI Runs ────────────────────────────────────────────────────────────────

export function usePlateAIRuns(plateId: string) {
  return useQuery({
    queryKey: ["ai-runs", plateId],
    queryFn: () => aiRunsApi.listByPlate(plateId),
    enabled: !!plateId,
  });
}

export function useStartAIRun() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: aiRunsApi.start,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["ai-runs"] }),
  });
}

// ─── Jobs ───────────────────────────────────────────────────────────────────

export function useJobs(params?: Parameters<typeof jobsApi.list>[0]) {
  return useQuery({
    queryKey: ["jobs", params],
    queryFn: () => jobsApi.list(params),
    staleTime: 15_000,
  });
}

export function useEnqueueJob() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: jobsApi.enqueue,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["jobs"] }),
  });
}

// ─── QA Reviews ─────────────────────────────────────────────────────────────

export function usePlateQAReviews(plateId: string) {
  return useQuery({
    queryKey: ["qa-reviews", plateId],
    queryFn: () => qaReviewsApi.listByPlate(plateId),
    enabled: !!plateId,
  });
}

export function useApproveReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { comments?: string } }) =>
      qaReviewsApi.approve(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["qa-reviews"] }),
  });
}

export function useRejectReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: { comments: string; override_colony_count?: number } }) =>
      qaReviewsApi.reject(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["qa-reviews"] }),
  });
}
