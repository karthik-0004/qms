"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import { useUIStore } from "@/lib/stores/ui.store";

/**
 * Keeps sidebar product section aligned with the current URL when visiting
 * /qms, /ccv, or /em routes directly (deep links, refresh).
 */
export function ActiveProductSync() {
  const pathname = usePathname();
  const setActiveProduct = useUIStore((s) => s.setActiveProduct);

  useEffect(() => {
    if (pathname.startsWith("/qms")) setActiveProduct("qms");
    else if (pathname.startsWith("/em")) setActiveProduct("em");
    else if (pathname.startsWith("/ccv")) setActiveProduct("ccv");
  }, [pathname, setActiveProduct]);

  return null;
}
