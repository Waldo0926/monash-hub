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
