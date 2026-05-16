"use client"

import type { ReactNode } from "react"
import { cn } from "@/lib/utils"

interface TileConfig {
  id: string
  icon: ReactNode
  label: string
  count?: number
  description?: string
  color?: string
  onClick?: () => void
}

interface DashboardTilesProps {
  tiles: TileConfig[]
  columns?: 2 | 3 | 4
  className?: string
}

const COLORS = [
  "bg-blue-50 border-blue-200 hover:bg-blue-100 dark:bg-blue-950 dark:border-blue-800 dark:hover:bg-blue-900",
  "bg-emerald-50 border-emerald-200 hover:bg-emerald-100 dark:bg-emerald-950 dark:border-emerald-800 dark:hover:bg-emerald-900",
  "bg-amber-50 border-amber-200 hover:bg-amber-100 dark:bg-amber-950 dark:border-amber-800 dark:hover:bg-amber-900",
  "bg-purple-50 border-purple-200 hover:bg-purple-100 dark:bg-purple-950 dark:border-purple-800 dark:hover:bg-purple-900",
  "bg-rose-50 border-rose-200 hover:bg-rose-100 dark:bg-rose-950 dark:border-rose-800 dark:hover:bg-rose-900",
  "bg-cyan-50 border-cyan-200 hover:bg-cyan-100 dark:bg-cyan-950 dark:border-cyan-800 dark:hover:bg-cyan-900",
  "bg-orange-50 border-orange-200 hover:bg-orange-100 dark:bg-orange-950 dark:border-orange-800 dark:hover:bg-orange-900",
  "bg-indigo-50 border-indigo-200 hover:bg-indigo-100 dark:bg-indigo-950 dark:border-indigo-800 dark:hover:bg-indigo-900",
  "bg-teal-50 border-teal-200 hover:bg-teal-100 dark:bg-teal-950 dark:border-teal-800 dark:hover:bg-teal-900",
  "bg-pink-50 border-pink-200 hover:bg-pink-100 dark:bg-pink-950 dark:border-pink-800 dark:hover:bg-pink-900",
  "bg-lime-50 border-lime-200 hover:bg-lime-100 dark:bg-lime-950 dark:border-lime-800 dark:hover:bg-lime-900",
  "bg-violet-50 border-violet-200 hover:bg-violet-100 dark:bg-violet-950 dark:border-violet-800 dark:hover:bg-violet-900",
]

export function DashboardTiles({ tiles, columns = 4, className }: DashboardTilesProps) {
  const gridCols = {
    2: "grid-cols-1 sm:grid-cols-2",
    3: "grid-cols-1 sm:grid-cols-2 md:grid-cols-3",
    4: "grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4",
  }

  return (
    <div className={cn("grid gap-4", gridCols[columns], className)}>
      {tiles.map((tile, i) => (
        <button
          key={tile.id}
          type="button"
          onClick={tile.onClick}
          className={cn(
            "flex flex-col gap-2 rounded-xl border p-4 text-left transition-colors cursor-pointer",
            COLORS[i % COLORS.length],
            tile.color,
          )}
        >
          <div className="flex items-center justify-between">
            <span className="text-2xl">{tile.icon}</span>
            {tile.count !== undefined && (
              <span className="text-2xl font-bold">{tile.count}</span>
            )}
          </div>
          <p className="text-sm font-semibold">{tile.label}</p>
          {tile.description && (
            <p className="text-xs text-muted-foreground">{tile.description}</p>
          )}
        </button>
      ))}
    </div>
  )
}
