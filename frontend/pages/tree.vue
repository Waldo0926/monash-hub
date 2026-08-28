<script setup lang="ts">
/**
 * The prerequisite graph.
 *
 * A unit page states its requisites truthfully and still does not answer the
 * question a student is holding: how many semesters of other units stand
 * between me and this one, and can I take them at my campus. This page walks
 * the rules transitively and draws the answer.
 *
 * The campus filter is the reason this is not just a nicer requisites list.
 * Every other prereq explorer for Monash is written from Clayton, where the
 * alternatives are all taught; at Malaysia several of them are not, and a
 * graph that does not say so draws a path the reader cannot walk. Units not
 * taught at the chosen campus stay on the graph and are marked, because
 * hiding them would make an unreachable rule look satisfiable.
 */
import { layoutTree, CARD_W, CARD_H, type TreeEdge, type TreeNode } from '~/composables/useTreeLayout'

const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()

const code = ref(String(route.query.unit || 'FIT2004').toUpperCase())
const direction = ref(String(route.query.direction || 'upstream'))
const campus = ref(String(route.query.campus ?? 'Malaysia'))
const depth = ref(Number(route.query.depth || 3))
const draft = ref(code.value)

const query = computed(() => {
  const params = new URLSearchParams({ direction: direction.value, depth: String(depth.value) })
  if (campus.value) params.set('campus', campus.value)
  return params.toString()
})

// The cache key is fixed when the composable is set up, so a URL that reads
// reactive state is not enough on its own - without this every control on the
// rail changes the address bar and nothing else. See useApiFetch.
const { data, pending, error } = await useLocalisedApiFetch<any>(
  () => `/v1/units/${code.value}/tree?${query.value}`,
  { watch: [code, direction, campus, depth] }
)

watch([code, direction, campus, depth], () => {
  router.replace({
    query: {
      unit: code.value,
      direction: direction.value,
      depth: String(depth.value),
      ...(campus.value ? { campus: campus.value } : {})
    }
  })
})

function show() {
  const next = draft.value.trim().toUpperCase()
  if (next) code.value = next
}

const layout = computed(() =>
  layoutTree((data.value?.nodes || []) as TreeNode[], (data.value?.edges || []) as TreeEdge[])
)

/**
 * The campus name as the reader would say it. The API filters on the Handbook's
 * own value ("Malaysia"), which is the right thing to send and the wrong thing
 * to drop into a Chinese sentence.
 */
const campusLabel = computed(() =>
  campus.value === 'Malaysia' ? $t('tree.campusMalaysia') : campus.value
)

/** Malaysia cannot teach every alternative, and the count is the headline. */
const elsewhere = computed(() =>
  campus.value ? layout.value.nodes.filter((n) => n.in_year && !n.offered_at_campus).length : 0
)

const PAD = 48

/**
 * The graph is drawn at its own size and navigated, not squeezed to fit.
 *
 * It used to fit: one viewBox around the whole graph, width and height 100%.
 * That is fine for eleven nodes and useless for two hundred - ENG1005
 * downstream fits by scaling everything to about a twentieth, and the zoom
 * button multiplied a baseline that was already unreadable, so the graph could
 * not be read at any setting.
 *
 * Now the SVG has its natural pixel size, the frame clips it, and pan and zoom
 * move the reader around it. The opening view is scaled to fit so the shape is
 * visible at a glance, but zooming in goes to full size and past it.
 */
const natural = computed(() => ({
  w: Math.max(layout.value.width + PAD * 2, 400),
  h: Math.max(layout.value.height + PAD * 2, 300)
}))

const MIN_ZOOM = 0.08
const MAX_ZOOM = 2.5

const selected = ref<string | null>(null)
const zoom = ref(1)
const pan = reactive({ x: 0, y: 0 })
const dragging = ref(false)
const frame = ref<HTMLElement | null>(null)

/**
 * The scale at which the whole graph is visible, never enlarging past 1.
 *
 * A frame with no size yet is the case that has to be handled, not divided by:
 * measured during hydration the box is 0 wide, and a fit computed from that is
 * 0.002 - a graph scaled into invisibility with no way back. The observer
 * below re-fits as soon as the frame has a real size.
 */
