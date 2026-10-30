// Unit ratings without an account: the rating belongs to the browser that wrote it.
import { expect, test } from '@playwright/test'

const UNIT = '/units/FIT2102'

test('a guest rates a unit, others see it as someone else\'s, and the author can take it back', async ({ page, browser }) => {
  await page.goto(UNIT)
  const reviews = page.locator('#reviews')
  await expect(reviews).toContainText('FIT2102 还没有人评分')

  // Picking a star on the short prompt opens the full form with that score in it.
  await reviews.locator('.prompt .star').nth(3).click()
  await expect(reviews.getByRole('group', { name: '总体评分' }).getByRole('radio', { name: '4 星，满分 5 星' })).toBeChecked()
  await reviews.getByLabel('你的评价（选填）').fill('Weekly exercises help a lot.')
  await reviews.getByRole('button', { name: '发布评分' }).click()

  await expect(reviews.getByRole('status')).toHaveText('谢谢，评分已保存')
  await expect(reviews.locator('.score')).toContainText('4.0')
  await expect(reviews.locator('.score')).toContainText('1 人评分')
  // The header chip above the Handbook sections picks the new average up too.
  await expect(page.locator('.chip--rating')).toContainText('4.0')

  // Same browser after a reload: still recognised as the author.
  await page.reload()
  await expect(reviews.locator('.own')).toContainText('你的评分')
  await expect(reviews.locator('.own')).toContainText('Weekly exercises help a lot.')

  // A different browser has a different key: it sees the review, not an edit form.
  const stranger = await browser.newContext({ locale: 'zh-CN' })
  const other = await stranger.newPage()
  await other.goto(UNIT)
  const theirs = other.locator('#reviews')
  await expect(theirs.locator('.review')).toContainText('Weekly exercises help a lot.')
  await expect(theirs.locator('.review')).toContainText('未登录的同学')
  await expect(theirs.locator('.own')).toHaveCount(0)
  await expect(theirs).toContainText('评价（1）')
  await stranger.close()

  page.once('dialog', (dialog) => dialog.accept())
  await reviews.getByRole('button', { name: '删除' }).click()
  await expect(reviews.getByRole('status')).toHaveText('你的评分已删除')
  await expect(reviews).toContainText('FIT2102 还没有人评分')
})
