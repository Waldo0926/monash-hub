// The home page: the row of searches under the search box.
import { expect, test } from '@playwright/test'

test('the row under the search box lists what people searched for lately', async ({ page }) => {
  await page.goto('/')
  const row = page.locator('.often')
  await expect(row).toContainText('最近常搜')
  // The seed has three terms searched on two days, most searched first.
  await expect(row.getByRole('button')).toHaveText(['FIT1008', 'census date', 'FIT2004'])
  await row.getByRole('button', { name: 'census date' }).click()
  await expect(page).toHaveURL(/\/search\?q=census(\+|%20)date/)
})
