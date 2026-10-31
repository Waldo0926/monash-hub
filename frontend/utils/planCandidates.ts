/**
 * The units a degree still wants, for the add-unit dialog to offer before the
 * reader has typed anything.
 *
 * A student who knows the code searches for it. The one this list is for does
 * not: they picked their degree, opened a semester, and the dialog said "type
 * a unit code". The degree page already names every unit each part asks for,
 * and the course map already knows which of them are on the map, so the
 * difference is the answer, read straight off the degree the plan page has
 * loaded. Nothing is fetched for it.
 *
 * Parts that list specialisations, majors or minors rather than units offer
 * the units of the one the student has started; until one is started, the
 * units of every choice, each saying which choice it belongs to, so "Part C"
 * does not read as a single list of 144 points when it means "one of these
 * four".
 */

/** The part a candidate counts towards, as the progress panel draws it. */
export interface CandidatePart {
  index: number
  title: string
  letter: string
  tone: number
  free: boolean
  /** The specialisation, major or minor the plan has started in this part, if any. */
  aos: string | null
}

export interface Candidate {
  unit_code: string
  title: string
  credit_points: number | null
  /** S1, S2 and so on at the plan's campus (every campus when it is not taught there). */
  periods: string[]
  offered_at_campus: boolean
  part: CandidatePart
  /** The specialisation, major or minor this unit came through, by title. */
  via: string | null
}

const AOS_TYPES = ['specialisation', 'major', 'minor']

function unitsIn(node: any): string[] {
  return [
    ...(node.items || []).filter((i: any) => i.type === 'unit').map((i: any) => i.code),
    ...(node.containers || []).flatMap(unitsIn)
  ]
}

function choicesIn(node: any): string[] {
  return [
    ...(node.items || []).filter((i: any) => AOS_TYPES.includes(i.type)).map((i: any) => i.code),
    ...(node.containers || []).flatMap(choicesIn)
  ]
}

/**
 * Every unit the degree names that is not on the map, in the degree's own
 * order: part by part, and within a part as the Handbook lists them. A unit
 * named by two parts is offered once, under the first.
 *
 * Units the chosen Handbook year no longer lists are left out: they cannot be
 * added without a red mark, and the degree page is where to read about them.
 * Units not taught at the plan's campus stay, marked, because the rule still
 * names them and the student should see that it does.
 */
export function degreeCandidates(
  course: any,
  parts: CandidatePart[],
  planned: Set<string>
): Candidate[] {
  if (!course?.containers || !parts.length) return []
  const facts = course.units || {}
  const aosUnits = new Map<string, string[]>(
    (course.areas_of_study || []).map((a: any) => [a.code, a.unit_codes || []])
  )
  const aosTitle = new Map<string, string>(
    (course.areas_of_study || []).map((a: any) => [a.code, a.title])
  )

  const seen = new Set<string>()
  const out: Candidate[] = []
  const offer = (code: string, part: CandidatePart, via: string | null) => {
    if (seen.has(code) || planned.has(code)) return
    const fact = facts[code]
    if (!fact || fact.in_year === false) return
    seen.add(code)
    out.push({
      unit_code: code,
      title: fact.title || '',
      credit_points: fact.credit_points == null ? null : Number(fact.credit_points),
      periods: fact.periods || [],
      offered_at_campus: fact.offered_at_campus !== false,
      part,
      via
    })
  }

  course.containers.forEach((node: any, index: number) => {
    const part = parts[index]
    // A free elective part is "anything else": it has no list to offer.
    if (!part || part.free) return
    for (const code of unitsIn(node)) offer(code, part, null)
    const choices = choicesIn(node)
    const picked = part.aos && choices.includes(part.aos) ? [part.aos] : choices
    for (const aos of picked) {
      for (const code of aosUnits.get(aos) || []) offer(code, part, aosTitle.get(aos) || aos)
    }
  })
  return out
}

/**
 * The slot on the map with room for one more, nearest the start: the first
 * semester that holds fewer than a full load, in the order the map draws them.
 * A full map falls back to its last slot, which the dialog names, so the unit
 * still lands somewhere the student can see and move.
 */
export function firstOpenSlot(
  years: number[],
  periods: string[],
  count: (year: number, period: string) => number,
  load: number
): { year: number; period: string } | null {
  if (!years.length || !periods.length) return null
  for (const year of years) {
    for (const period of periods) {
      if (count(year, period) < load) return { year, period }
    }
  }
  return { year: years[years.length - 1]!, period: periods[0]! }
}
