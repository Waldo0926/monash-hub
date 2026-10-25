// The course map: units dropped into semesters and checked against the Handbook.
import { expect, test, type Page } from '@playwright/test'

/** Opens the add-unit dialog on a slot, picks one unit and closes it again. */
async function addUnit(page: Page, slot: string, code: string) {
  await page.getByRole('button', { name: `添加课程: ${slot}` }).first().click()
  const dialog = page.getByRole('dialog')
  await dialog.getByRole('textbox').fill(code)
  await dialog.getByRole('option', { name: new RegExp(code) }).click()
  await dialog.getByRole('button', { name: `添加到 ${slot}` }).click()
  await expect(dialog.getByRole('status')).toContainText(`${code} 已加入`)
  await dialog.getByRole('button', { name: '关闭' }).click()
  await expect(dialog).toBeHidden()
}

function card(page: Page, code: string) {
  return page.locator('.ucard').filter({ has: page.getByRole('link', { name: code, exact: true }) })
}

test.beforeEach(async ({ page }) => {
  await page.goto('/plan')
  // Every slot name carries its year, so pin it rather than follow the clock.
  await page.getByLabel('起始年').fill('2026')
  await page.getByLabel('起始年').blur()
  await expect(page.getByRole('heading', { name: /第 1 年\s*2026/ })).toBeVisible()
})

test('a unit placed before its prerequisite is flagged until the order is fixed', async ({ page }) => {
  const verdict = page.locator('.board').getByRole('status').first()

  await addUnit(page, '第一学期, 2026', 'FIT2004')
  await expect(card(page, 'FIT2004')).toContainText('需要先修完 FIT1008')
  await expect(verdict).toHaveText(/有问题：1 处/)

  await addUnit(page, '第二学期, 2026', 'FIT1008')
  // FIT1008 is there now, but after FIT2004, so it still does not count.
  await expect(card(page, 'FIT2004')).toContainText('需要先修完 FIT1008')

  await card(page, 'FIT2004').getByLabel('移到… FIT2004').selectOption({ label: '第一学期, 2027' })
  await expect(verdict).toHaveText(/没有问题/)
  await expect(card(page, 'FIT2004')).not.toContainText('需要先修完')
})

test('a unit put in a semester it does not run in says when it does', async ({ page }) => {
  await addUnit(page, '第一学期, 2026', 'FIT2102')
  await expect(card(page, 'FIT2102')).toContainText('这个教学期不开。本校区开在：第二学期')
})

test('the plan stays in this browser across a reload, removals included', async ({ page }) => {
  await addUnit(page, '第一学期, 2026', 'FIT1008')
  await addUnit(page, '第二学期, 2026', 'FIT2004')
  await page.reload()
  await expect(card(page, 'FIT1008')).toBeVisible()
  await expect(card(page, 'FIT2004')).toBeVisible()

  await page.getByRole('button', { name: '移除这门课: FIT2004' }).click()
  await expect(card(page, 'FIT2004')).toHaveCount(0)
  await page.reload()
  await expect(card(page, 'FIT1008')).toBeVisible()
  await expect(card(page, 'FIT2004')).toHaveCount(0)
})

test('an empty plan says what to do first, and the problem count leads to the unit', async ({ page }) => {
  const steps = page.locator('.start')
  await expect(steps).toContainText('选校区和专业与学位')
  await expect(page.locator('.plan-title')).toContainText('只保存在这个浏览器')

  await addUnit(page, '第一学期, 2026', 'FIT2004')
  await expect(steps).toHaveCount(0)

  await page.getByRole('button', { name: /有问题：1 处/ }).click()
  await expect(card(page, 'FIT2004').getByRole('link', { name: 'FIT2004', exact: true })).toBeFocused()
})

test('export and print sit in the More menu', async ({ page }) => {
  // The phone's bottom bar has its own 更多, so the menu is found by where it is.
  await page.getByRole('toolbar').getByText('更多', { exact: true }).click()
  await expect(page.getByRole('button', { name: '导出' })).toBeVisible()
  await expect(page.getByRole('button', { name: '打印' })).toBeVisible()
})
