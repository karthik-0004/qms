import { cache } from "react";
import { auth } from "./config";

/**
 * Same as `auth()`, but deduped within one RSC navigation when called from
 * root layout, segment layouts, and pages. Do not use for middleware (`auth(...)` wrapper).
 */
export const getCachedSession = cache(auth);
