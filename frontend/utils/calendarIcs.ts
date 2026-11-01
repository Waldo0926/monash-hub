/**
 * Build an offline .ics file from the same sourced Monash dates the page shows.
 * Date ranges use *exclusive* DTEND, as required by RFC 5545.
 *
 * Some official events have times but no verified timezone-independent instant
 * in the stored data. Export as all-day markers with the printed time and
 * official source in DESCRIPTION rather than inventing a deadline timestamp.
 */
import type { KeyDate, KeyDates } from './keyDates'
import { keyDateLabel, type KeyDateLang } from './keyDates'

function icsEscape(value: string): string {
  return value.replace(/\\/g, '\\\\').replace(/\r?\n/g, '\\n')
    .replace(/,/g, '\\,').replace(/;/g, '\\;')
}
function asDate(iso: string): string | null {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(iso)) return null
  const d = new Date(iso + 'T00:00:00Z')
  if (Number.isNaN(d.getTime()) || d.toISOString().slice(0, 10) !== iso) return null
  return iso.replace(/-/g, '')
}
function nextDate(iso: string): string {
  const d = new Date(iso + 'T00:00:00Z')
  d.setUTCDate(d.getUTCDate() + 1)
  return d.toISOString().slice(0, 10).replace(/-/g, '')
}
function key(item: KeyDate, campus: string): string {
  return [campus, item.kind, item.period ?? '', item.date, item.end ?? '', item.name ?? ''].join('|')
}
function id(value: string): string {
  // Stable FNV-1a; includes the campus to avoid cross-campus collisions.
  let hash = 2166136261
  for (const c of value) {
    hash ^= c.charCodeAt(0)
    hash = Math.imul(hash, 16777619)
  }
  return (hash >>> 0).toString(16).padStart(8, '0')
}
function fold(line: string): string {
  // 75-octet folding is required for interoperability with calendar clients.
  const chunks: string[] = []
  let part = ''
  let len = 0
  for (const char of line) {
    const bytes = new TextEncoder().encode(char).length
    if (len + bytes > 75) { chunks.push(part); part = ' '; len = 1 }
    part += char
    len += bytes
  }
  if (part) chunks.push(part)
  return chunks.join('\r\n')
}

export function buildKeyDatesIcs(data: KeyDates, language: KeyDateLang, includeHolidays = true, stamp = new Date()): string {
  const lines = [
    'BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Monash Hub//Unofficial Key Dates//EN',
    'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
    'X-WR-CALNAME:' + icsEscape(data.campus === 'malaysia' ? 'Monash Malaysia - Key dates' : 'Monash Australia - Key dates')
  ]
  const seen = new Set<string>()
  const now = stamp.toISOString().replace(/[-:]/g, '').replace(/\.\d{3}/, '')
  for (const item of data.items) {
    if (!includeHolidays && item.kind === 'holiday') continue
    const start = asDate(item.date)
    const end = asDate(item.end || item.date)
    if (!start || !end || end < start) continue
    const identity = key(item, data.campus)
    if (seen.has(identity)) continue
    seen.add(identity)
    const label = keyDateLabel(item, language)
    const src = data.sources[item.source]
    const sourceUrl = src?.url || ''
    const description = [
      label.sub || '',
      item.time ? (language === 'zh' ? '官网显示时间：' : 'Time shown by source: ') + item.time : '',
      sourceUrl ? 'Official source: ' + sourceUrl : '',
      language === 'zh'
        ? '非官方日历副本。请以Monash官网为准，部分教学期不在此列表中'
        : 'Unofficial calendar copy. Verify with Monash; not all teaching periods are included.'
    ].filter(Boolean).join('\n')
    lines.push(
      'BEGIN:VEVENT',
      'UID:' + id(identity) + '@monashhub.secureview.tech',
      'DTSTAMP:' + now,
      'DTSTART;VALUE=DATE:' + start,
      'DTEND;VALUE=DATE:' + nextDate(item.end || item.date),
      'SUMMARY:' + icsEscape(label.main),
      'DESCRIPTION:' + icsEscape(description),
      ...(sourceUrl ? ['URL:' + sourceUrl] : []),
      'END:VEVENT'
    )
  }
  lines.push('END:VCALENDAR')
  return lines.map(fold).join('\r\n') + '\r\n'
}
