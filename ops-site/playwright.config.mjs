import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/browser',
  testMatch: '*.spec.mjs',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 45_000,
  expect: { timeout: 10_000 },
  reporter: process.env.CI ? 'line' : 'list',
  use: {
    baseURL: 'http://127.0.0.1:3100',
    browserName: 'chromium',
    viewport: { width: 1280, height: 800 },
    trace: 'off',
    screenshot: 'off',
    video: 'off',
  },
  webServer: {
    command: 'npm run start -- -p 3100',
    // This variable applies only to the loopback browser test server.
    // Vercel previews/prod must never expose this gated draft route.
    env: { KAIGO_OPS_SOURCE_GUIDE_REVIEW: 'local' },
    url: 'http://127.0.0.1:3100/',
    timeout: 120_000,
    reuseExistingServer: !process.env.CI,
  },
});
