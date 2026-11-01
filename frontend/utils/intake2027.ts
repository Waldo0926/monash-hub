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
/** Do not do fuzzy matching: an alias or longer variant can misidentify a degree. */
export function october2027Status(title: string): IntakeStatus {
  return listed.has(title.replace(/\s+/g, ' ').trim()) ? 'listed' : 'not_verified'
}
