// Both desktop and phone use the disposable stack's synthetic notices and fees.
import { expect, test } from '@playwright/test'

test('fees and future intake dates do not override a current programme notice', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', e => errors.push(e.message))
  await page.goto('/fees')
  await expect(page.locator('.source-coverage')).toContainText(/来源索引|source/);
  const filter = page.getByLabel(/筛选当前申请通知|Filter current application notices/)
  await expect(filter).toBeVisible()
  await filter.selectOption('closed')
  await expect(page).toHaveURL(/admissions=closed/)
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await expect(page.locator('.tr .name')).toContainText('Master of Professional Counselling')
  await expect(page.locator('.admissions-notice')).toContainText(/关闭申请|closed notice/)
  await expect(page.locator('.admissions-notice')).toContainText(/收费表的课程链接|fee-table link differs/)
  await page.reload()
  await expect(filter).toHaveValue('closed')
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await filter.selectOption('not_verified')
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await expect(page.locator('.tr .name')).toContainText('Bachelor of Psychology')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true)
  expect(errors).toEqual([])
})

test('selected-intake proof cannot leak into another year or period', async ({ page }) => {
  await page.goto('/fees?year=2027&intake=october&intake_status=open')
  const filter = page.getByLabel(/筛选所选批次的申请状态|Filter selected-intake application status/)
  await expect(filter).toHaveValue('open')
  await expect(page.locator('.tr .name')).toHaveCount(1)
  await expect(page.locator('.selected-intake')).toContainText(/明确显示开放|Explicit open/)
  await expect(page.locator('.admissions-notice strong').first()).toContainText(/未核实|Not verified/)

  await page.getByLabel('Intake year', { exact: true }).selectOption('2028')
  await expect(page).toHaveURL(/year=2028/)
  await expect(page.locator('.tr .name')).toHaveCount(0)
  await filter.selectOption('not_verified')
  await expect(page.locator('.tr .name')).toHaveCount(2)
  await expect(page.locator('.fee-publication').first()).toContainText(/来源年份.*2027|source year.*2027/)
  await expect(page.locator('.intake-listed')).toHaveCount(0)
  await page.reload()
  await expect(page.getByLabel('Intake year', { exact: true })).toHaveValue('2028')

  await page.getByLabel('Intake year', { exact: true }).selectOption('2027')
  await page.getByLabel('Intake period', { exact: true }).selectOption('february')
  await expect(page.locator('.tr .name')).toHaveCount(2)
  await expect(page.locator('.selected-intake').first()).toContainText(/未核实|Not verified/)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1)).toBe(true)
})