function fitScale(): number {
  const box = frame.value?.getBoundingClientRect()
  if (!box?.width || !box?.height || !natural.value.w || !natural.value.h) return zoom.value
  return Math.min(1, box.width / natural.value.w, box.height / natural.value.h)
}

function fit() {
  const box = frame.value?.getBoundingClientRect()
  if (!box?.width || !box?.height) return
  const scale = fitScale()
  zoom.value = scale
  pan.x = (box.width - natural.value.w * scale) / 2
  pan.y = (box.height - natural.value.h * scale) / 2
}

/** Zoom about the middle of the frame, so the view does not jump. */
function zoomBy(factor: number) {
  const box = frame.value?.getBoundingClientRect()
  const next = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, zoom.value * factor))
  if (box) {
    const cx = box.width / 2
    const cy = box.height / 2
    pan.x = cx - ((cx - pan.x) / zoom.value) * next
    pan.y = cy - ((cy - pan.y) / zoom.value) * next
  }
  zoom.value = next
}

function onWheel(event: WheelEvent) {
  event.preventDefault()
  zoomBy(event.deltaY < 0 ? 1.12 : 1 / 1.12)
}
let origin = { x: 0, y: 0, panX: 0, panY: 0 }
let pressed: string | null = null

/**
 * The canvas captures the pointer so that a drag survives leaving the frame,
 * and a captured pointer never delivers a click to the card underneath. So the
 * canvas decides for itself: a press that ends within a few pixels of where it
 * started was a click on whatever was under it, not a pan.
 */
const CLICK_SLOP = 4

function startDrag(event: PointerEvent) {
  dragging.value = true
  origin = { x: event.clientX, y: event.clientY, panX: pan.x, panY: pan.y }
  pressed = (event.target as Element).closest('.node')?.getAttribute('data-code') || null
  ;(event.currentTarget as Element).setPointerCapture(event.pointerId)
}
function onDrag(event: PointerEvent) {
  if (!dragging.value) return
  pan.x = origin.panX + (event.clientX - origin.x)
  pan.y = origin.panY + (event.clientY - origin.y)
}
function endDrag(event: PointerEvent) {
  dragging.value = false
  ;(event.currentTarget as Element).releasePointerCapture(event.pointerId)
  const moved = Math.hypot(event.clientX - origin.x, event.clientY - origin.y)
  if (moved <= CLICK_SLOP) selected.value = pressed
  pressed = null
}
// A new graph is a new shape, so it opens fitted rather than at whatever pan
// and zoom the last one was left at.
watch(layout, () => nextTick(fit))

let watcher: ResizeObserver | undefined
onMounted(() => {
  nextTick(fit)
  if (typeof ResizeObserver === 'undefined' || !frame.value) return
  // Fires once when the frame first has a size, and again whenever the window
  // changes - the second is what keeps a fitted graph fitted.
  watcher = new ResizeObserver(() => fit())
  watcher.observe(frame.value)
})
onBeforeUnmount(() => watcher?.disconnect())

const detail = computed(() => layout.value.nodes.find((n) => n.unit_code === selected.value) || null)

/** A cut title needs to look cut - without the ellipsis it reads as a typo. */
const TITLE_CHARS = 22
function clip(title: string): string {
  return title.length > TITLE_CHARS ? `${title.slice(0, TITLE_CHARS - 1)}…` : title
}

/** Faculty prefixes get a stable colour so a column reads as one discipline. */
function hue(prefix: string): number {
  let sum = 0
  for (const ch of prefix) sum = (sum * 31 + ch.charCodeAt(0)) % 360
  return sum
}
</script>

