/**
 * What a unit's Handbook assessment table says about exams, as the API sends
 * it in `exam_status` and filters on it. Same order everywhere: unit list
 * filter, electives page and the colour on each unit card.
 *
 * none: no exam, quiz or test listed. quiz: no exam, but a quiz or test.
 * exam: an exam is listed (a card says "final" when the item's name does).
 * unknown: the Handbook lists no assessment yet.
 */
export const EXAM_STATUSES = ['none', 'quiz', 'exam', 'unknown'] as const
export type ExamStatus = typeof EXAM_STATUSES[number]
