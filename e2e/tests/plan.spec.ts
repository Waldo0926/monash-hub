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

test('with a degree chosen, the dialog offers its units before anything is typed', async ({ page }) => {
  await page.getByLabel('专业与学位').selectOption('C9001')
  await expect(page.getByText('Part A. Synthetic core')).toBeVisible()

  await page.getByRole('button', { name: '添加课程: 第一学期, 2026' }).first().click()
  const dialog = page.getByRole('dialog')
  await expect(dialog.getByRole('heading', { name: '专业与学位里还没排的课（3 门）' })).toBeVisible()
  await expect(dialog.getByRole('option')).toHaveCount(3)
  // Each row says which part of the degree it counts towards.
  await expect(dialog.getByRole('option', { name: /FIT2085/ })).toContainText('A')

  await dialog.getByRole('option', { name: /FIT1008/ }).click()
  await dialog.getByRole('button', { name: '添加到 第一学期, 2026' }).click()
  await expect(dialog.getByRole('status')).toContainText('FIT1008 已加入')
  // What is on the map leaves the list.
  await expect(dialog.getByRole('option')).toHaveCount(2)
  await expect(dialog.getByRole('option', { name: /FIT1008/ })).toHaveCount(0)

  // Typing still searches everything, the degree's list or not.
  await dialog.getByRole('textbox').fill('FIT2102')
  await expect(dialog.getByRole('option', { name: /FIT2102/ })).toBeVisible()
})

test('an unfinished part of the degree opens the dialog on what it still wants', async ({ page }) => {
  await page.getByLabel('专业与学位').selectOption('C9001')
  await addUnit(page, '第一学期, 2026', 'FIT1008')

  await page.getByRole('button', { name: '找Part A. Synthetic core的课' }).click()
  // The first semester with room is where a unit from here goes.
  const dialog = page.getByRole('dialog', { name: '添加课程到 第一学期, 2026' })
  await expect(dialog.getByRole('heading', { name: 'Part A. Synthetic core还缺的课' })).toBeVisible()
  await expect(dialog.getByRole('option')).toHaveCount(2)
  await expect(dialog.getByRole('option', { name: /FIT2004/ })).toBeVisible()
  await expect(dialog.getByRole('option', { name: /FIT2085/ })).toBeVisible()

  await dialog.getByRole('button', { name: '看整个专业与学位' }).click()
  await expect(dialog.getByRole('heading', { name: '专业与学位里还没排的课（2 门）' })).toBeVisible()
})

// A plan as one line of text, for moving it between devices without a file.
const FRIEND = 'MH1|%E6%9C%8B%E5%8F%8B%E7%9A%84|2026|3|Malaysia||S1;S2|FIT1008@0.0,FIT2004@1.0'

test('a pasted plan code arrives as a new plan', async ({ page }) => {
  await page.getByRole('toolbar').getByText('更多', { exact: true }).click()
  await page.getByRole('button', { name: '粘贴规划码' }).click()
  await page.getByLabel('粘贴规划码').fill(`看看这个 ${FRIEND}`)
  await page.getByRole('button', { name: '导入', exact: true }).click()
  await expect(page.getByRole('status').filter({ hasText: '「朋友的」已作为新规划加入' })).toBeVisible()
  await expect(card(page, 'FIT1008')).toBeVisible()
  await expect(card(page, 'FIT2004')).toBeVisible()
})

test('a plan link opens the plan it carries and leaves the code out of the address', async ({ page }) => {
  // Opened fresh, as from a chat message.
  await page.goto('about:blank')
  await page.goto(`/plan#plan=${encodeURIComponent(FRIEND)}`)
  await expect(card(page, 'FIT1008')).toBeVisible()
  await expect(page.getByRole('heading', { name: /第 1 年\s*2026/ })).toBeVisible()
  expect(new URL(page.url()).hash).toBe('')
  // Pasted into the address bar of a tab already on the page: only the hash changes.
  const second = FRIEND.replace('%E6%9C%8B%E5%8F%8B%E7%9A%84', 'again').replace('FIT1008@0.0', 'FIT2102@0.1')
  await page.goto(`/plan#plan=${encodeURIComponent(second)}`)
  await expect(page.getByRole('status').filter({ hasText: '「again」已作为新规划加入' })).toBeVisible()
  await expect(card(page, 'FIT2102')).toBeVisible()
})

test.describe('copying', () => {
  test.use({ permissions: ['clipboard-read', 'clipboard-write'] })
  test('copy plan code puts a link to this plan on the clipboard', async ({ page }) => {
    await addUnit(page, '第一学期, 2026', 'FIT1008')
    await page.getByRole('toolbar').getByText('更多', { exact: true }).click()
    await page.getByRole('button', { name: '复制规划码' }).click()
    await expect(page.getByRole('status').filter({ hasText: '已复制' })).toBeVisible()
    const copied = await page.evaluate(() => navigator.clipboard.readText())
    expect(copied).toContain('/plan#plan=MH1')
    expect(decodeURIComponent(copied)).toContain('FIT1008@0.0')
  })
})