<template>
  <div class="page">
    <header class="intro">
      <h1>{{ $t('tree.title') }}</h1>
      <p class="lede">{{ $t('tree.lede') }}</p>
    </header>

    <div class="split">
      <aside class="rail">
        <section class="card">
          <label class="label" for="tree-unit">{{ $t('tree.unit') }}</label>
          <form class="finder" @submit.prevent="show">
            <input
              id="tree-unit"
              v-model="draft"
              class="input"
              :placeholder="$t('tree.unitPlaceholder')"
              autocomplete="off"
            />
            <button class="btn btn--primary btn--small" type="submit">{{ $t('tree.show') }}</button>
          </form>

          <span class="label">{{ $t('tree.direction') }}</span>
          <div class="segmented">
            <button
              v-for="option in ['upstream', 'downstream', 'both']"
              :key="option"
              class="seg"
              :class="{ 'seg--on': direction === option }"
              type="button"
              @click="direction = option"
            >
              {{ $t(`tree.dir.${option}`) }}
            </button>
          </div>

          <label class="label" for="tree-depth">{{ $t('tree.depth') }}</label>
          <input id="tree-depth" v-model.number="depth" class="range" type="range" min="1" max="4" />
          <p class="hint">{{ $t('tree.depthValue', { n: depth }) }}</p>

          <label class="label" for="tree-campus">{{ $t('tree.campus') }}</label>
          <select id="tree-campus" v-model="campus" class="input">
            <option value="Malaysia">{{ $t('tree.campusMalaysia') }}</option>
            <option value="Clayton">Clayton</option>
            <option value="">{{ $t('tree.campusAny') }}</option>
          </select>
        </section>

        <section v-if="campus && elsewhere" class="card notice">
          <strong>{{ $t('tree.notHereTitle', { n: elsewhere }) }}</strong>
          <p>{{ $t('tree.notHereBody', { campus: campusLabel }) }}</p>
        </section>

        <section class="card legend">
          <span class="label">{{ $t('tree.legend') }}</span>
          <p class="key"><span class="swatch swatch--seed" />{{ $t('tree.keySeed') }}</p>
          <p class="key"><svg class="line" viewBox="0 0 40 8"><path d="M0 4 H40" /></svg>{{ $t('tree.keyPrereq') }}</p>
          <p class="key">
            <svg class="line line--dash" viewBox="0 0 40 8"><path d="M0 4 H40" /></svg>{{ $t('tree.keyCoreq') }}
          </p>
          <p class="key"><span class="swatch swatch--away" />{{ $t('tree.keyAway', { campus: campusLabel || '—' }) }}</p>
          <p class="key"><span class="swatch swatch--gone" />{{ $t('tree.keyGone') }}</p>
        </section>
      </aside>

      <section class="canvas-wrap">
        <ErrorState v-if="error" :error="error" />
        <Skeleton v-else-if="pending" :lines="6" />
        <template v-else>
          <div class="canvas-tools">
            <button class="tool" type="button" :aria-label="$t('tree.zoomIn')" @click="zoomBy(1.25)">+</button>
            <button class="tool" type="button" :aria-label="$t('tree.zoomOut')" @click="zoomBy(1 / 1.25)">−</button>
            <button class="tool" type="button" :aria-label="$t('tree.fit')" @click="fit">⤢</button>
            <span class="tool tool--read">{{ Math.round(zoom * 100) }}%</span>
          </div>
          <p v-if="data?.truncated" class="truncated">{{ $t('tree.truncated') }}</p>

          <div
            ref="frame"
            class="canvas"
            :class="{ 'canvas--dragging': dragging }"
            @pointerdown="startDrag"
            @pointermove="onDrag"
            @pointerup="endDrag"
            @pointercancel="endDrag"
            @wheel="onWheel"
          >
            <svg
              :width="natural.w"
              :height="natural.h"
              :viewBox="`${-PAD} ${-PAD} ${natural.w} ${natural.h}`"
              class="graph"
              :style="{ transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})` }"
              role="img"
              :aria-label="$t('tree.figureLabel', { code })"
            >
              <defs>
                <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6"
                        markerHeight="6" orient="auto-start-reverse">
                  <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--border-strong)" />
                </marker>
              </defs>

              <path
                v-for="(edge, index) in layout.edges"
                :key="index"
                :d="edge.path"
                class="edge"
                :class="{ 'edge--coreq': edge.type === 'corequisite', 'edge--lit': selected === edge.source || selected === edge.target }"
                marker-end="url(#arrow)"
              />

              <g
                v-for="node in layout.nodes"
                :key="node.unit_code"
                class="node"
                :class="{
                  'node--seed': node.depth === 0,
                  'node--away': campus && node.in_year && !node.offered_at_campus,
                  'node--gone': !node.in_year,
                  'node--on': selected === node.unit_code
                }"
                :transform="`translate(${node.x}, ${node.y})`"
                :data-code="node.unit_code"
                tabindex="0"
                role="button"
                @keydown.enter="selected = node.unit_code"
              >
                <rect class="card-bg" :width="CARD_W" :height="CARD_H" rx="10" />
                <rect
                  class="stripe"
                  width="6"
                  :height="CARD_H"
                  rx="3"
                  :style="{ fill: `hsl(${hue(node.prefix)} 62% 48%)` }"
                />
                <text class="code" x="16" y="22">{{ node.unit_code }}</text>
                <text class="period" :x="CARD_W - 12" y="22">{{ node.periods.join('·') }}</text>
                <text class="name" x="16" y="40">
                  {{ clip(node.title || $t('tree.notPublished')) }}
                </text>
                <text
                  v-if="campus && node.in_year && !node.offered_at_campus"
                  class="away-mark"
                  :x="CARD_W - 12"
                  :y="CARD_H - 10"
                >✕</text>
              </g>
            </svg>
          </div>
        </template>
      </section>

      <aside v-if="detail" class="panel card">
        <button class="close" type="button" :aria-label="$t('tree.close')" @click="selected = null">×</button>
        <h2>{{ detail.unit_code }}</h2>
        <p class="panel-title">{{ detail.title || $t('tree.notPublished') }}</p>
        <p v-if="!detail.in_year" class="warn">{{ $t('tree.goneBody') }}</p>
        <p v-else-if="campus && !detail.offered_at_campus" class="warn">
          {{ $t('tree.awayBody', { campus: campusLabel }) }}
        </p>
        <p v-if="detail.periods.length" class="meta">
          {{ $t('tree.periods') }}: {{ detail.periods.join(' · ') }}
        </p>
        <NuxtLink v-if="detail.in_year" class="btn btn--ghost btn--small" :to="`/units/${detail.unit_code}`">
          {{ $t('tree.openUnit') }}
        </NuxtLink>
        <button
          v-if="detail.in_year && detail.unit_code !== code"
          class="btn btn--ghost btn--small"
          type="button"
          @click="draft = detail.unit_code; show()"
        >
          {{ $t('tree.centre') }}
        </button>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.page { max-width: var(--container); margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.intro h1 { margin: 0 0 var(--s2); }
.lede { color: var(--muted); margin: 0 0 var(--s5); max-width: 60ch; }

.split { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: var(--s4); align-items: start; }
.split:has(.panel) { grid-template-columns: 260px minmax(0, 1fr) 260px; }

.card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius); padding: var(--s4); box-shadow: var(--shadow-sm);
}
.rail { display: grid; gap: var(--s3); }
.label { display: block; font-size: 0.8rem; font-weight: 600; color: var(--muted); margin: var(--s3) 0 var(--s2); }
.label:first-child { margin-top: 0; }
.finder { display: flex; gap: var(--s2); }
.input {
  width: 100%; padding: var(--s2) var(--s3); border: 1px solid var(--border-strong);
  border-radius: var(--radius-sm); font: inherit; background: var(--surface); color: var(--text);
}
.range { width: 100%; }
.hint { margin: var(--s1) 0 0; font-size: 0.8rem; color: var(--muted); }

