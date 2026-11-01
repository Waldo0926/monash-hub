/**
 * Intake listing evidence, kept strictly separate from fee rows.
 *
 * A programme listed for October 2027 is evidence it appears in that
 * official intake's AVAILABLE COURSES section; it does NOT mean applications
 * are currently open or that other programmes have been discontinued.
 *
 * Reviewed against Monash Malaysia's October intake page on 2026-11-01.
 * Any new intake/degree must be verified against its own official listing.
 */
export const OCTOBER_2027_SOURCE = 'https://www.monash.edu.my/study/apply/intake-periods/october-intake'
export const OCTOBER_2027_CHECKED = '2026-11-01'
const listed = new Set([
  'Bachelor of Arts and Social Sciences',
  'Bachelor of Digital Media and Communication',
  'Bachelor of Business and Commerce',
  'Bachelor of Business and Commerce and Bachelor of Digital Media and Communication',
  'Bachelor of Business and Commerce and Bachelor of Computer Science',
  'Bachelor of Civil Engineering (Honours)',
  'Bachelor of Chemical Engineering (Honours)',
  'Bachelor of Electrical and Computer Systems Engineering (Honours)',
  'Bachelor of Mechanical Engineering (Honours)',
  'Bachelor of Robotics and Mechatronics Engineering (Honours)',
  'Bachelor of Materials Engineering (Honours)',
  'Bachelor of Computer Science',
  'Bachelor of Computer Science in Data Science',
  'Bachelor of Computer Science in Artificial Intelligence',
  'Bachelor of Psychology',
  'Bachelor of Psychology and Business',
  'Bachelor of Applied Data Science',
  'Bachelor of Science',
  'Bachelor of Food Science and Technology',
  'Bachelor of Medical Bioscience',
  'Diploma of Higher Education Studies'
])
export type IntakeStatus = 'listed' | 'not_verified'
export type IntakePeriod = 'february' | 'july' | 'october'

export type IntakeEvidence = {
  id: IntakePeriod
  year: 2027
  source: string
  checkedOn: string
  /** These are the public general-category deadlines, NOT proof of open applications. */
  generalDeadlineMalaysia: string
  generalDeadlineInternational: string
  /** A per-degree available-courses list is published for October, not February/July. */
  hasVerifiedDegreeList: boolean
  exceptionsApply: boolean
}

export const INTAKES_2027: readonly IntakeEvidence[] = [
  {
    id: 'february', year: 2027,
    source: 'https://www.monash.edu.my/study/apply/intake-periods/february-intake',
    checkedOn: '2026-11-01',
    generalDeadlineMalaysia: '2027-02-19',
    generalDeadlineInternational: '2026-12-18',
    hasVerifiedDegreeList: false, exceptionsApply: true
  },
  {
    id: 'july', year: 2027,
    source: 'https://www.monash.edu.my/study/apply/intake-periods',
    checkedOn: '2026-11-01',
    generalDeadlineMalaysia: '2027-07-16',
    generalDeadlineInternational: '2027-05-14',
    hasVerifiedDegreeList: false, exceptionsApply: true
  },
  {
    id: 'october', year: 2027,
    source: OCTOBER_2027_SOURCE,
    checkedOn: OCTOBER_2027_CHECKED,
    generalDeadlineMalaysia: '2027-10-15',
    generalDeadlineInternational: '2027-08-13',
    hasVerifiedDegreeList: true, exceptionsApply: false
  }
]

/** Only exact titles in the explicitly dated October 2027 list qualify. */
export function intake2027Status(title: string, period: IntakePeriod): IntakeStatus {
  if (period !== 'october') return 'not_verified'
  return listed.has(title.replace(/\s+/g, ' ').trim()) ? 'listed' : 'not_verified'
}

export function october2027Status(title: string): IntakeStatus {
  return intake2027Status(title, 'october')
}

/**
 * The official deadline table does not certify that an individual degree is
 * accepting applications at this moment. No 'open', 'paused', or 'closed'
 * state is inferred from this dataset.
 */
export const APPLICATION_STATUS_2027 = 'not_verified' as const
