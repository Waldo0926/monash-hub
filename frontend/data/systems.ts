/**
 * The Monash systems a student actually logs into, and which campus each is for.
 *
 * The URLs were given by the site's author; they are not guessed and not
 * shortened. `.monash.edu.my` links are Malaysia's own - SORS, Attendance,
 * MoVA (Monash Connect Malaysia) and the Helpdesk - so they carry
 * the campus label the guide pages use, for the same reason: a reader should
 * not have to work out from a hostname whether a link is meant for them.
 */
export interface MonashSystem {
  name: string
  url: string
  /** Matches OfficialPage.applies_to - 'all' or 'malaysia'. */
  appliesTo: 'all' | 'malaysia'
  hint?: { zh: string; en: string }
}

export const MONASH_SYSTEMS: MonashSystem[] = [
  { name: 'Moodle', url: 'https://learning.monash.edu/my/', appliesTo: 'all', hint: { zh: '课件与作业', en: 'Units & assignments' } },
  {
    name: 'WES',
    url: 'https://my.monash.edu/wes/student_services/',
    appliesTo: 'all',
    hint: { zh: '选课与成绩', en: 'Enrolment & results' }
  },
  { name: 'Allocate+', url: 'https://my-timetable.monash.edu/', appliesTo: 'all', hint: { zh: '排课表选班', en: 'Class timetable' } },
  { name: 'eExam', url: 'https://eassessment.monash.edu/my/', appliesTo: 'all', hint: { zh: '在线考试', en: 'Online exams' } },
  { name: 'SORS', url: 'https://sors.monash.edu.my/', appliesTo: 'malaysia', hint: { zh: '请假与证明', en: 'Requests & letters' } },
  {
    name: 'Attendance',
    url: 'https://attendance.monash.edu.my/student/',
    appliesTo: 'malaysia',
    hint: { zh: '课堂考勤', en: 'Class attendance' }
  },
  {
    name: 'MoVA',
    url: 'https://www.monash.edu.my/student-services/connect?chatbot=open',
    appliesTo: 'malaysia',
    hint: { zh: '马莫在线咨询', en: 'Student support' }
  },
  {
    name: 'MUM Helpdesk',
    url: 'https://helpdesk.monash.edu.my/',
    appliesTo: 'malaysia',
    hint: { zh: 'IT 与校园支持', en: 'IT & campus help' }
  }
]
