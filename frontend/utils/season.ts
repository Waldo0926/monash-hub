/**
 * Which part of the semester it is, read off the key dates the home page
 * already has, and which guides belong to it.
 *
 * Exam weeks win over everything else: in late October WES re-enrolment is open
 * too, but a student four days from a final opens the site for the exam
 * timetable and special consideration, not for next year's units.
 */
import { dayNumber, type KeyDate } from '~/utils/keyDates'

export type Season = 'exams' | 'enrol' | 'start' | 'term'

const ENROL_KINDS = new Set([
  'reenrol', 'reenrol_late', 'wes_open',
  'allocate_pref_open', 'allocate_pref_close', 'allocate_adjust_open', 'allocate_adjust_close'
])

export function pickSeason(items: KeyDate[], today: string): Season {
  const now = dayNumber(today)
  const academic = items.filter(i => i.kind !== 'holiday')
  const daysTo = (item: KeyDate) => dayNumber(item.date) - now
  const underway = (item: KeyDate) => daysTo(item) <= 0 && dayNumber(item.end ?? item.date) >= now

  const examSoon = academic.some(i => (i.kind === 'swot_vac' || i.kind === 'exams') && (underway(i) || daysTo(i) <= 21))
  // Exams over, results not out yet: still the same few pages people need.
  const awaitingResults = academic[0]?.kind === 'results' && daysTo(academic[0]) <= 30
  if (examSoon || awaitingResults) return 'exams'

  if (academic.some(i => ENROL_KINDS.has(i.kind) && (underway(i) || daysTo(i) <= 14))) return 'enrol'
  if (academic.some(i => i.kind === 'census' && daysTo(i) >= 0 && daysTo(i) <= 35)) return 'start'
  return 'term'
}

// Guides that do not exist at a campus simply do not come back from the API, so
// a list can name a few more than it shows.
export const SEASON_GUIDES: Record<'malaysia' | 'australia', Record<Season, string[]>> = {
  malaysia: {
    exams: [
      'final-assessment-dates', 'dates-timetables-start-times', 'special-consideration',
      'supporting-documents', 'defer-final-assessment', 'results-release',
      'malaysia-frequent-asked-questions-faq-exam-results'
    ],
    enrol: [
      're-enrol', 'it-undergraduate-re-enrolment-malaysia', 'allocate-timetable',
      'add-or-withdraw-units', 'course-advice', 'study-load'
    ],
    start: [
      'census-dates-explained', 'add-or-withdraw-units', 'allocate-timetable',
      'malaysia-student-pass', 'enrolments', 'study-load'
    ],
    term: [
      'special-consideration', 'supporting-documents', 'add-or-withdraw-units',
      'census-dates', 'intermission', 'failed-units'
    ]
  },
  australia: {
    exams: [
      'final-assessment-dates', 'dates-timetables-start-times', 'special-consideration',
      'supporting-documents', 'defer-final-assessment', 'results-release'
    ],
    enrol: [
      're-enrol', 'it-undergraduate-re-enrolment', 'allocate-timetable',
      'add-or-withdraw-units', 'course-advice', 'study-load'
    ],
    start: [
      'census-dates-explained', 'add-or-withdraw-units', 'allocate-timetable',
      'confirmation-of-enrolment', 'enrolments', 'study-load'
    ],
    term: [
      'special-consideration', 'supporting-documents', 'add-or-withdraw-units',
      'census-dates', 'intermission', 'failed-units'
    ]
  }
}

/** At most this many links in the block, in the order listed above. */
export const SEASON_LIMIT = 6
