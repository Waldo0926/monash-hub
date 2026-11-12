import { expect, test } from '@playwright/test'

test.use({ serviceWorkers: 'block' })

test('comparison retains the exact commencement edition and source while inputs change', async ({ page }) => {
  const requests: number[] = []
  await page.route('**/api/v1/courses/C9001?*', route => {
    const year = Number(new URL(route.request().url()).searchParams.get('year'))
    requests.push(year)
    return route.fulfill({ json: {
      course_code: 'C9001', academic_year: year, title: 'Synthetic degree',
      source_url: `https://handbook.monash.edu/${year}/courses/C9001`,
      last_checked: '2026-11-01T00:00:00Z',
      containers: [{ title: `Synthetic requirement ${year}`, credit_points: 24 }]
    } })
  })
  await page.goto('/units/compare?code=TST1001&from=2025&to=2026&course=C9001&commenced=2025')
  const context = page.locator('.commencement-context')
  await expect(context).toContainText('C9001 · 2025')
  await expect(context).toContainText('Synthetic requirement 2025')
  await expect(context.getByRole('link', { name: /2025 Monash Handbook/ })).toHaveAttribute('href', /2025\/courses\/C9001$/)
  await page.getByLabel(/学位入学年份|Degree commencement year/).fill('2024')
  await expect(context).toContainText('C9001 · 2025')
  await expect(page.locator('.compare-warning').first()).toContainText(/选择已改变|Selection changed/)
  expect(requests).toEqual([2025])
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true)
})

test('a missing commencement edition is not replaced by a newer indexed degree', async ({ page }) => {
  const years: number[] = []
  await page.route('**/api/v1/courses/C9001?*', route => {
    years.push(Number(new URL(route.request().url()).searchParams.get('year')))
    return route.fulfill({ status: 404, json: { detail: 'Synthetic missing commencement edition' } })
  })
  await page.addInitScript(() => {
    localStorage.setItem('mh_plans_v1', JSON.stringify({ activeId: 'test', plans: [{
      id: 'test', updatedAt: Date.now(), state: { name: 'Synthetic plan', startYear: 2024,
        years: 3, campus: 'Malaysia', courseCode: 'C9001',
        periods: ['First semester', 'Second semester'], entries: [] }
    }] }))
  })
  await page.goto('/plan')
  await expect(page.locator('.commencement-context')).toHaveAttribute('data-state', 'not_indexed')
  await expect(page.locator('.commencement-context')).toContainText('C9001 · 2024')
  await expect(page.locator('.commencement-context')).toContainText(/没有使用邻近|No nearby/)
  await expect(page.locator('.parts')).toHaveCount(0)
  expect(years).toEqual([2024])
})

test('a degree response for the wrong year cannot supply commencement requirements', async ({ page }) => {
  await page.route('**/api/v1/courses/C9001?*', route => route.fulfill({ json: {
    course_code: 'C9001', academic_year: 2026,
    source_url: 'https://handbook.monash.edu/2026/courses/C9001',
    containers: [{ title: 'Wrong-year requirement' }]
  } }))
  await page.goto('/units/compare?code=TST1001&from=2025&to=2026&course=C9001&commenced=2025')
  await expect(page.locator('.commencement-context')).toHaveAttribute('data-state', 'identity_mismatch')
  await expect(page.locator('.commencement-context')).not.toContainText('Wrong-year requirement')
  await expect(page.locator('.comparison-context')).toContainText('2025 → 2026')
})
