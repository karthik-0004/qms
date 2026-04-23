"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

type ProductId = "qms" | "em" | "ccv" | null;
type Theme = "light" | "dark" | "system";

interface UIState {
  sidebarOpen: boolean;
  sidebarCollapsed: boolean;
  activeProduct: ProductId;
  theme: Theme;
  commandPaletteOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  setActiveProduct: (product: ProductId) => void;
  setTheme: (theme: Theme) => void;
  setCommandPaletteOpen: (open: boolean) => void;
}

export const useUIStore = create<UIState>()(
  persist(
    (set) => ({
      sidebarOpen: true,
      sidebarCollapsed: false,
      activeProduct: null,
      theme: "system",
      commandPaletteOpen: false,

      setSidebarOpen: (sidebarOpen) => set({ sidebarOpen }),
      toggleSidebar: () => set((s) => ({ sidebarOpen: !s.sidebarOpen })),
      setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
      setActiveProduct: (activeProduct) => set({ activeProduct }),
      setTheme: (theme) => set({ theme }),
      setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
    }),
    {
      name: "rainer-ui",
      partialize: (state) => ({
        sidebarCollapsed: state.sidebarCollapsed,
        activeProduct: state.activeProduct,
        theme: state.theme,
      }),
    }
  )
);
