import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "jsdom",
    exclude: [
      "**/node_modules/**",
      "**/.next/**",
      "**/dist/**",
      "**/build/**",
      "e2e/**",
      "**/playwright-report/**",
      "**/test-results/**",
    ],
  },
});

