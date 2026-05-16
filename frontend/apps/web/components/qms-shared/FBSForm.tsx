"use client"

import { useState, type ReactNode } from "react"
import { cn } from "@/lib/utils"

interface FBSTab {
  id: string
  label: string
  icon?: string
  content: ReactNode
  validation?: () => boolean | Promise<boolean>
}

interface FBSFormProps {
  tabs: FBSTab[]
  defaultTab?: string
  className?: string
  header?: ReactNode
}

export function FBSForm({ tabs, defaultTab, className, header }: FBSFormProps) {
  const [activeTab, setActiveTab] = useState(defaultTab ?? tabs[0]?.id)

  return (
    <div className={cn("space-y-4", className)}>
      {header}

      {/* Tab bar */}
      <div className="flex overflow-x-auto gap-0.5 rounded-lg border bg-muted/30 p-0.5">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              "flex items-center gap-1.5 whitespace-nowrap px-3 py-2 rounded-md text-sm font-medium transition-colors",
              activeTab === tab.id
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground",
            )}
          >
            {tab.icon && <span className="text-base">{tab.icon}</span>}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Active tab content */}
      <div>
        {tabs.find((t) => t.id === activeTab)?.content}
      </div>
    </div>
  )
}
