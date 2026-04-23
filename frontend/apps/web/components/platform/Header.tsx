"use client";

import { signOut } from "next-auth/react";
import { useUIStore } from "@/lib/stores/ui.store";
import { Bell, LogOut, User, Search, Moon, Sun } from "lucide-react";
import { cn } from "@/lib/utils";
import { useState } from "react";
import { toast } from "sonner";

interface HeaderProps {
  session: Record<string, unknown>;
}

export function Header({ session }: HeaderProps) {
  const { theme, setTheme } = useUIStore();
  const [notifOpen, setNotifOpen] = useState(false);

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

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setNotifOpen(!notifOpen)}
            className="p-2 rounded-lg hover:bg-muted transition relative"
            title="Notifications"
          >
            <Bell size={18} />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-red-500" />
          </button>
        </div>

        {/* User menu */}
        <div className="flex items-center gap-2 pl-2 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
            <User size={16} className="text-primary" />
          </div>
          <div className="hidden sm:block">
            <p className="text-sm font-medium leading-none">
              {(session?.user as { email?: string } | undefined)?.email?.split("@")[0] ?? "User"}
            </p>
            <p className="text-xs text-muted-foreground capitalize">
              {String((session as Record<string, unknown>)?.role ?? "user")}
            </p>
          </div>
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
