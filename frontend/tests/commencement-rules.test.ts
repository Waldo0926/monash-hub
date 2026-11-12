import { describe, expect, it, vi } from 'vitest'
import { loadCommencementRules } from '../utils/commencementRules'

const snapshot = {
  course_code: 'C9001', academic_year: 2025, title: 'Synthetic degree',
  source_url: 'https://handbook.monash.edu/2025/courses/C9001',
  containers: [{ title: 'Synthetic 2025 requirement', credit_points: 24 }]
}

describe('exact commencement-year records', () => {
  it('requests the exact year even when another year is supplied in options', async () => {
    const fetcher = vi.fn().mockResolvedValue(snapshot)
    const result = await loadCommencementRules(fetcher, 'c9001', 2025, { year: '2027' })
    expect(result.status).toBe('available')
    expect(result.snapshot?.containers?.[0]?.title).toBe('Synthetic 2025 requirement')
    const url = new URL(fetcher.mock.calls[0]![0], 'https://example.invalid')
    expect(url.searchParams.get('year')).toBe('2025')
  })

  it('never retries an absent edition using the nearest or current year', async () => {
    const fetcher = vi.fn().mockRejectedValue({ statusCode: 404 })
    const result = await loadCommencementRules(fetcher, 'C9001', 2024)
    expect(result.status).toBe('not_indexed')
    expect(result.snapshot).toBeNull()
    expect(fetcher).toHaveBeenCalledTimes(1)
    expect(fetcher.mock.calls[0]![0]).toContain('year=2024')
  })

  it.each([
    { ...snapshot, academic_year: 2026 },
    { ...snapshot, course_code: 'C9002' },
    { ...snapshot, source_url: 'https://handbook.monash.edu/2026/courses/C9001' },
    { ...snapshot, source_url: 'https://example.invalid/2025/courses/C9001' }
  ])('rejects a mismatched degree, year or official source', async value => {
    const result = await loadCommencementRules(async () => value, 'C9001', 2025)
    expect(result.status).toBe('identity_mismatch')
    expect(result.snapshot).toBeNull()
  })

  it('does not interpret an unavailable response as a missing degree', async () => {
    const result = await loadCommencementRules(async () => { throw { status: 503 } }, 'C9001', 2025)
    expect(result.status).toBe('failed')
    expect(result.snapshot).toBeNull()
  })
})
