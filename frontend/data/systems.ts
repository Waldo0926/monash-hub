/**
 * The Monash systems a student actually logs into, and which campus each is for.
 *
 * The URLs were given by the site's author; they are not guessed and not
 * shortened. `.monash.edu.my` hosts are Malaysia's own - SORS, Attendance,
 * AskMira and the Helpdesk have no Australian equivalent here - so they carry
 * the campus label the guide pages use, for the same reason: a reader should
 * not have to work out from a hostname whether a link is meant for them.
 */
export interface MonashSystem {
  name: string
  url: string
  /** Matches OfficialPage.applies_to - 'all' or 'malaysia'. */
  appliesTo: 'all' | 'malaysia'
}

export const MONASH_SYSTEMS: MonashSystem[] = [
  { name: 'Moodle', url: 'https://learning.monash.edu/my/', appliesTo: 'all' },
  {
    name: 'WES',
    url: 'https://my.monash.edu/wes/student_services/',
    appliesTo: 'all'
  },
  { name: 'Allocate+', url: 'https://my-timetable.monash.edu/', appliesTo: 'all' },
  { name: 'eExam', url: 'https://eassessment.monash.edu/my/', appliesTo: 'all' },
  { name: 'SORS', url: 'https://sors.monash.edu.my/', appliesTo: 'malaysia' },
  {
    name: 'Attendance',
    url: 'https://attendance.monash.edu.my/student/',
    appliesTo: 'malaysia'
  },
  { name: 'AskMira', url: 'https://askmira.monash.edu.my/', appliesTo: 'malaysia' },
  {
    name: 'MUM Helpdesk',
    url: 'https://helpdesk.monash.edu.my/',
    appliesTo: 'malaysia'
  }
]
