import { expect, test } from '@playwright/test'

async function comparisonPage(page: import('@playwright/test').Page, wrongYear = false) {
  if (wrongYear) await page.route('**/api/v1/units/TST1001?*', route => {
    const year = Number(new URL(route.request().url()).searchParams.get('year'))
    return route.fulfill({ json: { unit_code: 'TST1001', academic_year: wrongYear ? 2024 : year,
      title: 'Synthetic comparison', credit_points: '6', has_exam: null,
      offerings: [], assessments: [], requisites: [],
      source_url: `https://handbook.monash.edu/${year}/units/TST1001`, last_checked: null } })
  })
  await page.goto('/units/compare')
  await page.getByPlaceholder('FIT2102').fill('TST1001')
  await page.locator('.compare-form select').nth(0).selectOption('2026')
  await page.locator('.compare-form select').nth(1).selectOption('2027')
  await page.getByRole('button', { name: /比较变化|^Compare$/ }).click()
}

test('completed results keep their original year labels when selection changes', async ({ page }) => {
  await comparisonPage(page)
  await expect(page.locator('.comparison-context')).toHaveText('TST1001 · 2026 → 2027')
  await expect(page.locator('.compare-warning')).toContainText(/资料不足|Insufficient source data/)
  await page.locator('.compare-form select').nth(0).selectOption('2025')
  await expect(page.locator('.comparison-context')).toHaveText('TST1001 · 2026 → 2027')
  await expect(page.locator('.compare-warning').first()).toContainText(/选择已改变|Selection changed/)
  await expect(page.locator('.compare-sources a').first()).toHaveAttribute('href', /2026\/units\/TST1001$/)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true)
})

test('an API response for another year is rejected rather than mislabeled', async ({ page }) => {
  await comparisonPage(page, true)
  await expect(page.getByRole('alert')).toContainText(/暂时无法读取|Could not read/)
  await expect(page.locator('.comparison-context')).toHaveCount(0)
})
