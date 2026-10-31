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
  change: FeeChange | null
}

/** One amount compared with the same amount last year. */
export type FeeDelta = { previous: number; diff: number; pct: number | null }

export type FeeChange = {
  year: number
  domestic: (FeeDelta | null)[] | null
  international: (FeeDelta | null)[] | null
  source: string
}

/** The delta for the n-th amount on one side of a row, if there is one. */
export function deltaAt(change: FeeChange | null | undefined, side: 'domestic' | 'international', n: number): FeeDelta | null {
  return change?.[side]?.[n] ?? null
}

/** "+RM 2,880 (+5.3%)", "-RM 400 (-1.2%)". Zero is the caller's to word. */
export function formatDelta(delta: FeeDelta): string {
  const sign = delta.diff > 0 ? '+' : delta.diff < 0 ? '−' : ''
  const amount = String(Math.abs(delta.diff)).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
  const pct = delta.pct == null ? '' : ` (${sign}${Math.abs(delta.pct).toFixed(1)}%)`
  return `${sign}RM ${amount}${pct}`
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
