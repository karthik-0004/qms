"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { documentsApi, qualityEventsApi, capaApi, trainingApi, equipmentApi, auditApi, complaintsApi, riskApi, managementReviewApi, envMonitoringApi, ptApi } from "@/lib/api/services/qms";

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

export function useMakeDocumentEffective() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.makeEffective(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["documents"] });
      qc.invalidateQueries({ queryKey: ["documents", id] });
    },
  });
}

export function useMakeDocumentSuperseded() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => documentsApi.makeSuperseded(id),
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

export function useEquipmentCalibrations(equipmentId: string) {
  return useQuery({
    queryKey: ["equipment", equipmentId, "calibrations"],
    queryFn: () => equipmentApi.listCalibrations(equipmentId),
    enabled: !!equipmentId,
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

// ── Phase 4: Dashboard ──────────────────────────────────────────────────────

export function useTrainingDashboardStats() {
  return useQuery({
    queryKey: ["training", "dashboard"],
    queryFn: () => trainingApi.dashboardStats(),
    staleTime: 60_000,
  });
}

// ── Phase 4: Job Codes ──────────────────────────────────────────────────────

export function useJobCodes(params?: Parameters<typeof trainingApi.listJobCodes>[0]) {
  return useQuery({
    queryKey: ["training", "job-codes", params],
    queryFn: () => trainingApi.listJobCodes(params),
    staleTime: 30_000,
  });
}

export function useJobCode(id: string) {
  return useQuery({
    queryKey: ["training", "job-codes", id],
    queryFn: () => trainingApi.getJobCode(id),
    enabled: !!id,
  });
}

export function useCreateJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: trainingApi.createJobCode,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training", "job-codes"] }),
  });
}

export function useUpdateJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof trainingApi.updateJobCode>[1] }) =>
      trainingApi.updateJobCode(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["training", "job-codes"] });
      qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.id] });
    },
  });
}

export function useDeleteJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => trainingApi.deleteJobCode(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training", "job-codes"] }),
  });
}

export function useJobCodeCourses(jobCodeId: string) {
  return useQuery({
    queryKey: ["training", "job-codes", jobCodeId, "courses"],
    queryFn: () => trainingApi.getJobCodeCourses(jobCodeId),
    enabled: !!jobCodeId,
  });
}

export function useLinkCourseToJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ jobCodeId, data }: { jobCodeId: string; data: Parameters<typeof trainingApi.linkCourseToJobCode>[1] }) =>
      trainingApi.linkCourseToJobCode(jobCodeId, data),
    onSuccess: (_, variables) => qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.jobCodeId, "courses"] }),
  });
}

export function useUnlinkCourseFromJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ jobCodeId, courseId }: { jobCodeId: string; courseId: string }) =>
      trainingApi.unlinkCourseFromJobCode(jobCodeId, courseId),
    onSuccess: (_, variables) => qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.jobCodeId, "courses"] }),
  });
}

export function useJobCodeAssignees(jobCodeId: string) {
  return useQuery({
    queryKey: ["training", "job-codes", jobCodeId, "assignees"],
    queryFn: () => trainingApi.getJobCodeAssignees(jobCodeId),
    enabled: !!jobCodeId,
  });
}

export function useAssignUserToJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ jobCodeId, data }: { jobCodeId: string; data: Parameters<typeof trainingApi.assignUserToJobCode>[1] }) =>
      trainingApi.assignUserToJobCode(jobCodeId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.jobCodeId, "assignees"] });
      qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.jobCodeId, "status"] });
    },
  });
}

export function useUnassignUserFromJobCode() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ jobCodeId, userId }: { jobCodeId: string; userId: string }) =>
      trainingApi.unassignUserFromJobCode(jobCodeId, userId),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.jobCodeId, "assignees"] });
      qc.invalidateQueries({ queryKey: ["training", "job-codes", variables.jobCodeId, "status"] });
    },
  });
}

export function useJobCodeStatusMatrix(jobCodeId: string) {
  return useQuery({
    queryKey: ["training", "job-codes", jobCodeId, "status"],
    queryFn: () => trainingApi.getJobCodeStatusMatrix(jobCodeId),
    enabled: !!jobCodeId,
    refetchInterval: 30_000,
  });
}

// ── Phase 4: Trainers ────────────────────────────────────────────────────────

export function useTrainers(params?: Parameters<typeof trainingApi.listTrainers>[0]) {
  return useQuery({
    queryKey: ["training", "trainers", params],
    queryFn: () => trainingApi.listTrainers(params),
    staleTime: 30_000,
  });
}

export function useCreateTrainer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: trainingApi.createTrainer,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training", "trainers"] }),
  });
}

export function useUpdateTrainer() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof trainingApi.updateTrainer>[1] }) =>
      trainingApi.updateTrainer(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training", "trainers"] }),
  });
}

// ── Phase 4: Exams ───────────────────────────────────────────────────────────

export function useExams(params?: Parameters<typeof trainingApi.listExams>[0]) {
  return useQuery({
    queryKey: ["training", "exams", params],
    queryFn: () => trainingApi.listExams(params),
    staleTime: 30_000,
  });
}

