import { defineConfig } from '@playwright/test';

// Load .env when present (Node >= 20.12); CI can set the variables directly.
try {
  process.loadEnvFile();
} catch {
  // no .env file: fall back to the defaults below
}

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  reporter: 'list',
  use: {
    baseURL: process.env.BASE_URL ?? 'https://www.dili.com',
    trace: 'on-first-retry',
  },
});
