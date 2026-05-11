"use client";

import { formatDistanceToNow } from "date-fns";
import { Bell } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Button } from "@/components/ui/button";
import {
  NOTIFICATIONS_EMPTY,
  NOTIFICATIONS_MARK_ALL_READ,
  NOTIFICATIONS_MARK_READ,
  NOTIFICATIONS_PANEL_TITLE,
} from "@/constants/notifications-panel";
import { cn } from "@/lib/utils";
import { useNotificationsStore } from "@/lib/stores/notifications.store";

export function NotificationBell() {
  const [open, setOpen] = useState(false);

  const items = useNotificationsStore((s) => s.items);
  const markRead = useNotificationsStore((s) => s.markRead);
  const markAllRead = useNotificationsStore((s) => s.markAllRead);
  const seedIfEmpty = useNotificationsStore((s) => s.seedIfEmpty);

  const panelRef = useRef<HTMLDivElement>(null);
  const buttonRef = useRef<HTMLButtonElement>(null);

  const unreadCount = items.filter((n) => !n.read).length;

  useEffect(() => {
    seedIfEmpty();
  }, [seedIfEmpty]);

  useEffect(() => {
    if (!open) return;

    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };

    const onPointer = (e: MouseEvent | PointerEvent) => {
      const t = e.target as Node;
      if (panelRef.current?.contains(t)) return;
      if (buttonRef.current?.contains(t)) return;
      setOpen(false);
    };

    document.addEventListener("keydown", onKey);
    document.addEventListener("pointerdown", onPointer);
    return () => {
      document.removeEventListener("keydown", onKey);
      document.removeEventListener("pointerdown", onPointer);
    };
  }, [open]);

  return (
    <div className="relative">
      <button
        ref={buttonRef}
        type="button"
        aria-expanded={open}
        aria-haspopup="dialog"
        aria-controls="notifications-panel"
        aria-label={
          unreadCount > 0
            ? `${NOTIFICATIONS_PANEL_TITLE}, ${unreadCount} unread`
            : NOTIFICATIONS_PANEL_TITLE
        }
        onClick={() => setOpen(!open)}
        className="p-2 rounded-lg hover:bg-muted transition relative outline-none focus-visible:ring-2 focus-visible:ring-ring"
      >
        <Bell size={18} className="text-foreground" />
        {unreadCount > 0 ? (
          <span
            aria-hidden
            className="absolute top-1.5 right-1.5 min-w-[6px] h-2 px-0.5 rounded-full bg-red-500"
          />
        ) : null}
      </button>

      {open ? (
        <div
          ref={panelRef}
          id="notifications-panel"
          role="dialog"
          aria-modal="false"
          aria-label={NOTIFICATIONS_PANEL_TITLE}
          className={cn(
            "absolute right-0 top-full mt-2 z-[100]",
            "w-[min(calc(100vw-2rem),22rem)] max-h-[min(24rem,70vh)]",
            "rounded-lg border bg-popover text-popover-foreground shadow-lg overflow-hidden flex flex-col"
          )}
        >
          <div className="flex items-center justify-between gap-2 px-4 py-3 border-b shrink-0">
            <p className="text-sm font-semibold">{NOTIFICATIONS_PANEL_TITLE}</p>
            {items.length > 0 && unreadCount > 0 ? (
              <Button
                variant="ghost"
                size="sm"
                type="button"
                className="h-8 text-xs"
                onClick={() => markAllRead()}
              >
                {NOTIFICATIONS_MARK_ALL_READ}
              </Button>
            ) : null}
          </div>

          <ul className="overflow-y-auto flex-1 p-2 space-y-1 list-none">
            {items.length === 0 ? (
              <li className="text-sm text-muted-foreground px-3 py-6 text-center">
                {NOTIFICATIONS_EMPTY}
              </li>
            ) : (
              items.map((n) => (
                <li key={n.id}>
                  <div
                    className={cn(
                      "rounded-md px-3 py-2 transition-colors flex flex-col gap-1 border border-transparent",
                      n.read ? "opacity-75" : "bg-muted/70 border-border/60"
                    )}
                  >
                    <div className="flex justify-between gap-2 items-start">
                      <p className="text-sm font-medium leading-tight">{n.title}</p>
                      <span className="text-[10px] text-muted-foreground whitespace-nowrap shrink-0">
                        {formatDistanceToNow(new Date(n.createdAt), { addSuffix: true })}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground leading-snug">{n.body}</p>
                    {!n.read ? (
                      <Button
                        variant="secondary"
                        size="sm"
                        type="button"
                        className="h-7 text-xs self-start mt-1"
                        onClick={() => markRead(n.id)}
                      >
                        {NOTIFICATIONS_MARK_READ}
                      </Button>
                    ) : null}
                  </div>
                </li>
              ))
            )}
          </ul>
        </div>
      ) : null}
    </div>
  );
}