export function useExam(id: string) {
  return useQuery({
    queryKey: ["training", "exams", id],
    queryFn: () => trainingApi.getExam(id),
    enabled: !!id,
  });
}

export function useCreateExam() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: trainingApi.createExam,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["training", "exams"] }),
  });
}

export function useAddExamQuestion() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ examId, data }: { examId: string; data: Parameters<typeof trainingApi.addExamQuestion>[1] }) =>
      trainingApi.addExamQuestion(examId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["training", "exams", variables.examId] });
      qc.invalidateQueries({ queryKey: ["training", "exams", variables.examId, "questions"] });
    },
  });
}

export function useExamQuestions(examId: string) {
  return useQuery({
    queryKey: ["training", "exams", examId, "questions"],
    queryFn: () => trainingApi.listExamQuestions(examId),
    enabled: !!examId,
  });
}

export function useStartExamAttempt() {
  return useMutation({
    mutationFn: (examId: string) => trainingApi.startExamAttempt(examId),
  });
}

export function useSubmitExamAttempt() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ attemptId, data }: { attemptId: string; data: { answers: Record<string, string> } }) =>
      trainingApi.submitExamAttempt(attemptId, data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["training", "my-exam-attempts"] });
      qc.invalidateQueries({ queryKey: ["training", "dashboard"] });
    },
  });
}

export function useMyExamAttempts() {
  return useQuery({
    queryKey: ["training", "my-exam-attempts"],
    queryFn: () => trainingApi.listMyExamAttempts(),
    staleTime: 15_000,
  });
}

// ─── Audit Management ────────────────────────────────────────────────────────

export function useAudits(params?: Parameters<typeof auditApi.list>[0]) {
  return useQuery({
    queryKey: ["audits", params],
    queryFn: () => auditApi.list(params),
    staleTime: 30_000,
  });
}

export function useAudit(id: string) {
  return useQuery({
    queryKey: ["audits", id],
    queryFn: () => auditApi.get(id),
    enabled: !!id,
  });
}

export function useCreateAudit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: auditApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["audits"] }),
  });
}

export function useUpdateAudit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof auditApi.update>[1] }) =>
      auditApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["audits"] });
      qc.invalidateQueries({ queryKey: ["audits", variables.id] });
    },
  });
}

export function useStartAudit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => auditApi.start(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["audits"] });
      qc.invalidateQueries({ queryKey: ["audits", id] });
    },
  });
}

export function useCompleteAudit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, summary }: { id: string; summary?: string }) => auditApi.complete(id, summary),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["audits"] });
      qc.invalidateQueries({ queryKey: ["audits", variables.id] });
    },
  });
}

export function useDeleteAudit() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => auditApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["audits"] }),
  });
}

export function useAuditFindings(auditId: string) {
  return useQuery({
    queryKey: ["audits", auditId, "findings"],
    queryFn: () => auditApi.listFindings(auditId),
    enabled: !!auditId,
  });
}

export function useAddAuditFinding() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({
      auditId,
      data,
    }: {
      auditId: string;
      data: Parameters<typeof auditApi.addFinding>[1];
    }) => auditApi.addFinding(auditId, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["audits", variables.auditId, "findings"] });
      qc.invalidateQueries({ queryKey: ["audits", variables.auditId] });
    },
  });
}

export function useAuditChecklists() {
  return useQuery({
    queryKey: ["audit-checklists"],
    queryFn: () => auditApi.listChecklists(),
    staleTime: 60_000,
  });
}

// ─── Customer Complaints ─────────────────────────────────────────────────────

export function useComplaints(params?: Parameters<typeof complaintsApi.list>[0]) {
  return useQuery({
    queryKey: ["complaints", params],
    queryFn: () => complaintsApi.list(params),
    staleTime: 30_000,
  });
}

export function useComplaint(id: string) {
  return useQuery({
    queryKey: ["complaints", id],
    queryFn: () => complaintsApi.get(id),
    enabled: !!id,
  });
}

export function useCreateComplaint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: complaintsApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["complaints"] }),
  });
}

export function useUpdateComplaint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof complaintsApi.update>[1] }) =>
      complaintsApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["complaints"] });
      qc.invalidateQueries({ queryKey: ["complaints", variables.id] });
    },
  });
}


export function useDeleteComplaint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => complaintsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["complaints"] }),
  });
}

export function useRespondToComplaint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, response_text }: { id: string; response_text: string }) =>
      complaintsApi.respond(id, { response_text }),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["complaints", variables.id] });
    },
  });
}

// ─── Risk Management ─────────────────────────────────────────────────────────

export function useRisks(params?: Parameters<typeof riskApi.list>[0]) {
  return useQuery({
    queryKey: ["risks", params],
    queryFn: () => riskApi.list(params),
    staleTime: 30_000,
  });
}

export function useRisk(id: string) {
  return useQuery({
    queryKey: ["risks", id],
    queryFn: () => riskApi.get(id),
    enabled: !!id,
  });
}

export function useCreateRisk() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: riskApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["risks"] }),
  });
}

