import { expect, test } from '@playwright/test'

test('import retains each retake and appends attempts for an existing code', async ({ page }) => {
  await page.goto('/marks')
  await page.getByRole('button', { name: '导入', exact: true }).click()
  await page.locator('.paste-box').fill('FIT1008 6 40 N\nFIT1008 6 80 HD')
  await page.getByRole('button', { name: '加入这些课程', exact: true }).click()
  const rows = page.locator('li.row')
  await expect(rows).toHaveCount(2)
  await expect(rows.nth(0).locator('input[type=number]').nth(0)).toHaveValue('40')
  await expect(rows.nth(1).locator('input[type=number]').nth(0)).toHaveValue('80')

  await page.getByRole('button', { name: '导入', exact: true }).click()
  await page.locator('.paste-box').fill('FIT1008 6 70 D')
  await page.getByRole('button', { name: '加入这些课程', exact: true }).click()
  await expect(rows).toHaveCount(3)
  await page.reload()
  await expect(rows).toHaveCount(3)
})
