"use client"

import { useState } from "react"
import { SlidersHorizontal, X } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { cn } from "@/lib/utils"

interface FilterGroup {
  id: string
  label: string
  type: "checkbox" | "select" | "date-range" | "text"
  options?: { label: string; value: string }[]
  value: string | string[]
  onChange: (value: string | string[]) => void
}

interface FilterSidebarProps {
  groups: FilterGroup[]
  className?: string
  onClearAll?: () => void
}

export function FilterSidebar({ groups, className, onClearAll }: FilterSidebarProps) {
  const [open, setOpen] = useState(false)

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        onClick={() => setOpen(!open)}
        className="gap-1.5"
      >
        <SlidersHorizontal className="h-4 w-4" />
        Filters
      </Button>

      <div
        className={cn(
          "fixed inset-y-0 right-0 z-50 w-80 bg-background border-l shadow-xl transform transition-transform duration-200 overflow-y-auto",
          open ? "translate-x-0" : "translate-x-full",
          className,
        )}
      >
        <div className="flex items-center justify-between p-4 border-b">
          <h3 className="font-semibold text-sm">Filters</h3>
          <div className="flex items-center gap-2">
            {onClearAll && (
              <Button variant="ghost" size="sm" onClick={onClearAll}>
                Clear all
              </Button>
            )}
            <Button variant="ghost" size="icon" onClick={() => setOpen(false)}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        <div className="p-4 space-y-5">
          {groups.map((group, i) => (
            <div key={group.id}>
              {i > 0 && <Separator className="mb-5" />}
              <p className="text-sm font-medium mb-2">{group.label}</p>

              {group.type === "checkbox" && group.options && (
                <div className="space-y-1.5">
                  {group.options.map((opt) => {
                    const values = Array.isArray(group.value) ? group.value : []
                    const checked = values.includes(opt.value)
                    return (
                      <label
                        key={opt.value}
                        className="flex items-center gap-2 text-sm cursor-pointer hover:text-foreground transition-colors"
                      >
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => {
                            const next = checked
                              ? values.filter((v) => v !== opt.value)
                              : [...values, opt.value]
                            group.onChange(next)
                          }}
                          className="rounded border-slate-300"
                        />
                        {opt.label}
                      </label>
                    )
                  })}
                </div>
              )}

              {group.type === "select" && group.options && (
                <select
                  value={typeof group.value === "string" ? group.value : ""}
                  onChange={(e) => group.onChange(e.target.value)}
                  className="flex h-9 w-full rounded-md border border-input bg-background px-3 py-1 text-sm"
                >
                  <option value="">All</option>
                  {group.options.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              )}

              {group.type === "text" && (
                <Input
                  value={typeof group.value === "string" ? group.value : ""}
                  onChange={(e) => group.onChange(e.target.value)}
                  placeholder={`Filter by ${group.label.toLowerCase()}...`}
                />
              )}
            </div>
          ))}
        </div>
      </div>

      {open && (
        <div
          className="fixed inset-0 z-40 bg-black/20"
          onClick={() => setOpen(false)}
        />
      )}
    </>
  )
}
