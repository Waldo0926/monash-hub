// The installed app: the manifest a phone reads, pages that open with no
// signal, and the hint that tells a student how to add the site.
import { expect, test, type Page } from '@playwright/test'

/** Wait until the service worker has taken over this tab. */
async function controlled(page: Page) {
  await page.waitForFunction(async () => {
    await navigator.serviceWorker.ready
    return !!navigator.serviceWorker.controller
  })
}

async function cachedUrls(page: Page): Promise<string[]> {
  return page.evaluate(async () => {
    const urls: string[] = []
    for (const name of await caches.keys()) {
      for (const request of await (await caches.open(name)).keys()) urls.push(request.url)
    }
    return urls
  })
}

test('the manifest names the app and describes it in the reader\'s language', async ({ request }) => {
  const response = await request.get('/manifest.webmanifest', { headers: { 'Accept-Language': 'zh-CN' } })
  expect(response.status()).toBe(200)
  expect(response.headers()['content-type']).toContain('application/manifest+json')
  const manifest = await response.json()
  expect(manifest.name).toBe('Monash Hub')
  expect(manifest.display).toBe('standalone')
  expect(manifest.start_url).toBe('/')
  expect(manifest.description).toBe('Monash 课程、学位、官方指南和学生社区')
  expect(manifest.shortcuts.map((s: any) => s.name)).toContain('课程')
  for (const icon of manifest.icons) {
    const file = await request.get(icon.src)
    expect(file.status(), icon.src).toBe(200)
  }

  const english = await request.get('/manifest.webmanifest', { headers: { Cookie: 'mh_locale=en' } })
  expect((await english.json()).description).toBe('Monash units, degrees, official guides and student community')
})

test('a unit page read once opens again with no network, and says it is a saved copy', async ({ page, context }) => {
  await page.goto('/')
  await controlled(page)
  await page.goto('/units/FIT2004')
  await expect(page.getByRole('heading', { level: 1 })).toContainText('FIT2004')

  // Ratings and community threads are live: never saved, even though the page asked for them.
  await expect.poll(async () => (await cachedUrls(page)).some(u => u.endsWith('/units/FIT2004'))).toBe(true)
  const saved = await cachedUrls(page)
  expect(saved.some(u => u.includes('/api/v1/reviews/'))).toBe(false)
  expect(saved.some(u => u.includes('/api/v1/community/'))).toBe(false)

  await context.setOffline(true)
  await page.reload()
  await expect(page.getByRole('heading', { level: 1 })).toContainText('FIT2004')
  await expect(page.getByRole('status').filter({ hasText: '现在没有网络' })).toBeVisible()

  // A page never opened before gets the offline page, which lists what is saved.
  await page.goto('/community')
  await expect(page.getByRole('heading', { level: 1 })).toHaveText('现在没有网络')
  await expect(page.getByRole('link', { name: /FIT2004/ })).toBeVisible()

  await context.setOffline(false)
  await page.getByRole('button', { name: '重试' }).click()
  await expect(page).toHaveURL(/\/community$/)
  await expect(page.getByRole('heading', { level: 1 })).not.toHaveText('现在没有网络')
})

test('a unit that is not found is not saved, so it cannot stand in for a real page later', async ({ page }) => {
  await page.goto('/')
  await controlled(page)
  const response = await page.goto('/units/FIT9999')
  expect(response?.status()).toBe(404)
  await page.goto('/units/FIT2004')
  await expect.poll(async () => (await cachedUrls(page)).some(u => u.endsWith('/units/FIT2004'))).toBe(true)
  expect((await cachedUrls(page)).some(u => u.includes('FIT9999'))).toBe(false)
})

test('the add-to-home-screen hint waits a few pages on a phone and stays closed once closed', async ({ page, isMobile }) => {
  const hint = page.getByRole('complementary', { name: '添加到手机主屏幕' })
  await page.goto('/units/FIT2004')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(hint).toHaveCount(0)

  await page.goto('/units/FIT1008')
  await page.goto('/guides')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  if (!isMobile) {
    // Desktop readers get the steps in the footer only.
    await expect(hint).toHaveCount(0)
    return
  }
  await expect(hint).toBeVisible()
  await hint.getByRole('button', { name: '怎么添加' }).click()
  // Playwright's Pixel 7 is Chrome on Android; the steps name its menu.
  await expect(hint).toContainText('添加到主屏幕')

  await hint.getByRole('button', { name: '不再提示' }).click()
  await expect(hint).toHaveCount(0)
  await page.goto('/units/FIT2102')
  await expect(page.getByRole('heading', { level: 1 })).toBeVisible()
  await expect(hint).toHaveCount(0)
})
