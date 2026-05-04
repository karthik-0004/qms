/** Seed items for in-app notifications until tenant API exposes real inbox data. */

export type DemoNotificationSeed = {
  id: string;
  title: string;
  body: string;
  /** ISO datetime */
  createdAt: string;
};

export const DEMO_NOTIFICATION_SEEDS: DemoNotificationSeed[] = [
  {
    id: "demo-welcome",
    title: "Welcome to Rainer",
    body: "Your workspace is ready. Explore QMS, EM, and CCV modules from the sidebar.",
    createdAt: new Date().toISOString(),
  },
  {
    id: "demo-review",
    title: "Scheduled review reminder",
    body: "Quarterly document review cycle starts next week.",
    createdAt: new Date(Date.now() - 3600_000).toISOString(),
  },
];
