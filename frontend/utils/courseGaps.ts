/** Conservative hints, NOT official mandatory-unit eligibility determinations.
 * A leaf with exactly one unit may be a required unit; never infer one from
 * alternatives, elective groups or a multi-unit list.
 */
export interface DegreeNode {
  title?: string | null
  connector?: string | null
  free_elective?: boolean | null
  items?: { type?: string | null; code?: string | null }[]
  containers?: DegreeNode[]
}
export function possibleMissingExplicitUnits(nodes: DegreeNode[], planned: string[]) {
  const have = new Set(planned.map(code => code.toUpperCase()))
  const seen = new Set<string>()
  const missing: { code: string; part: string }[] = []
  const visit = (node: DegreeNode, parent: string, alternative: boolean) => {
    const title = node.title || parent
    const choice = alternative || /^(or|any)$/i.test(node.connector || '')
      || /\b(choose|select|either|any of|options?)\b/i.test(node.title || '')
    if (choice || node.free_elective) return
    const items = node.items || []
    if (!(node.containers || []).length && items.length === 1 && items[0]?.type === 'unit') {
      const code = (items[0]?.code || '').toUpperCase()
      if (/^[A-Z]{3,4}\d{4}$/.test(code) && !have.has(code) && !seen.has(code)) {
        missing.push({ code, part: title || parent })
        seen.add(code)
      }
    }
    for (const child of node.containers || []) visit(child, title || parent, choice)
  }
  for (const node of nodes) visit(node, node.title || '', false)
  return missing
}
