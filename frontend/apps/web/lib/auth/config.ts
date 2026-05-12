import NextAuth, { CredentialsSignin } from "next-auth";
import Credentials from "next-auth/providers/credentials";
import { z } from "zod";

function parseLoginFetchTimeoutMs(): number {
  const raw = process.env.AUTH_LOGIN_FETCH_TIMEOUT_MS;
  const n = raw ? Number(raw) : NaN;
  if (Number.isFinite(n) && n >= 3_000 && n <= 120_000) return n;
  return 25_000;
}

function getAuthServiceBaseUrl(): string | null {
  const raw = process.env.AUTH_SERVICE_URL?.trim();
  if (!raw) return null;
  return raw.replace(/\/+$/, "");
}

function throwCredentialsWithCode(code: string, message?: string): never {
  const err = new CredentialsSignin(message);
  err.code = code;
  throw err;
}

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(1),
  mfa_code: z
    .string()
    .trim()
    .regex(/^\d{6}$/)
    .optional(),
});

async function refreshAccessToken(refreshToken: string): Promise<{
  access_token: string;
  refresh_token: string;
  expires_at: number;
} | null> {
  const baseUrl = getAuthServiceBaseUrl();
  if (!baseUrl) return null;
  try {
    const res = await fetch(`${baseUrl}/api/v1/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
      signal: AbortSignal.timeout(10_000),
    });
    if (!res.ok) return null;
    const data = await res.json();
    const payload = data.data;
    if (!payload?.access_token) return null;
    return {
      access_token: payload.access_token,
      refresh_token: payload.refresh_token || refreshToken,
      expires_at: Math.floor(Date.now() / 1000) + (payload.expires_in ?? 900),
    };
  } catch {
    return null;
  }
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  session: { strategy: "jwt" },
  pages: {
    signIn: "/signin",
    error: "/signin",
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

        const baseUrl = getAuthServiceBaseUrl();
        if (!baseUrl) {
          throwCredentialsWithCode(
            "auth_misconfigured",
            "AUTH_SERVICE_URL is not set.",
          );
        }

        if (
          process.env.NODE_ENV === "development" &&
          baseUrl.includes("auth-service") &&
          !baseUrl.includes("localhost")
        ) {
          console.warn(
            '[auth] AUTH_SERVICE_URL uses the Docker hostname "auth-service". ' +
              "When Next.js runs on your machine (npm run dev), use http://localhost:8001 " +
              "(see docs/dev-auth-access.md).",
          );
        }

        const loginFetchTimeoutMs = parseLoginFetchTimeoutMs();

        try {
          let res: Response;
          try {
            res = await fetch(`${baseUrl}/api/v1/auth/login`, {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify(parsed.data),
              signal: AbortSignal.timeout(loginFetchTimeoutMs),
            });
          } catch (fetchErr: unknown) {
            const name =
              fetchErr &&
              typeof fetchErr === "object" &&
              "name" in fetchErr
                ? String((fetchErr as { name?: unknown }).name)
                : "";
            if (name === "AbortError" || name === "TimeoutError") {
              throwCredentialsWithCode(
                "auth_timeout",
                `Auth service did not respond within ${loginFetchTimeoutMs}ms.`,
              );
            }
            throwCredentialsWithCode(
              "auth_unreachable",
              "Could not reach auth service.",
            );
          }

          if (!res.ok) {
            let error: { error?: { code?: string } } | null = null;
            try {
              error = (await res.json()) as { error?: { code?: string } };
            } catch {
              /* non-JSON error body */
            }
            if (error?.error?.code === "MFA_REQUIRED") {
              throwCredentialsWithCode("MFA_REQUIRED");
            }
            return null;
          }

          const data = await res.json();
          const payload = data.data;
          const user = payload?.user;
          if (!user || !payload?.access_token) return null;

          const expiresIn = payload.expires_in ?? 900;
          const accessTokenExp = Math.floor(Date.now() / 1000) + expiresIn;

          return {
            id: user.id,
            email: user.email,
            role: user.role,
            tenant_id: user.tenant_id ?? null,
            company_id: user.company_id ?? null,
            mfa_enabled: user.mfa_enabled,
            access_token: payload.access_token,
            refresh_token: payload.refresh_token ?? null,
            access_token_exp: accessTokenExp,
          };
        } catch (err: unknown) {
          if (err instanceof CredentialsSignin) throw err;
          return null;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id;
        token.id = user.id;
        token.email = user.email;
        token.role = (user as Record<string, unknown>).role as string;
        token.tenant_id = (user as Record<string, unknown>).tenant_id as string | null;
        token.company_id = (user as Record<string, unknown>).company_id as string | null;
        token.access_token = (user as Record<string, unknown>).access_token as string;
        token.refresh_token = (user as Record<string, unknown>).refresh_token as string | null;
        token.access_token_exp = (user as Record<string, unknown>).access_token_exp as number;
      }

      // Proactively refresh the access_token when it's within 5 minutes of expiry.
      const now = Math.floor(Date.now() / 1000);
      const exp = token.access_token_exp as number | undefined;
      const rt = token.refresh_token as string | null | undefined;
      if (exp && rt && now > exp - 300) {
        const refreshed = await refreshAccessToken(rt);
        if (refreshed) {
          token.access_token = refreshed.access_token;
          token.refresh_token = refreshed.refresh_token;
          token.access_token_exp = refreshed.expires_at;
          token.error = undefined;
        } else {
          token.error = "RefreshAccessTokenError";
        }
      }

      return token;
    },
    async session({ session, token }) {
      session.user.id = (token.id as string) ?? (token.sub ?? "");
      session.user.email = (token.email as string) ?? session.user.email ?? "";
      session.user.role =
        typeof token.role === "string" ? token.role : "tenant_user";
      session.user.tenant_id =
        token.tenant_id === undefined ? null : (token.tenant_id as string | null);
      session.user.company_id =
        token.company_id === undefined ? null : (token.company_id as string | null);
      const access = (token.access_token as string) ?? "";
      session.user.access_token = access;
      session.accessToken = access;
      return session;
    },
  },
  trustHost: true,
});
