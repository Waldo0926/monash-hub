/**
 * Age is a visibility cue, never evidence that student experience is wrong.
 * A timestamp with no timezone is intentionally treated as UTC to avoid
 * inconsistent SSR/client thresholds.
 */
export function olderThanMonths(value: string | null | undefined, months: number, now = new Date()): boolean {
  if (!value || !Number.isInteger(months) || months <= 0) return false
  const parsed = new Date(value)
  if (Number.isNaN(parsed.getTime()) || parsed.getTime() > now.getTime()) return false
  const limit = new Date(now.getTime())
  limit.setUTCMonth(limit.getUTCMonth() - months)
  return parsed < limit
}
