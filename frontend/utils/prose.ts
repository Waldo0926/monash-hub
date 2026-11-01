/**
 * Joining interface strings in the reader's language.
 *
 * Chinese UI strings carry no closing 。 (docs/CHINESE-COPY-STYLE.md), so two
 * of them set side by side need the full stop put back between them, and a
 * Chinese list takes 、 rather than a comma. Japanese strings already end in 。.
 */
export function joinSentences(parts: (string | false | null | undefined)[], locale: string): string {
  const list = parts.filter((p): p is string => !!p)
  if (locale === 'zh') return list.map((p, i) => i < list.length - 1 && !/[。！？]$/.test(p) ? `${p}。` : p).join('')
  if (locale === 'ja') return list.join('')
  return list.join(' ')
}

export function joinList(items: string[], locale: string): string {
  return items.join(locale === 'zh' || locale === 'ja' ? '、' : ', ')
}
