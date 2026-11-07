import { describe, expect, it } from 'vitest'
import { applyGpa, applyWam, parsePastedResults, type MarksReference } from '../utils/marks'

// Synthetic reference subset: just the two grades used by these attempts.
const reference: MarksReference = {
  grade_points: { malaysia: { N: 1.15, HD: 4 } },
  grade_names: { N: 'Fail', HD: 'High distinction' },
  grade_bands: [{ floor: 80, grade: 'HD' }, { floor: 0, grade: 'N' }],
  excluded_grades: [], level_weights: { first_year: 0.5, other: 1 }, sources: {}, guides: {}
}

describe('transcript attempts', () => {
  it('preserves a failed attempt and the retake in either order', () => {
    for (const text of ['FIT1008 6 40 N\nFIT1008 6 80 HD', 'FIT1008 6 80 HD\nFIT1008 6 40 N']) {
      const rows = parsePastedResults(text)
      expect(rows).toHaveLength(2)
      const attempts = rows.map((row, id) => ({ ...row, id, level: 1 }))
      expect(applyWam(attempts, reference)).toBe(60)
      expect(applyGpa(attempts, reference, 'malaysia')).toBeCloseTo(2.575)
    }
  })

  it('keeps identical rows because a code and mark do not identify an attempt', () => {
    expect(parsePastedResults('FIT1008 6 80 HD\nFIT1008 6 80 HD')).toHaveLength(2)
  })

  it('keeps markless attempts alongside a later mark for the same unit', () => {
    expect(parsePastedResults('FIT1008 6 WN\nFIT1008 6 80 HD')).toEqual([
      { unitCode: 'FIT1008', creditPoints: 6, mark: null, grade: 'WN' },
      { unitCode: 'FIT1008', creditPoints: 6, mark: 80, grade: 'HD' }
    ])
  })
})
