// Both desktop and phone use the disposable stack's synthetic notices and fees.
import { expect, test } from '@playwright/test'

test('fees and future intake dates do not override a current programme notice', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/fees')
  const filter = page.getByLabel(/筛选当前申请通知|Filter current application notices/)
  await expect(filter).toBeVisible()
  await filter.selectOption('closed')
  await expect(page).toHaveURL(/admissions=closed/)
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await expect(page.locator('.tr .name')).toContainText('Master of Professional Counselling')
  await expect(page.locator('.admissions-notice')).toContainText(/关闭申请|closed notice/)
  await page.reload()
  await expect(filter).toHaveValue('closed')
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await filter.selectOption('not_verified')
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await expect(page.locator('.tr .name')).toContainText('Bachelor of Psychology')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true)
  expect(errors).toEqual([])
})
