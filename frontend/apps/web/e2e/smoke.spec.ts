import { test, expect } from "@playwright/test";

test.describe("Smoke Tests", () => {
  test("login page loads", async ({ page }) => {
    await page.goto("/login");
    await expect(page).toHaveTitle(/Rainer/i);
    await expect(page.locator("input[type='email'], input[name='email']")).toBeVisible();
  });

  test("unauthenticated user is redirected to login", async ({ page }) => {
    await page.goto("/dashboard");
    await page.waitForURL(/\/login/);
    expect(page.url()).toContain("/login");
  });

  test("sidebar navigation renders", async ({ page }) => {
    // This test assumes an authenticated session via storageState
    test.skip(!process.env.AUTH_STORAGE_STATE, "Requires auth storage state");
    await page.goto("/dashboard");
    await expect(page.locator("nav")).toBeVisible();
  });
});
