"use client";

import type { Session } from "next-auth";
import { signOut } from "next-auth/react";
import { useUIStore } from "@/lib/stores/ui.store";
import { LogOut, User, Search, Moon, Sun } from "lucide-react";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import { NotificationBell } from "@/components/platform/notification-bell";
import { useEffect, useMemo, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";

interface HeaderProps {
  session: Session;
}

export function Header({ session }: HeaderProps) {
  const { theme, setTheme } = useUIStore();
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const urlQuery = searchParams.get("q") ?? "";
  const [query, setQuery] = useState(urlQuery);

  const baseParams = useMemo(() => {
    // `useSearchParams()` returns a readonly instance; clone to safely mutate.
    return new URLSearchParams(searchParams.toString());
  }, [searchParams]);

  useEffect(() => {
    // Keep input in sync if navigation changes URL params.
    setQuery(urlQuery);
  }, [urlQuery]);

  useEffect(() => {
    const handle = window.setTimeout(() => {
      const next = new URLSearchParams(baseParams);
      const trimmed = query.trim();

      if (trimmed) next.set("q", trimmed);
      else next.delete("q");

      const qs = next.toString();
      // Next.js typed routes can reject dynamic, param-built URLs at type-level.
      // Runtime is valid; cast keeps typecheck strict elsewhere.
      router.replace((qs ? `${pathname}?${qs}` : pathname) as any, { scroll: false });
    }, 250);

    return () => window.clearTimeout(handle);
  }, [baseParams, pathname, query, router]);

  const handleSignOut = async () => {
    toast.promise(signOut({ callbackUrl: "/login" }), {
      loading: "Signing out...",
      success: "Signed out successfully",
      error: "Failed to sign out",
    });
  };

  return (
    <header className="h-16 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 flex items-center px-6 gap-4">
      {/* Search */}
      <div className="flex-1 max-w-md">
        <div className="relative">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground"
          />
          <input
            type="search"
            placeholder="Search..."
            className="w-full pl-9 pr-4 py-2 rounded-lg bg-muted border-0 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="flex items-center gap-2 ml-auto">
        {/* Theme toggle */}
        <button
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
          className="p-2 rounded-lg hover:bg-muted transition"
          title="Toggle theme"
        >
          {theme === "dark" ? <Sun size={18} /> : <Moon size={18} />}
        </button>

        <NotificationBell />

        {/* User menu */}
        <div className="flex items-center gap-2 pl-2 border-l border-border">
          <Link
            href={"/profile" as any}
            className="flex items-center gap-2 rounded-lg px-2 py-1 hover:bg-muted transition"
            title="My Profile"
          >
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              <User size={16} className="text-primary" />
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium leading-none">
                {session.user?.email?.split("@")[0] ?? "User"}
              </p>
              <p className="text-xs text-muted-foreground capitalize">{session.user.role ?? "user"}</p>
            </div>
          </Link>
          <button
            onClick={handleSignOut}
            className="p-2 rounded-lg hover:bg-muted transition text-muted-foreground hover:text-foreground"
            title="Sign out"
          >
            <LogOut size={16} />
          </button>
        </div>
      </div>
    </header>
  );
}
