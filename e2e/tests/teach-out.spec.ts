// A faculty notice that a unit is closing. Monash Malaysia and the Australian
// campuses publish separate lists and change units on different dates, so a
// student sees both, their own campus first, each with a link to its page.
import { expect, test } from '@playwright/test'

const MY = 'https://www.monash.edu.my/it/e2e-teach-out'
const AU = 'https://www.monash.edu/it/e2e-teach-out'

test('searching a unit that is closing shows both campuses and links both lists', async ({ page }) => {
  await page.goto('/search?q=FIT2004')
  const notice = page.locator('.teach').first()
  await expect(notice).toBeVisible()
  const regions = notice.locator('.region')
  await expect(regions).toHaveCount(2)
  await expect(regions.nth(0).getByRole('heading')).toHaveText('马来西亚校区')
  await expect(regions.nth(0)).toContainText('Final offering S2 2026')
  await expect(regions.nth(0)).toContainText('Replace with FIT3901 from 2027 (S1)')
  await expect(regions.nth(1).getByRole('heading')).toHaveText('澳洲校区')
  await expect(regions.nth(1)).toContainText('No longer offered')
  await expect(regions.nth(0).getByRole('link')).toHaveAttribute('href', MY)
  await expect(regions.nth(1).getByRole('link')).toHaveAttribute('href', AU)
})

test('a campus whose list leaves the unit out says so and still links its list', async ({ page }) => {
  await page.goto('/units/FIT2102')
  const regions = page.locator('.teach .region')
  await expect(regions).toHaveCount(2)
  await expect(regions.nth(0)).toContainText('这个校区的列表里没有这门课的变更说明')
  await expect(regions.nth(0)).not.toContainText('FIT3902')
  await expect(regions.nth(0).getByRole('link')).toHaveAttribute('href', MY)
  await expect(regions.nth(1)).toContainText('Replace with FIT3902 from 2027')
})
