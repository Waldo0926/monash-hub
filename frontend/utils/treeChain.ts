/**
 * The units connected to one node of the prerequisite graph, in both
 * directions: everything it needs, however many steps back, and everything
 * that needs it. Edges run from the prerequisite to the unit that requires it,
 * which is how the API draws them.
 *
 * This is what the graph dims everything else against. Highlighting only the
 * edges touching the selected node, which is what it did before, answered
 * "what does this connect to" and not the question a student standing in
 * front of FIT3155 has, which is "which of these forty boxes are on my way to
 * it".
 */
export interface ChainEdge {
  source: string
  target: string
}

export function chainOf(code: string, edges: ChainEdge[]): Set<string> {
  const up = new Map<string, string[]>()
  const down = new Map<string, string[]>()
  for (const edge of edges) {
    if (!up.has(edge.target)) up.set(edge.target, [])
    if (!down.has(edge.source)) down.set(edge.source, [])
    up.get(edge.target)!.push(edge.source)
    down.get(edge.source)!.push(edge.target)
  }
  const chain = new Set<string>([code])
  for (const next of [up, down]) {
    const queue = [code]
    while (queue.length) {
      const at = queue.pop()!
      for (const other of next.get(at) || []) {
        if (chain.has(other)) continue
        chain.add(other)
        queue.push(other)
      }
    }
  }
  return chain
}
