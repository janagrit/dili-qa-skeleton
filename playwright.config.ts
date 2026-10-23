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
  reporter: [
    ['list'],
    ['./reporters/table-summary-reporter.js'],
  ],
  use: {
    // `||` (not `??`) so an empty BASE_URL= in .env still falls back.
    baseURL: process.env.BASE_URL || 'https://www.dili.com',
    trace: 'on-first-retry',
  },
  projects: [
    // Pure engine + registry tests: no browser, no network. This is what CI runs.
    { name: 'logic', testDir: './tests/logic' },
    // UI tests drive the live site through page objects (tests/pages): run on demand, never in CI by default.
    { name: 'ui', testDir: './tests/ui' },
  ],
});
