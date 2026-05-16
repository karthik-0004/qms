"use client"

import { cn } from "@/lib/utils"

interface WorkflowStep {
  key: string
  label: string
  icon?: string
}

interface WorkflowStepBarProps {
  steps: WorkflowStep[]
  currentStep: string
  completedSteps?: string[]
  className?: string
}

export function WorkflowStepBar({
  steps,
  currentStep,
  completedSteps = [],
  className,
}: WorkflowStepBarProps) {
  const currentIndex = steps.findIndex((s) => s.key === currentStep)

  return (
    <div className={cn("w-full", className)}>
      <div className="flex items-center justify-between">
        {steps.map((step, i) => {
          const isCompleted = completedSteps.includes(step.key)
          const isCurrent = step.key === currentStep
          const isPending = !isCompleted && !isCurrent

          return (
            <div key={step.key} className="flex items-center flex-1 last:flex-none">
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "flex items-center justify-center w-8 h-8 rounded-full border-2 text-xs font-bold transition-colors",
                    isCompleted && "bg-emerald-500 border-emerald-500 text-white",
                    isCurrent && "border-blue-500 text-blue-600 bg-blue-50 dark:bg-blue-950 dark:text-blue-400",
                    isPending && "border-slate-300 text-slate-400 bg-white dark:bg-slate-800 dark:border-slate-600",
                  )}
                >
                  {isCompleted ? "✓" : step.icon ?? i + 1}
                </div>
                <span
                  className={cn(
                    "text-xs mt-1.5 text-center whitespace-nowrap transition-colors",
                    isCompleted && "text-emerald-600 font-medium dark:text-emerald-400",
                    isCurrent && "text-blue-600 font-medium dark:text-blue-400",
                    isPending && "text-slate-400 dark:text-slate-500",
                  )}
                >
                  {step.label}
                </span>
              </div>
              {i < steps.length - 1 && (
                <div
                  className={cn(
                    "flex-1 h-0.5 mx-2 mt-[-1.5rem]",
                    i < currentIndex ? "bg-emerald-400" : "bg-slate-200 dark:bg-slate-700",
                  )}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
