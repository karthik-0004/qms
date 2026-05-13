import { cache } from "react";
import type { Session } from "next-auth";
import { auth } from "./config";

/**
 * Same as `auth()`, but deduped within one RSC navigation when called from
 * root layout, segment layouts, and pages. Do not use for middleware (`auth(...)` wrapper).
 */
export const getCachedSession = cache(async (): Promise<Session | null> => {
  try {
    return await auth();
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    if (
      message.includes("JWTSessionError") ||
      message.includes("no matching decryption secret")
    ) {
      return null;
    }
    throw err;
  }
});
