import type { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session {
    user: DefaultSession["user"] & {
      id: string;
      role: string;
      tenant_id: string | null;
      company_id: string | null;
      /** Present for bearer API calls from the browser. */
      access_token: string;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
    role?: string;
    tenant_id?: string | null;
    company_id?: string | null;
    access_token?: string;
    refresh_token?: string | null;
    access_token_exp?: number;
    error?: string;
  }
}
