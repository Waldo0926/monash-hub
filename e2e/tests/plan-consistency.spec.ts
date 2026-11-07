import { expect, test, type Page, type Route } from '@playwright/test'

test.use({ serviceWorkers: 'block' })

function deferred<T>() {
  let resolve!: (value: T) => void
  const promise = new Promise<T>(done => { resolve = done })
  return { promise, resolve }
}

async function openPlan(page: Page) {
  await page.addInitScript(() => {
    localStorage.setItem('mh_plans_v1', JSON.stringify({
      activeId: 'test', plans: [{ id: 'test', updatedAt: Date.now(), state: {
        name: 'Synthetic plan', startYear: 2026, years: 3, campus: 'Malaysia', courseCode: '',
        periods: ['First semester', 'Second semester'],
        entries: [{ unit_code: 'FIT1008', year: 2026, teaching_period: 'First semester' }]
      } }]
    }))
  })
  await page.goto('/plan')
}

async function reply(route: Route, issues: unknown[] = []) {
  await route.fulfill({ json: {
    academic_year: 2026, campus: route.request().postDataJSON().campus,
    credit_points: 6, units: 1, unit_credit_points: { FIT1008: 6 },
    unit_titles: { FIT1008: 'Synthetic unit' }, issues
  } })
}

async function renderResponse(page: Page, route: Route, send: () => Promise<void>) {
  const received = page.waitForResponse(response => response.request() === route.request())
  await send()
  await (await received).finished()
  // Let the resolved fetch and Vue's render consume the response before asserting.
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))))
}

test('a slower old campus response cannot replace the current verdict', async ({ page }) => {
  const old = deferred<Route>()
  await page.route('**/api/v1/plan/check', async route => {
    if (route.request().postDataJSON().campus === 'Malaysia') old.resolve(route)
    else await reply(route)
  })
  await openPlan(page)
  const stale = await old.promise
  await page.locator('.settings select').first().selectOption('Clayton')
  const verdict = page.locator('.board [role=status]').first()
  await expect(verdict).toHaveText(/没有问题/)
  await renderResponse(page, stale, () => reply(stale, [{
    unit_code: 'FIT1008', year: 2026, teaching_period: 'First semester',
    severity: 'error', kind: 'not_offered_at_campus', detail: { campus: 'Malaysia', elsewhere: ['Clayton'] }
  }]))
  await expect(verdict).toHaveText(/没有问题/)
  await expect(page.locator('.ucard-issues')).toHaveCount(0)
})

test('an old failure cannot clear loading or set an error for a newer check', async ({ page }) => {
  const old = deferred<Route>()
  const latest = deferred<Route>()
  await page.route('**/api/v1/plan/check', route => {
    if (route.request().postDataJSON().campus === 'Malaysia') old.resolve(route)
    else latest.resolve(route)
  })
  await openPlan(page)
  const stale = await old.promise
  await page.locator('.settings select').first().selectOption('Clayton')
  const current = await latest.promise
  await renderResponse(page, stale, () => stale.fulfill({ status: 422, json: { detail: 'Old check failed' } }))
  const verdict = page.locator('.board [role=status]').first()
  await expect(verdict).toHaveText(/核对中/)
  await expect(page.locator('[role=alert]')).toHaveCount(0)
  await renderResponse(page, current, () => reply(current))
  await expect(verdict).toHaveText(/没有问题/)
})

test('unverified requisites warn and retain a direct official source link', async ({ page }) => {
  const source = 'https://handbook.monash.edu/2026/units/FIT1008'
  await page.route('**/api/v1/plan/check', route => reply(route, [{
    unit_code: 'FIT1008', year: 2026, teaching_period: 'First semester',
    severity: 'warning', kind: 'unverified_requisite', detail: { source_url: source }
  }]))
  await openPlan(page)
  await expect(page.locator('.ucard-issues')).toContainText('需要人工核对')
  await expect(page.locator('.ucard-issues a')).toHaveAttribute('href', source)
  await expect(page.locator('.board [role=status]').first()).not.toHaveText(/没有问题/)
})
