import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
  mfa_code: z
    .string()
    .trim()
    .regex(/^\d{6}$/)
    .optional(),
});

export const { handlers, signIn, signOut, auth } = NextAuth({
  session: { strategy: "jwt" },
  pages: {
    signIn: "/login",
    error: "/login",
  },
  providers: [
    Credentials({
      id: "credentials",
      name: "Email & Password",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
        mfa_code: { label: "MFA Code", type: "text" },
      },
      async authorize(credentials) {
        const parsed = loginSchema.safeParse(credentials);
        if (!parsed.success) return null;

        try {
          const res = await fetch(
            `${process.env.AUTH_SERVICE_URL}/api/v1/auth/login`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(parsed.data),
            }
          );

          if (!res.ok) {
            const error = await res.json();
            if (error.error?.code === "MFA_REQUIRED") {
              throw new Error("MFA_REQUIRED");
            }
            return null;
          }

          const data = await res.json();
          const payload = data.data;
          const user = payload?.user;
          if (!user || !payload?.access_token) return null;

          return {
            id: user.id,
            email: user.email,
            role: user.role,
            tenant_id: user.tenant_id,
            mfa_enabled: user.mfa_enabled,
            access_token: payload.access_token,
          };
        } catch (err: unknown) {
          if (err instanceof Error && err.message === "MFA_REQUIRED") {
            throw err;
          }
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.email = user.email;
        token.role = (user as Record<string, unknown>).role as string;
        token.tenant_id = (user as Record<string, unknown>).tenant_id as string | null;
        token.access_token = (user as Record<string, unknown>).access_token as string;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.id as string;
      session.user.email = token.email as string;
      (session as unknown as Record<string, unknown>).role = token.role;
      (session as unknown as Record<string, unknown>).tenant_id = token.tenant_id;
      (session as unknown as Record<string, unknown>).access_token = token.access_token;
      return session;
    },
  },
  trustHost: true,
});
