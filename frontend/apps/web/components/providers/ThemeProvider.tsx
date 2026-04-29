"use client"

import { useEffect } from "react"

import { useUIStore } from "@/lib/stores/ui.store"

type ThemeMode = "light" | "dark" | "system"

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const theme = useUIStore((s) => s.theme) as ThemeMode

  useEffect(() => {
    const root = document.documentElement

    const apply = (mode: ThemeMode) => {
      if (mode === "dark") {
        root.classList.add("dark")
      } else if (mode === "light") {
        root.classList.remove("dark")
      }
    }

    // For "system", we derive from the media query below.
    if (theme !== "system") apply(theme)
  }, [theme])

  useEffect(() => {
    if (theme !== "system") return

    const root = document.documentElement
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)")

    const syncFromSystem = () => {
      if (mediaQuery.matches) {
        root.classList.add("dark")
      } else {
        root.classList.remove("dark")
      }
    }

    syncFromSystem()
    mediaQuery.addEventListener("change", syncFromSystem)

    return () => {
      mediaQuery.removeEventListener("change", syncFromSystem)
    }
  }, [theme])

  return children
}

