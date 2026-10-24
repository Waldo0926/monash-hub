// The unit page: what a student lands on from a search result or a shared link.
import { expect, test } from '@playwright/test'

test('the server renders the Handbook facts, so a shared link has them before any script runs', async ({ request }) => {
  const response = await request.get('/units/FIT2004')
  expect(response.status()).toBe(200)
  const html = await response.text()
  expect(html).toContain('Synthetic algorithms and data structures')
  expect(html).toContain('https://handbook.monash.edu/2026/units/FIT2004')
})

test('a unit page shows where it runs and leads to its prerequisite', async ({ page }) => {
  const problems: string[] = []
  page.on('pageerror', (error) => problems.push(error.message))
  page.on('console', (message) => {
    if (message.type() === 'error' || /hydration/i.test(message.text())) problems.push(message.text())
  })

  await page.goto('/units/FIT2004')
  await expect(page.getByRole('heading', { level: 1 })).toHaveText(
    'FIT2004 · Synthetic algorithms and data structures'
  )
  const offerings = page.locator('#offerings')
  await expect(offerings.getByRole('row')).toHaveCount(3)
  await expect(offerings).toContainText('第一学期')
  await expect(offerings).toContainText('第二学期')
  await expect(page.locator('#assessment')).toContainText('60%')

  await page.locator('#requisites').getByRole('link', { name: /FIT1008/ }).first().click()
  await expect(page).toHaveURL(/\/units\/FIT1008$/)
  await expect(page.getByRole('heading', { level: 1 })).toContainText('FIT1008')
  // The other direction: FIT1008's page names FIT2004 as what it opens up.
  await expect(page.locator('#requisites')).toContainText('FIT2004')

  expect(problems).toEqual([])
})

test('a code the Handbook does not have says so instead of showing an empty page', async ({ page }) => {
  const response = await page.goto('/units/FIT9999')
  expect(response?.status()).toBe(404)
  await expect(page.getByRole('main').getByRole('alert')).toContainText('没有找到这个内容')
})
