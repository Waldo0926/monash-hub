import type { FeeRow } from './tuition'

/**
 * This is a student-controlled *scenario*, not a fee quote or eligibility test.
 * Never calculate from unreadable/missing numbers or silently turn full-course
 * totals into annual fees.
 */
export type FeeScenario = {
  row: FeeRow
  feeSide: 'domestic' | 'international'
  amountIndex: number
  yearsRemaining: number
  scholarshipPercent: number
  livingPerYear: number
}
export type FeeEstimate = {
  basis: 'per_year' | 'full_course'
  published: number
  grossTuition: number
  discount: number
  netTuition: number
  living: number
  total: number
}
export function estimateFeeScenario(input: FeeScenario): FeeEstimate | null {
  const { row } = input
  if (row.unreadable || (row.basis !== 'per_year' && row.basis !== 'full_course')) return null
  const amount = row[input.feeSide]?.[input.amountIndex]?.value
  if (amount == null || !Number.isFinite(amount) || amount < 0) return null
  const { yearsRemaining, scholarshipPercent, livingPerYear } = input
  if (![yearsRemaining, scholarshipPercent, livingPerYear].every(Number.isFinite)) return null
  if (yearsRemaining <= 0 || yearsRemaining > 12 || scholarshipPercent < 0 || scholarshipPercent > 100 || livingPerYear < 0) return null
  const grossTuition = amount * (row.basis === 'per_year' ? yearsRemaining : 1)
  const discount = grossTuition * (scholarshipPercent / 100)
  const netTuition = grossTuition - discount
  const living = yearsRemaining * livingPerYear
  return { basis: row.basis, published: amount, grossTuition, discount, netTuition, living, total: netTuition + living }
}
