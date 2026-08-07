import { defineConfig, devices } from "@playwright/test";
import process from "node:process";

const port = Number(process.env.E2E_FRONTEND_PORT ?? 5173);
const frontendBaseURL = process.env.E2E_BASE_URL ?? `http://127.0.0.1:${port}`;
const apiBaseURL = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";

export default defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html"], ["list"]],
  use: {
    baseURL: frontendBaseURL,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
  },
  webServer: {
    command: `npm run dev -- --host 127.0.0.1 --port ${port}`,
    url: frontendBaseURL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      VITE_API_PROXY_TARGET: apiBaseURL,
    },
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
