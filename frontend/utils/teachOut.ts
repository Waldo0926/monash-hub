/**
 * A short label for a faculty's "Change" cell, for the tag on a degree line.
 *
 * The faculty's wording is shown in full on the unit page. This only shortens it
 * for a chip, and only for the three shapes the tables use; anything else is
 * returned exactly as published rather than paraphrased.
 */
const LABELS: Record<string, { gone: string; renamed: string; last: (year: string, period: string) => string }> = {
  zh: { gone: '不再开设', renamed: '已更名', last: (y, p) => `最后一次开设：${y} ${p}` },
  ja: { gone: '開講終了', renamed: '名称変更', last: (y, p) => `最終開講：${y} ${p}` },
  ko: { gone: '개설 종료', renamed: '명칭 변경', last: (y, p) => `마지막 개설: ${y} ${p}` }
}

export function teachOutLabel(change: string, locale: string): string {
  const text = change.replace(/\s+/g, ' ').trim()
  const words = LABELS[locale]
  if (!words) return text
  if (/^no longer offered$/i.test(text)) return words.gone
  if (/^renamed$/i.test(text)) return words.renamed
  const last = /^final offering (S1|S2|FY|Summer[^0-9]*) ?(\d{4})$/i.exec(text)
  if (last) return words.last(last[2]!, last[1]!)
  return text
}

export type TeachOutRegion = 'malaysia' | 'australia'

/**
 * Which faculty page speaks for a campus. Monash Malaysia's School of IT keeps
 * its own list; the Faculty of IT's page on monash.edu is for the Australian
 * campuses. Same rule as region() in backend/app/knowledge/teach_out.py.
 */
export function teachOutRegion(campus: string | null | undefined): TeachOutRegion {
  return campus === 'Malaysia' ? 'malaysia' : 'australia'
}

/** The entries one campus's page lists. A page for every campus counts for both. */
export function teachOutFor<T extends { applies_to?: string | null }>(entries: T[], region: TeachOutRegion): T[] {
  return entries.filter(e => !e.applies_to || e.applies_to === region || e.applies_to === 'all')
}
