"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

import { DEMO_NOTIFICATION_SEEDS } from "@/data/demo-notifications";

export interface InAppNotification {
  id: string;
  title: string;
  body: string;
  createdAt: string;
  read: boolean;
}

interface NotificationsState {
  items: InAppNotification[];
  markRead: (id: string) => void;
  markAllRead: () => void;
  seedIfEmpty: () => void;
}

function seedsToItems(seeds: typeof DEMO_NOTIFICATION_SEEDS): InAppNotification[] {
  return seeds.map((s) => ({
    id: s.id,
    title: s.title,
    body: s.body,
    createdAt: s.createdAt,
    read: false,
  }));
}

export const useNotificationsStore = create<NotificationsState>()(
  persist(
    (set, get) => ({
      items: [],

      seedIfEmpty: () => {
        const { items } = get();
        if (items.length === 0) {
          set({ items: seedsToItems(DEMO_NOTIFICATION_SEEDS) });
        }
      },

      markRead: (id) =>
        set((state) => ({
          items: state.items.map((n) => (n.id === id ? { ...n, read: true } : n)),
        })),

      markAllRead: () =>
        set((state) => ({
          items: state.items.map((n) => ({ ...n, read: true })),
        })),
    }),
    {
      name: "rainer-in-app-notifications",
      partialize: (state) => ({ items: state.items }),
    }
  )
);