.segmented { display: flex; border: 1px solid var(--border-strong); border-radius: var(--radius-sm); overflow: hidden; }
.seg { flex: 1; padding: var(--s2); border: 0; background: var(--surface); font: inherit; font-size: 0.82rem; cursor: pointer; color: var(--text); }
.seg + .seg { border-left: 1px solid var(--border); }
.seg--on { background: var(--navy); color: var(--text-inverse); }

.notice { background: var(--warning-bg); border-color: #fcd9a4; }
.notice strong { display: block; color: var(--warning); margin-bottom: var(--s1); }
.notice p { margin: 0; font-size: 0.85rem; color: var(--text); }

.legend .key { display: flex; align-items: center; gap: var(--s2); margin: 0 0 var(--s2); font-size: 0.82rem; color: var(--muted); }
.swatch { width: 14px; height: 14px; border-radius: 4px; border: 1px solid var(--border-strong); flex: none; }
.swatch--seed { background: var(--blue-50); border-color: var(--blue); }
.swatch--away { background: repeating-linear-gradient(45deg, #fff, #fff 3px, #e2e8f0 3px, #e2e8f0 6px); }
.swatch--gone { background: var(--surface-2); border-style: dashed; }
.line { width: 40px; height: 8px; flex: none; }
.line path { stroke: var(--border-strong); stroke-width: 1.5; fill: none; }
.line--dash path { stroke-dasharray: 4 3; }

.canvas-wrap { position: relative; min-height: 420px; }
.canvas {
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  overflow: hidden; height: 620px; touch-action: none; cursor: grab;
  background-image: radial-gradient(var(--border) 1px, transparent 1px);
  background-size: 22px 22px;
}
.canvas--dragging { cursor: grabbing; }
.graph { display: block; transform-origin: 0 0; will-change: transform; }

.canvas-tools { position: absolute; left: var(--s3); bottom: var(--s3); z-index: 2; display: grid; gap: var(--s1); }
.tool {
  width: 32px; height: 32px; border: 1px solid var(--border-strong); background: var(--surface);
  border-radius: var(--radius-sm); cursor: pointer; font-size: 1rem; line-height: 1; color: var(--text);
}
.tool--read {
  display: grid; place-items: center; width: auto; padding: 0 var(--s2);
  font-size: 0.7rem; color: var(--muted); cursor: default;
}
.truncated {
  position: absolute; right: var(--s3); top: var(--s3); z-index: 2; margin: 0;
  background: var(--warning-bg); color: var(--warning); border-radius: var(--radius-pill);
  padding: var(--s1) var(--s3); font-size: 0.78rem;
}

.edge { fill: none; stroke: var(--border-strong); stroke-width: 1.4; }
.edge--coreq { stroke-dasharray: 5 4; }
.edge--lit { stroke: var(--blue); stroke-width: 2.2; }

.node { cursor: pointer; }
.card-bg { fill: var(--surface); stroke: var(--border-strong); stroke-width: 1; }
.node--seed .card-bg { fill: var(--blue-50); stroke: var(--blue); stroke-width: 2; }
.node--on .card-bg { stroke: var(--blue); stroke-width: 2; }
.node--away .card-bg { fill: var(--surface-2); stroke: var(--warning); stroke-dasharray: 5 3; }
.away-mark { font: 700 12px var(--font); fill: var(--warning); text-anchor: end; }
.node--gone { opacity: 0.55; }
.node--gone .card-bg { fill: var(--surface-2); stroke-dasharray: 3 3; }
.node:focus-visible .card-bg { stroke: var(--blue); stroke-width: 2.5; }

.code { font: 600 12px var(--font-mono); fill: var(--text); }
.period { font: 500 10px var(--font); fill: var(--muted); text-anchor: end; }
.name { font: 400 11px var(--font); fill: var(--muted); }

.panel { position: relative; display: grid; gap: var(--s2); justify-items: start; }
.panel h2 { margin: 0; font-size: 1.05rem; font-family: var(--font-mono); }
.panel-title { margin: 0; font-weight: 600; }
.meta { margin: 0; font-size: 0.85rem; color: var(--muted); }
.warn { margin: 0; font-size: 0.85rem; color: var(--warning); background: var(--warning-bg); padding: var(--s2); border-radius: var(--radius-sm); }
.close { position: absolute; top: var(--s2); right: var(--s2); border: 0; background: none; font-size: 1.3rem; line-height: 1; cursor: pointer; color: var(--muted); }

@media (max-width: 900px) {
  .split, .split:has(.panel) { grid-template-columns: minmax(0, 1fr); }
  .canvas { height: 480px; }
  /* Stacked, the rail fills a phone screen and the graph - the thing the page
     is for - starts below the fold. The controls read fine underneath it. */
  .canvas-wrap { order: -1; }
  .panel { order: -2; }
}
</style>
