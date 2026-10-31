// The prerequisite graph: selecting a unit shows its own chain and dims the rest.
import { expect, test } from '@playwright/test'

test('selecting a unit on the graph dims what is not on its chain', async ({ page }) => {
  // FIT1008 unlocks FIT2004 and FIT2085, which have nothing to do with each other.
  await page.goto('/tree?unit=FIT1008&direction=downstream&campus=Malaysia')
  const graph = page.getByRole('img', { name: 'FIT1008 的先修关系图' })
  await expect(graph.locator('.node')).toHaveCount(3)
  await expect(graph.locator('.node--dim')).toHaveCount(0)

  await graph.locator('.node[data-code="FIT2004"]').focus()
  await page.keyboard.press('Enter')

  const toggle = page.getByRole('checkbox', { name: '只看这门课的先修链' })
  await expect(toggle).toBeChecked()
  await expect(page.getByText('这条链上还有 1 门课')).toBeVisible()
  await expect(graph.locator('.node[data-code="FIT2085"]')).toHaveClass(/node--dim/)
  await expect(graph.locator('.node[data-code="FIT1008"]')).not.toHaveClass(/node--dim/)
  await expect(graph.locator('.node[data-code="FIT2004"]')).not.toHaveClass(/node--dim/)

  // The whole graph comes back on request, with the unit still selected.
  await toggle.uncheck()
  await expect(graph.locator('.node--dim')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'FIT2004' })).toBeVisible()
})
