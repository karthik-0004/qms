import { z } from "zod";
import { TENANT_PRODUCT_IDS, TENANT_REGION_OPTIONS, TENANT_TIERS } from "@/constants/tenant-admin";

type RegionCode = (typeof TENANT_REGION_OPTIONS)[number]["value"];
const REGION_CODES_FOR_ZOD = TENANT_REGION_OPTIONS.map((r) => r.value) as [RegionCode, ...RegionCode[]];
const productEnum = TENANT_PRODUCT_IDS as unknown as [string, ...string[]];
const tierEnum = TENANT_TIERS as unknown as [string, ...string[]];

const optionalTrimmed = () =>
  z
    .string()
    .optional()
    .transform((v) => {
      const t = v?.trim();
      return t === "" ? undefined : t;
    });

export const tenantCreateSchema = z.object({
  tenant_name: z.string().trim().min(2).max(100),
  products: z.array(z.enum(productEnum)).min(1),
  tier: z.enum(tierEnum),
  region: z.enum(REGION_CODES_FOR_ZOD),
  primary_first_name: z.string().trim().min(1).max(100),
  primary_last_name: z.string().trim().min(1).max(100),
  primary_email: z.string().trim().email(),
  primary_phone: optionalTrimmed(),
  company_website: optionalTrimmed(),
  company_industry: optionalTrimmed(),
  company_notes: optionalTrimmed(),
  address_line1: optionalTrimmed(),
  address_line2: optionalTrimmed(),
  city: optionalTrimmed(),
  state: optionalTrimmed(),
  country: optionalTrimmed(),
  postal_code: optionalTrimmed(),
  billing_email: optionalTrimmed(),
  billing_phone: optionalTrimmed(),
  tax_id: optionalTrimmed(),
  billing_address_same_as_address: z.boolean(),
  billing_address_line1: optionalTrimmed(),
  billing_address_line2: optionalTrimmed(),
  billing_city: optionalTrimmed(),
  billing_state: optionalTrimmed(),
  billing_country: optionalTrimmed(),
  billing_postal_code: optionalTrimmed(),
  tenant_timezone: z.string().trim().min(1).max(100),
  tenant_locale: z.string().trim().min(1).max(20),
}).superRefine((data, ctx) => {
  if (data.billing_email && !z.string().email().safeParse(data.billing_email).success) {
    ctx.addIssue({
      code: z.ZodIssueCode.custom,
      message: "Invalid email",
      path: ["billing_email"],
    });
  }
});

export type TenantCreateFormValues = z.infer<typeof tenantCreateSchema>;

export const tenantUpdateSchema = z.object({
  tenant_name: z.string().trim().min(2).max(100),
  tier: z.enum(tierEnum),
  products: z.array(z.enum(productEnum)).min(1),
});

export type TenantUpdateFormValues = z.infer<typeof tenantUpdateSchema>;

export const tenantSettingsSchema = z.object({
  max_users: z.coerce.number().int().min(1).max(10000),
  max_storage_gb: z.coerce.number().int().min(1).max(10000),
  timezone: z.string().trim().min(1).max(100),
  locale: z.string().trim().min(1).max(20),
});

export type TenantSettingsFormValues = z.infer<typeof tenantSettingsSchema>;
