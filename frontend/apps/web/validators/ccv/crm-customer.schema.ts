import { z } from "zod";

export const crmCustomerCreateSchema = z.object({
  company_name: z.string().min(1, "Company name is required").max(255),
  industry: z.string().max(100).optional(),
  email: z.union([z.literal(""), z.string().email("Invalid email")]).optional(),
  phone: z.string().max(80).optional(),
});

export type CrmCustomerCreateFormValues = z.infer<typeof crmCustomerCreateSchema>;
