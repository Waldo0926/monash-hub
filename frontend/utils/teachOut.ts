/**
 * A short label for a faculty's "Change" cell, for the tag on a degree line.
 *
 * The faculty's wording is shown in full on the unit page. This only shortens it
 * for a chip, and only for the three shapes the tables use; anything else is
 * returned exactly as published rather than paraphrased.
 */
export function teachOutLabel(change: string, zh: boolean): string {
  const text = change.replace(/\s+/g, ' ').trim()
  if (!zh) return text
  if (/^no longer offered$/i.test(text)) return '不再开设'
  if (/^renamed$/i.test(text)) return '已更名'
  const last = /^final offering (S1|S2|FY|Summer[^0-9]*) ?(\d{4})$/i.exec(text)
  if (last) return `最后一次开设：${last[2]} ${last[1]}`
  return text
}
