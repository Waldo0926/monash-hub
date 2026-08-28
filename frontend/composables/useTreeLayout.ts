/**
 * Layered layout for the prerequisite graph.
 *
 * There is no graph library in this project and this file is the reason it can
 * stay that way. The problem is the easy half of Sugiyama: the API already
 * returns a layer for every node — its signed depth from the seed — so there is
 * nothing to rank and no cycle to break. What is left is ordering nodes within
 * a layer so the edges between layers cross as little as possible, which is the
 * median heuristic, and then assigning coordinates.
 *
 * The heuristic is worth spelling out because "sort by code" looks like it
 * would do: with FIT1045 and ENG1013 both feeding FIT1058, alphabetical order
 * puts ENG above FIT in one column and below it in the next, and every such
 * inversion is a line crossing the reader has to untangle. Sorting each layer
 * by the median position of its neighbours in the layer before it removes most
 * of them in a handful of sweeps.
 */
export const CARD_W = 176
export const CARD_H = 56
export const COL_GAP = 96
export const ROW_GAP = 18
export const COL_W = CARD_W + COL_GAP
export const ROW_H = CARD_H + ROW_GAP

export interface TreeNode {
  unit_code: string
  title: string | null
  depth: number
  in_year: boolean
  offered_at_campus: boolean
  periods: string[]
  prefix: string
  credit_points?: number | null
}

export interface TreeEdge {
  source: string
  target: string
  type: string
  connector: string | null
  group: number
}

export interface PlacedNode extends TreeNode {
  x: number
  y: number
}

export interface PlacedEdge extends TreeEdge {
  path: string
}

export interface Layout {
  nodes: PlacedNode[]
  edges: PlacedEdge[]
  width: number
  height: number
}

const SWEEPS = 4

function median(values: number[]): number {
  if (!values.length) return -1
  const sorted = [...values].sort((a, b) => a - b)
  const mid = sorted.length >> 1
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2
}

/**
 * Order each layer so that edges between neighbouring layers cross less.
 *
 * A node with no neighbour in the layer being read from keeps its current
 * position rather than collapsing to the top — sorting those to -1 would pile
 * every unattached node into one corner and undo the work.
 */
function reduceCrossings(layers: Map<number, string[]>, edges: TreeEdge[]): void {
  const depths = [...layers.keys()].sort((a, b) => a - b)
  const incoming = new Map<string, string[]>()
  const outgoing = new Map<string, string[]>()
  for (const edge of edges) {
    if (!incoming.has(edge.target)) incoming.set(edge.target, [])
    if (!outgoing.has(edge.source)) outgoing.set(edge.source, [])
    incoming.get(edge.target)!.push(edge.source)
    outgoing.get(edge.source)!.push(edge.target)
  }

  const indexIn = (depth: number) => {
    const order = layers.get(depth) || []
    return new Map(order.map((code, index) => [code, index]))
  }

  for (let sweep = 0; sweep < SWEEPS; sweep += 1) {
    const forward = sweep % 2 === 0
    const walk = forward ? depths.slice(1) : depths.slice(0, -1).reverse()
    for (const depth of walk) {
      const reference = indexIn(depth + (forward ? -1 : 1))
      const neighbours = forward ? incoming : outgoing
      const order = layers.get(depth)!
      const current = new Map(order.map((code, index) => [code, index]))
      layers.set(
        depth,
        [...order].sort((a, b) => {
          const ma = median((neighbours.get(a) || []).map((n) => reference.get(n)!).filter((v) => v !== undefined))
          const mb = median((neighbours.get(b) || []).map((n) => reference.get(n)!).filter((v) => v !== undefined))
          const ka = ma < 0 ? current.get(a)! : ma
          const kb = mb < 0 ? current.get(b)! : mb
          return ka - kb || current.get(a)! - current.get(b)!
        })
      )
    }
  }
}

/** A left-to-right cubic, flat enough that a same-row edge reads as a straight line. */
function curve(x1: number, y1: number, x2: number, y2: number): string {
  const span = Math.max(40, (x2 - x1) * 0.5)
  return `M ${x1} ${y1} C ${x1 + span} ${y1}, ${x2 - span} ${y2}, ${x2} ${y2}`
}

export function layoutTree(nodes: TreeNode[], edges: TreeEdge[]): Layout {
  if (!nodes.length) return { nodes: [], edges: [], width: 0, height: 0 }

  const known = new Set(nodes.map((n) => n.unit_code))
  const live = edges.filter((e) => known.has(e.source) && known.has(e.target))

  const layers = new Map<number, string[]>()
  for (const node of [...nodes].sort((a, b) => a.unit_code.localeCompare(b.unit_code))) {
    if (!layers.has(node.depth)) layers.set(node.depth, [])
    layers.get(node.depth)!.push(node.unit_code)
  }
  reduceCrossings(layers, live)

  const depths = [...layers.keys()].sort((a, b) => a - b)
  const tallest = Math.max(...depths.map((d) => layers.get(d)!.length))
  const height = tallest * ROW_H
  const placed = new Map<string, PlacedNode>()
  const byCode = new Map(nodes.map((n) => [n.unit_code, n]))

  depths.forEach((depth, column) => {
    const order = layers.get(depth)!
    // Each column is centred against the tallest one, so a short column of
    // prerequisites sits beside the middle of the graph rather than its top.
    const top = (height - order.length * ROW_H) / 2
    order.forEach((code, row) => {
      placed.set(code, {
        ...byCode.get(code)!,
        x: column * COL_W,
        y: top + row * ROW_H
      })
    })
  })

  return {
    nodes: [...placed.values()],
    edges: live.map((edge) => {
      const from = placed.get(edge.source)!
      const to = placed.get(edge.target)!
      return {
        ...edge,
        path: curve(from.x + CARD_W, from.y + CARD_H / 2, to.x, to.y + CARD_H / 2)
      }
    }),
    width: depths.length * COL_W - COL_GAP,
    height
  }
}
