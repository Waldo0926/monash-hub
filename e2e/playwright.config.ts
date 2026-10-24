// Browser tests against the real stack: PostgreSQL, the API, the built Nuxt
// server, and a small proxy that gives them one origin the way nginx does in
// production. See README.md in this folder for running them locally.
import { defineConfig, devices } from '@playwright/test'

const PORT = Number(process.env.E2E_PORT || 3100)
const API_PORT = Number(process.env.E2E_API_PORT || 8100)
const WEB_PORT = Number(process.env.E2E_WEB_PORT || 3101)
const DATABASE_URL =
  process.env.DATABASE_URL || 'postgresql+psycopg://monashhub:testpass@localhost:5432/monashhub_e2e'

export default defineConfig({
  testDir: './tests',
  // The ratings tests share one database, so one test at a time.
  workers: 1,
  forbidOnly: !!process.env.CI,
  reporter: process.env.CI ? [['list'], ['html', { open: 'never' }]] : 'list',
  use: {
    baseURL: `http://127.0.0.1:${PORT}`,
    // The site's main readers are Chinese students; their interface is the one tested.
    locale: 'zh-CN',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure'
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'phone', use: { ...devices['Pixel 7'] } }
  ],
  webServer: [
    {
      // Migrate, load the synthetic units, then serve. Seeding empties the
      // Handbook and rating tables, so every run starts from the same state.
      command: `alembic upgrade head && python ../e2e/seed.py && uvicorn app.main:app --host 127.0.0.1 --port ${API_PORT}`,
      cwd: '../backend',
      url: `http://127.0.0.1:${API_PORT}/api/health`,
      env: { DATABASE_URL, CURRENT_ACADEMIC_YEAR: '2026', ENVIRONMENT: 'test' },
      reuseExistingServer: !process.env.CI,
      timeout: 120_000
    },
    {
      // The production build, not `nuxt dev`: hydration problems only show up here.
      command: 'node .output/server/index.mjs',
      cwd: '../frontend',
      url: `http://127.0.0.1:${WEB_PORT}/`,
      env: {
        NITRO_PORT: String(WEB_PORT),
        NITRO_HOST: '127.0.0.1',
        NUXT_API_BASE: `http://127.0.0.1:${API_PORT}/api`
      },
      reuseExistingServer: !process.env.CI,
      timeout: 60_000
    },
    {
      command: 'node proxy.mjs',
      url: `http://127.0.0.1:${PORT}/api/health`,
      env: { E2E_PORT: String(PORT), E2E_API_PORT: String(API_PORT), E2E_WEB_PORT: String(WEB_PORT) },
      reuseExistingServer: !process.env.CI
    }
  ]
})
