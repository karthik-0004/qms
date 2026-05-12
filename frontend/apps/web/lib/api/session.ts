import { getSession } from "next-auth/react";

type SessionLike = Record<string, unknown> | null;

let cachedSession: SessionLike = null;
let cachedAtMs = 0;

/** Default for session fetch wait and in-memory session reuse (5 minutes). */
const FIVE_MIN_MS = 5 * 60 * 1000;

function parseBoundedMs(
  raw: string | undefined,
  min: number,
  max: number,
  fallback: number,
): number {
  const n = raw ? Number(raw) : NaN;
  if (Number.isFinite(n) && n >= min && n <= max) return n;
  return fallback;
}

/** How long to reuse a successful `getSession()` result before refetching. */
const SESSION_CACHE_TTL_MS = parseBoundedMs(
  process.env.NEXT_PUBLIC_SESSION_CACHE_TTL_MS,
  1_000,
  30 * 60 * 1000,
  FIVE_MIN_MS,
);

/** Max wait for `getSession()` when `/api/auth/session` is slow. */
function resolveSessionFetchTimeoutMs(): number {
  return parseBoundedMs(
    process.env.NEXT_PUBLIC_SESSION_FETCH_TIMEOUT_MS,
    500,
    FIVE_MIN_MS,
    FIVE_MIN_MS,
  );
}

const SESSION_FETCH_TIMEOUT_MS = resolveSessionFetchTimeoutMs();

function nowMs() {
  return Date.now();
}

async function getSessionWithTimeout(timeoutMs: number): Promise<SessionLike> {
  return (await Promise.race([
    getSession() as unknown as Promise<SessionLike>,
    new Promise<SessionLike>((resolve) => {
      setTimeout(() => resolve(null), timeoutMs);
    }),
  ])) as SessionLike;
}

/**
 * Fetches NextAuth session with a bounded wait (default 5 minutes, overridable via env).
 */
export async function getSessionFast(): Promise<SessionLike> {
  const age = nowMs() - cachedAtMs;
  if (cachedSession && age < SESSION_CACHE_TTL_MS) return cachedSession;

  const session = await getSessionWithTimeout(SESSION_FETCH_TIMEOUT_MS);
  if (session) {
    cachedSession = session;
    cachedAtMs = nowMs();
  }

  return session;
}

/** Force-evict the in-memory session cache so the next call fetches fresh from the server. */
export function clearSessionCache(): void {
  cachedSession = null;
  cachedAtMs = 0;
}

/**
 * Token + tenant for API clients. Prefers NextAuth-augmented `session.user`;
 * falls back to legacy top-level fields for older sessions/tools.
 */
export function resolveSessionAuthContext(session: SessionLike | null): {
  bearerToken?: string;
  tenantId?: string | null;
} {
  if (!session) return {};
  const s = session as Record<string, unknown>;
  const user = s.user as Record<string, unknown> | undefined;

  /** Prefer top-level token — Auth.js client session may omit custom `user` fields. */
  const bearerFromSessionRoot = s.accessToken;
  const bearerFromUser = user?.access_token;
  const bearerFromLegacy = s.access_token;
  const bearerToken =
    typeof bearerFromSessionRoot === "string" && bearerFromSessionRoot.trim()
      ? bearerFromSessionRoot.trim()
      : typeof bearerFromUser === "string" && bearerFromUser.trim()
        ? bearerFromUser.trim()
        : typeof bearerFromLegacy === "string" && bearerFromLegacy.trim()
          ? bearerFromLegacy.trim()
          : undefined;

  const tenantFromUser = user?.tenant_id;
  const tenantFromLegacy = s.tenant_id;
  let tenantId: string | null | undefined;
  if (typeof tenantFromUser === "string" || tenantFromUser === null) {
    tenantId = tenantFromUser as string | null;
  } else if (typeof tenantFromLegacy === "string" || tenantFromLegacy === null) {
    tenantId = tenantFromLegacy as string | null;
  }

  return { bearerToken, tenantId };
}

