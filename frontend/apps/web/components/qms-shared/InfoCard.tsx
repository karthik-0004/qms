"use client"

import { useState, type ReactNode } from "react"
import { cn } from "@/lib/utils"

interface InfoCardTab {
  id: string
  label: string
  content: ReactNode
}

interface InfoCardSection {
  id: string
  title: string
  content: ReactNode
}

interface InfoCardProps {
  title: string
  subtitle?: string
  status?: ReactNode
  actions?: ReactNode
  sections: InfoCardSection[]
  tabs: InfoCardTab[]
  defaultTab?: string
  className?: string
}

export function InfoCard({
  title,
  subtitle,
  status,
  actions,
  sections,
  tabs,
  defaultTab,
  className,
}: InfoCardProps) {
  const [activeTab, setActiveTab] = useState(defaultTab ?? tabs[0]?.id)

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-3 flex-wrap">
            <h1 className="text-xl font-bold tracking-tight break-words">{title}</h1>
            {status && <span className="shrink-0">{status}</span>}
          </div>
          {subtitle && (
            <p className="text-muted-foreground text-sm mt-1">{subtitle}</p>
          )}
        </div>
        {actions && (
          <div className="flex flex-wrap items-center gap-2 shrink-0">
            {actions}
          </div>
        )}
      </div>

      {/* Two-column layout: left = sections, right = tabs */}
      <div className="grid grid-cols-1 lg:grid-cols-[1fr_320px] gap-6">
        {/* Left column: grouped form sections */}
        <div className="space-y-6">
          {sections.map((section) => (
            <div key={section.id}>
              <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-3">
                {section.title}
              </h2>
              <div className="rounded-lg border bg-card p-4 space-y-3">
                {section.content}
              </div>
            </div>
          ))}
        </div>

        {/* Right column: vertical tab navigation */}
        <div>
          <div className="flex flex-col gap-1 rounded-lg border bg-card p-1">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  "text-left px-3 py-2 rounded-md text-sm transition-colors",
                  activeTab === tab.id
                    ? "bg-primary/10 text-primary font-medium"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted",
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Active tab content */}
          <div className="mt-4">
            {tabs.find((t) => t.id === activeTab)?.content}
          </div>
        </div>
      </div>
    </div>
  )
}
