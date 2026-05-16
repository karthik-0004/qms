"use client"

import { cn } from "@/lib/utils"
import { Clock, User, Info } from "lucide-react"

interface TimelineEvent {
  id: string
  action: string
  actor: string
  timestamp: string
  description?: string
  before?: Record<string, unknown> | null
  after?: Record<string, unknown> | null
}

interface EventTimelineProps {
  events: TimelineEvent[]
  className?: string
  emptyMessage?: string
}

export function EventTimeline({
  events,
  className,
  emptyMessage = "No events recorded.",
}: EventTimelineProps) {
  if (events.length === 0) {
    return (
      <div className="flex items-center gap-2 py-8 text-sm text-muted-foreground justify-center">
        <Info className="h-4 w-4" />
        {emptyMessage}
      </div>
    )
  }

  return (
    <div className={cn("relative", className)}>
      <div className="absolute left-4 top-2 bottom-2 w-0.5 bg-border" />
      <div className="space-y-0">
        {events.map((event, i) => (
          <div key={event.id} className="relative flex gap-4 pb-6 last:pb-0">
            <div
              className={cn(
                "relative z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 bg-background shrink-0 mt-0.5",
                i === 0 ? "border-blue-400" : "border-slate-300 dark:border-slate-600",
              )}
            >
              <div
                className={cn(
                  "w-2.5 h-2.5 rounded-full",
                  i === 0 ? "bg-blue-500" : "bg-slate-400 dark:bg-slate-500",
                )}
              />
            </div>
            <div className="flex-1 min-w-0 pt-1">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-sm font-medium capitalize">
                  {event.action.replace(/_/g, " ")}
                </span>
                <span className="text-xs text-muted-foreground flex items-center gap-1">
                  <User className="h-3 w-3" />
                  {event.actor}
                </span>
                <span className="text-xs text-muted-foreground flex items-center gap-1 ml-auto">
                  <Clock className="h-3 w-3" />
                  {new Date(event.timestamp).toLocaleString()}
                </span>
              </div>
              {event.description && (
                <p className="text-sm text-muted-foreground mt-1">{event.description}</p>
              )}
              {event.before && event.after && (
                <details className="mt-1">
                  <summary className="text-xs text-muted-foreground cursor-pointer hover:text-foreground">
                    Show field changes
                  </summary>
                  <div className="mt-1 text-xs space-y-0.5">
                    {Object.entries(event.after).map(([key, val]) => {
                      const oldVal = event.before?.[key]
                      if (oldVal === val) return null
                      return (
                        <div key={key} className="flex gap-2">
                          <span className="font-medium w-28 truncate">{key}:</span>
                          <span className="text-red-500 line-through mr-1">
                            {String(oldVal ?? "—")}
                          </span>
                          <span className="text-emerald-500">{String(val ?? "—")}</span>
                        </div>
                      )
                    })}
                  </div>
                </details>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
