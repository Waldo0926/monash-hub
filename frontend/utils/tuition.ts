/**
 * Small helpers for showing the Monash Malaysia fee rows the API reads out of
 * /ugfees and /pgfees. Kept apart from the components so they can be tested.
 */

export type FeeAmount = { value: number | null; written: string; label: string | null }

export type FeeRow = {
  title: string
  title_zh: string | null
  covers: string[]
  school: string
  source: string
  duration: string | null
  mode: string | null
  variant: string | null
  basis: 'per_year' | 'full_course' | null
  domestic: FeeAmount[]
  international: FeeAmount[]
  unreadable: boolean
  note: { en: string; zh: string; url?: string } | null
}

/**
 * "RM 48,480". Grouping is done by hand rather than with Intl so the server
 * and the browser print the same string. An amount Monash printed wrongly
 * ("74,40") is shown as written, never repaired.
 */
export function formatAmount(amount: FeeAmount): string {
  if (amount.value == null) return `RM ${amount.written}`
  return `RM ${String(amount.value).replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`
}

/** The Chinese name where we have one, otherwise the English one Monash uses. */
export function feeTitle(row: Pick<FeeRow, 'title' | 'title_zh'>, locale: string): string {
  return locale === 'zh' && row.title_zh ? row.title_zh : row.title
}

/** Notes are written in English and Chinese. Japanese and Korean get the English. */
export function feeNote(note: FeeRow['note'], locale: string): string {
  if (!note) return ''
  return locale === 'zh' ? note.zh : note.en
}

/** Rows whose title, Chinese name or covered degrees contain the query. */
export function filterFees<T extends Pick<FeeRow, 'title' | 'title_zh' | 'covers'>>(rows: T[], query: string): T[] {
  const q = query.trim().toLowerCase()
  if (!q) return rows
  return rows.filter(row =>
    [row.title, row.title_zh ?? '', ...row.covers].some(text => text.toLowerCase().includes(q))
  )
}
