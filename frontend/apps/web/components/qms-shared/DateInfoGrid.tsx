"use client"

import { cn } from "@/lib/utils"

interface DateInfoItem {
  label: string
  value: string | null | undefined
}

interface DateInfoGridProps {
  items: DateInfoItem[]
  className?: string
}

export function DateInfoGrid({ items, className }: DateInfoGridProps) {
  return (
    <div className={cn("grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-3", className)}>
      {items.map((item) => (
        <div key={item.label}>
          <p className="text-xs text-muted-foreground">{item.label}</p>
          <p className="text-sm font-medium mt-0.5">{item.value ?? "—"}</p>
        </div>
      ))}
    </div>
  )
}
