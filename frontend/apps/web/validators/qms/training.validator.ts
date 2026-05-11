import { z } from "zod";

export const createCourseSchema = z.object({
  course_code: z.string().trim().min(1).max(50),
  title: z.string().trim().min(1),
  course_type: z.string().trim().min(1),
  department: z.string().trim().optional(),
  description: z.string().trim().optional(),
  duration_hours: z.coerce.number().positive().optional(),
  passing_score: z.coerce.number().int().min(0).max(100).default(80),
  requires_certification: z.coerce.boolean().default(false),
  recurrence_days: z.coerce.number().int().positive().optional(),
  is_mandatory: z.coerce.boolean().default(false),
});

export type CreateCourseInput = z.infer<typeof createCourseSchema>;

