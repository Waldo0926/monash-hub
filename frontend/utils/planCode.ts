/**
 * A plan as one line of text, for moving it to another device by hand.
 *
 * The plan lives in one browser. Export writes a file, which is fine on a
 * laptop and a chore on a phone: the file lands in Downloads and has to be
 * sent on and opened. A line of text goes through any chat app, including a
 * student's own "file transfer" chat, and is pasted back on the other side.
 * No server sees it: the code is made here and read here.
 *
 * The code is readable rather than compressed, so a student can see what it
 * says and a chat app's link detection does not mangle it:
 *
 *   MH1|<name>|<start year>|<years>|<campus>|<degree>|<periods>|<entries>
 *
 * Periods are short codes (S1, S2, SA...) separated by ";". Entries are
 * CODE@y.p, separated by ",": y is the year counted from the start year, p
 * the index into the periods list. Text fields are URI-encoded, so the code
 * has no spaces and the "|" only ever separates fields.
 */
import type { PlanState } from '../composables/usePlan'

export const PLAN_CODE_PREFIX = 'MH1'

const PERIOD_CODES: Record<string, string> = {
  'First semester': 'S1',
  'Second semester': 'S2',
  'Summer semester A': 'SA',
  'Summer semester B': 'SB',
  'Winter semester': 'W',
  'Full year': 'FY',
  'October intake teaching period, Malaysia campus': 'OCT'
}
const PERIOD_NAMES = Object.fromEntries(Object.entries(PERIOD_CODES).map(([name, code]) => [code, name]))

const enc = (text: string) => encodeURIComponent(text)
const dec = (text: string) => {
  try {
    return decodeURIComponent(text)
  } catch {
    return text
  }
}

export function encodePlan(plan: PlanState): string {
  const periods = plan.periods.map((p) => PERIOD_CODES[p] || enc(p))
  const entries = plan.entries
    .map((e) => {
      const p = plan.periods.indexOf(e.teaching_period)
      return p < 0 ? null : `${e.unit_code}@${e.year - plan.startYear}.${p}`
    })
    .filter((e): e is string => e !== null)
  return [
    PLAN_CODE_PREFIX,
    enc(plan.name),
    String(plan.startYear),
    String(plan.years),
    enc(plan.campus),
    enc(plan.courseCode),
    periods.join(';'),
    entries.join(',')
  ].join('|')
}

/** The code inside whatever was pasted: a bare code, a link ending in one, or a message around one. */
export function findPlanCode(text: string): string | null {
  const shape = /MH1\|[^\s|]*(?:\|[^\s|]*){6}/
  // As pasted first: a bare code's own %-escapes must stay as they are. A
  // link carries the code encoded once more, so it is read after one decode.
  const match = text.match(shape) || dec(text).match(shape)
  return match ? match[0] : null
}

/**
 * The plan a code describes, as the loose object `sanitise` in usePlan takes,
 * or null when the text holds no code. Field checks stay in one place there.
 */
export function decodePlan(text: string): Record<string, unknown> | null {
  const code = findPlanCode(text)
  if (!code) return null
  const [, name, startYear, years, campus, courseCode, periodText, entryText] = code.split('|')
  const periods = periodText ? periodText.split(';').map((p) => PERIOD_NAMES[p] || dec(p)) : []
  const start = Number(startYear)
  const entries = (entryText ? entryText.split(',') : []).flatMap((item) => {
    const m = item.match(/^([A-Za-z0-9]+)@(-?\d+)\.(\d+)$/)
    if (!m) return []
    const period = periods[Number(m[3])]
    return period ? [{ unit_code: m[1]!, year: start + Number(m[2]), teaching_period: period }] : []
  })
  return {
    name: dec(name || ''),
    startYear: start,
    years: Number(years),
    campus: dec(campus || ''),
    courseCode: dec(courseCode || ''),
    periods,
    entries
  }
}