export function useUpdateRisk() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof riskApi.update>[1] }) =>
      riskApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["risks"] });
      qc.invalidateQueries({ queryKey: ["risks", variables.id] });
    },
  });
}

export function useDeleteRisk() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => riskApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["risks"] }),
  });
}

// ─── Management Review ────────────────────────────────────────────────────────

export function useManagementReviews(params?: Parameters<typeof managementReviewApi.list>[0]) {
  return useQuery({
    queryKey: ["management-reviews", params],
    queryFn: () => managementReviewApi.list(params),
    staleTime: 30_000,
  });
}

export function useManagementReview(id: string) {
  return useQuery({
    queryKey: ["management-reviews", id],
    queryFn: () => managementReviewApi.get(id),
    enabled: !!id,
  });
}

export function useCreateManagementReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: managementReviewApi.create,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["management-reviews"] }),
  });
}

export function useUpdateManagementReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Parameters<typeof managementReviewApi.update>[1] }) =>
      managementReviewApi.update(id, data),
    onSuccess: (_, variables) => {
      qc.invalidateQueries({ queryKey: ["management-reviews"] });
      qc.invalidateQueries({ queryKey: ["management-reviews", variables.id] });
    },
  });
}

export function useCompleteManagementReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => managementReviewApi.complete(id),
    onSuccess: (_, id) => {
      qc.invalidateQueries({ queryKey: ["management-reviews"] });
      qc.invalidateQueries({ queryKey: ["management-reviews", id] });
    },
  });
}

// ─── Environmental Monitoring ────────────────────────────────────────────────

export function useMonitoringPoints(params?: Parameters<typeof envMonitoringApi.listPoints>[0]) {
  return useQuery({
    queryKey: ["em-points", params],
    queryFn: () => envMonitoringApi.listPoints(params),
    staleTime: 30_000,
  });
}

export function useMonitoringPoint(id: string) {
  return useQuery({
    queryKey: ["em-points", id],
    queryFn: () => envMonitoringApi.getPoint(id),
    enabled: !!id,
  });
}

export function useCreateMonitoringPoint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: envMonitoringApi.createPoint,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["em-points"] }),
  });
}

export function useUpdateMonitoringPoint() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) => envMonitoringApi.updatePoint(id, data),
    onSuccess: (_, v) => { qc.invalidateQueries({ queryKey: ["em-points"] }); qc.invalidateQueries({ queryKey: ["em-points", v.id] }); },
  });
}

export function useMonitoringReadings(pointId: string, params?: { from?: string; to?: string }) {
  return useQuery({
    queryKey: ["em-readings", pointId, params],
    queryFn: () => envMonitoringApi.listReadings(pointId, params),
    enabled: !!pointId,
    staleTime: 15_000,
  });
}

export function useAddMonitoringReading() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ pointId, data }: { pointId: string; data: Parameters<typeof envMonitoringApi.addReading>[1] }) =>
      envMonitoringApi.addReading(pointId, data),
    onSuccess: (_, v) => {
      qc.invalidateQueries({ queryKey: ["em-readings", v.pointId] });
      qc.invalidateQueries({ queryKey: ["em-points"] });
    },
  });
}

export function useMonitoringExcursions(pointId: string) {
  return useQuery({
    queryKey: ["em-excursions", pointId],
    queryFn: () => envMonitoringApi.listExcursions(pointId),
    enabled: !!pointId,
  });
}

// ─── Proficiency Testing ──────────────────────────────────────────────────────

export function usePTPrograms(params?: Parameters<typeof ptApi.listPrograms>[0]) {
  return useQuery({
    queryKey: ["pt-programs", params],
    queryFn: () => ptApi.listPrograms(params),
    staleTime: 30_000,
  });
}

export function usePTProgram(id: string) {
  return useQuery({
    queryKey: ["pt-programs", id],
    queryFn: () => ptApi.getProgram(id),
    enabled: !!id,
  });
}

export function useCreatePTProgram() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ptApi.createProgram,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pt-programs"] }),
  });
}

export function usePTRounds(programId: string) {
  return useQuery({
    queryKey: ["pt-rounds", programId],
    queryFn: () => ptApi.listRounds(programId),
    enabled: !!programId,
    staleTime: 30_000,
  });
}

export function usePTRound(id: string) {
  return useQuery({
    queryKey: ["pt-rounds", "detail", id],
    queryFn: () => ptApi.getRound(id),
    enabled: !!id,
  });
}

export function useCreatePTRound() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ programId, data }: { programId: string; data: Parameters<typeof ptApi.createRound>[1] }) =>
      ptApi.createRound(programId, data),
    onSuccess: (round) => qc.invalidateQueries({ queryKey: ["pt-rounds", round.program_id] }),
  });
}

export function useUpdatePTRound() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) => ptApi.updateRound(id, data),
    onSuccess: (round) => {
      qc.invalidateQueries({ queryKey: ["pt-rounds"] });
      qc.invalidateQueries({ queryKey: ["pt-rounds", "detail", round.id] });
    },
  });
}

export function useCalculatePTScores() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (roundId: string) => ptApi.calculateScores(roundId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["pt-rounds"] }),
  });
}
