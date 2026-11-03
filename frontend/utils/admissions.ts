export type AdmissionsEvidence = {
  course_code: string | null
  campus: 'Malaysia'
  status: 'open' | 'closed' | 'suspended' | 'conflict' | 'not_verified'
  reason: string
  source_url: string | null
  last_checked: string | null
  valid_until: string | null
  intake_status: 'not_verified'
}
