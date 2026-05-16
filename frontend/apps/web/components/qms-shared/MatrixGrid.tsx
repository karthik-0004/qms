"use client"

import { cn } from "@/lib/utils"

type CellStatus = "complete" | "in_progress" | "overdue" | "waiting" | "pending" | "none"

const STATUS_ICONS: Record<CellStatus, { icon: string; label: string; className: string }> = {
  complete: { icon: "✓", label: "Complete", className: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300" },
  in_progress: { icon: "◷", label: "In Progress", className: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300" },
  overdue: { icon: "⚠", label: "Overdue", className: "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300" },
  waiting: { icon: "🔒", label: "Waiting on Prerequisite", className: "bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300" },
  pending: { icon: "⏸", label: "Pending Launch", className: "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400" },
  none: { icon: "—", label: "Not Assigned", className: "text-slate-300 dark:text-slate-600" },
}

interface MatrixColumn {
  id: string
  label: string
}

interface MatrixRow {
  id: string
  label: string
  cells: Record<string, CellStatus>
}

interface MatrixGridProps {
  columns: MatrixColumn[]
  rows: MatrixRow[]
  columnLabel?: string
  className?: string
  onCellClick?: (rowId: string, colId: string) => void
  footer?: React.ReactNode
}

export function MatrixGrid({
  columns,
  rows,
  columnLabel = "Employee",
  className,
  onCellClick,
  footer,
}: MatrixGridProps) {
  return (
    <div className={cn("overflow-x-auto", className)}>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr>
            <th className="sticky left-0 z-20 bg-background border-b-2 border-r px-3 py-2.5 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider min-w-[160px]">
              {columnLabel}
            </th>
            {columns.map((col) => (
              <th
                key={col.id}
                className="border-b px-2 py-2.5 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider min-w-[48px] max-w-[80px]"
              >
                <div className="[writing-mode:vertical-lr] rotate-180 whitespace-nowrap">
                  {col.label}
                </div>
              </th>
            ))}
            <th className="border-b border-l px-3 py-2.5 text-center text-xs font-semibold text-muted-foreground uppercase tracking-wider min-w-[64px]">
              %
            </th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const statusValues = Object.values(row.cells)
            const completed = statusValues.filter((s) => s === "complete").length
            const pct = columns.length > 0 ? Math.round((completed / columns.length) * 100) : 0
            return (
              <tr key={row.id} className="border-b last:border-0 hover:bg-muted/30 transition-colors">
                <td className="sticky left-0 z-10 bg-background border-r px-3 py-2 font-medium text-sm whitespace-nowrap">
                  {row.label}
                </td>
                {columns.map((col) => {
                  const status = row.cells[col.id] ?? "none"
                  const info = STATUS_ICONS[status]
                  return (
                    <td
                      key={col.id}
                      className={cn(
                        "px-2 py-2 text-center",
                        onCellClick && "cursor-pointer hover:bg-muted/50",
                      )}
                      onClick={() => onCellClick?.(row.id, col.id)}
                      title={`${row.label} — ${col.label}: ${info.label}`}
                    >
                      <span
                        className={cn(
                          "inline-flex items-center justify-center w-7 h-7 rounded text-xs font-bold",
                          info.className,
                        )}
                      >
                        {info.icon}
                      </span>
                    </td>
                  )
                })}
                <td className="border-l px-3 py-2 text-center">
                  <span
                    className={cn(
                      "inline-flex px-2 py-0.5 rounded text-xs font-semibold",
                      pct >= 90 && "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/50 dark:text-emerald-300",
                      pct >= 70 && pct < 90 && "bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300",
                      pct < 70 && "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300",
                    )}
                  >
                    {pct}%
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
      {footer && (
        <div className="mt-3 text-xs text-muted-foreground">
          {footer}
        </div>
      )}
    </div>
  )
}
