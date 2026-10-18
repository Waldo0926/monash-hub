<script setup lang="ts">
import { CAMPUS_CHOICES } from '~/composables/useCampuses'
/**
 * The degree picker.
 *
 * Campus filters this list rather than marking it, which is the opposite of
 * the unit tree. There a prerequisite Malaysia does not teach still has to be
 * shown, because the rule names it and the student has to satisfy it some
 * other way. Here there is no other way: a degree that is not taught at your
 * campus is not one you can enrol in, and listing it would be offering
 * something that does not exist.
 */
const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()

const q = ref(String(route.query.q || ''))
const campus = ref(String(route.query.campus ?? 'Malaysia'))
const draft = ref(q.value)
const { year, setYear } = useHandbookYear()
const { data: facets } = await useApiFetch<any>('/v1/courses/filters')

const query = computed(() => {
  const params = new URLSearchParams({ limit: '200' })
  if (q.value) params.set('q', q.value)
  if (campus.value) params.set('campus', campus.value)
  if (year.value) params.set('year', String(year.value))
  return params.toString()
})

const { data, pending } = await useLocalisedApiFetch<any>(
  () => `/v1/courses?${query.value}`,
  { watch: [q, campus, year] }
)

watch([q, campus], () => {
  router.replace({
    query: {
      ...(q.value ? { q: q.value } : {}),
      ...(campus.value ? { campus: campus.value } : {}),
      ...(year.value ? { year: String(year.value) } : {})
    }
  })
})

/** The newest year is the default, so choosing it clears `?year=`. */
function pickYear(y: number) {
  setYear(y === facets.value?.years?.[0] ? null : y)
}

function search() {
  q.value = draft.value.trim()
}

const campusName = useCampusName()
const campusLabel = computed(() => campusName(campus.value))

/**
 * Two columns, so the whole list fits on about one screen and each type
 * scrolls on its own. Undergraduate types go on the left and postgraduate on
 * the right, most common first, which is the order a student scans in.
 * Honours goes on the left under the double degrees: it is an undergraduate
 * award, and the postgraduate side is already the longer column.
 */
const LEFT = [
  'UG specialist',
  'UG comprehensive',
  'UG double',
  'Honours - 1 yr',
  'Vertical double',
  'UG diploma'
]
const RIGHT = [
  'PG Masters',
  'Masters by research',
  'Doctorate by research',
  'Higher doctorate',
  'PG Grad Cert / Grad Dip',
  'PG coursework double'
]

/** Rows a panel shows before it starts to scroll. Mirrors the CSS max-height. */
const VISIBLE_ROWS = 6

const TYPE_KEYS: Record<string, string> = {
  'UG specialist': 'courses.type.ugSpecialist',
  'UG comprehensive': 'courses.type.ugComprehensive',
  'UG double': 'courses.type.ugDouble',
  'Vertical double': 'courses.type.verticalDouble',
  'Honours - 1 yr': 'courses.type.honoursOneYear',
  'UG diploma': 'courses.type.ugDiploma',
  'PG Grad Cert / Grad Dip': 'courses.type.pgCertificateDiploma',
  'PG Masters': 'courses.type.pgMasters',
  'PG coursework double': 'courses.type.pgCourseworkDouble',
  'Masters by research': 'courses.type.mastersResearch',
  'Doctorate by research': 'courses.type.doctorateResearch',
  'Higher doctorate': 'courses.type.higherDoctorate',
  'Non award pathway': 'courses.type.nonAward',
  'Other': 'courses.otherType'
}

function typeLabel(type: string) {
  const key = TYPE_KEYS[type]
  return key ? $t(key) : type
}

type Group = { type: string; courses: any[] }

const columns = computed(() => {
  const buckets = new Map<string, any[]>()
  for (const course of data.value?.results || []) {
    const key = course.course_type_raw || course.course_type || 'Other'
    if (!buckets.has(key)) buckets.set(key, [])
    buckets.get(key)!.push(course)
  }
  const take = (order: string[]): Group[] =>
    order.filter((type) => buckets.has(type)).map((type) => ({ type, courses: buckets.get(type)! }))
  const left = take(LEFT)
  const right = take(RIGHT)

  // Pathways, "Other" and any type the Handbook adds later go under whichever
  // column is shorter, so neither side ends with a long empty gap.
  const placed = new Set([...LEFT, ...RIGHT])
  const rest = [...buckets.keys()]
    .filter((type) => !placed.has(type))
    .sort((a, b) => (a === 'Other' ? 1 : b === 'Other' ? -1 : a.localeCompare(b)))
  const height = (groups: Group[]) =>
    groups.reduce((sum, g) => sum + 2 + Math.min(g.courses.length, VISIBLE_ROWS), 0)
  for (const type of rest) {
    const group = { type, courses: buckets.get(type)! }
    ;(height(left) <= height(right) ? left : right).push(group)
  }
  return [left, right].filter((column) => column.length)
})

/**
 * The jump links run in reading order rather than column order: every
 * undergraduate type on the first row of five, then the combined and
 * postgraduate types, so each row is one level of study.
 */
const JUMP_ORDER = [
  'UG specialist',
  'UG comprehensive',
  'UG double',
  'Honours - 1 yr',
  'UG diploma',
  'Vertical double',
  'PG Masters',
  'Masters by research',
  'Doctorate by research',
  'PG Grad Cert / Grad Dip',
  'PG coursework double',
  'Higher doctorate'
]

const jumpGroups = computed(() => {
  const rank = (type: string) => {
    const i = JUMP_ORDER.indexOf(type)
    return i < 0 ? JUMP_ORDER.length : i
  }
  return columns.value.flat().sort((a, b) => rank(a.type) - rank(b.type))
})

/** Lets a long "A/B" label wrap at the slash instead of mid-word. */
function breakAfterSlash(label: string) {
  return label.replace(/\//g, '/\u200b')
}

/** A stable anchor for each panel, so the jump links and shared URLs work. */
function anchor(type: string) {
  return `type-${type.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')}`
}

/** A jump link has to land on an open panel, even one the reader folded. */
function reveal(type: string) {
  const details = document.querySelector<HTMLDetailsElement>(`#${anchor(type)} details`)
  if (details) details.open = true
}

/**
 * How many degrees sit below the visible part of each panel. A list that
 * scrolls inside a card does not look scrollable until you try, so the
 * panel says how many more there are until the reader reaches the end.
 */
const lists = new Map<string, HTMLElement>()
const below = reactive<Record<string, number>>({})

function bindList(type: string, el: unknown) {
  if (el instanceof HTMLElement) lists.set(type, el)
  else lists.delete(type)
}

function measure(type: string) {
  const el = lists.get(type)
  if (!el) return
  const bottom = el.scrollTop + el.clientHeight
  let hidden = 0
  for (const item of el.children as HTMLCollectionOf<HTMLElement>) {
    if (item.offsetTop + item.offsetHeight > bottom + 1) hidden++
  }
  below[type] = hidden
}

function measureAll() {
  for (const type of lists.keys()) measure(type)
}

function scrollDown(type: string) {
  const el = lists.get(type)
  el?.scrollBy({ top: el.clientHeight * 0.8, behavior: 'smooth' })
}

watch(columns, () => nextTick(measureAll))
onMounted(() => {
  measureAll()
  window.addEventListener('resize', measureAll)
})
onBeforeUnmount(() => window.removeEventListener('resize', measureAll))

useSeoMeta({ title: () => $t('courses.title') })
</script>

<template>
  <div class="page">
    <header class="intro">
      <h1>{{ $t('courses.title') }}</h1>
      <p class="lede">{{ $t('courses.lede') }}</p>
    </header>

    <div class="controls">
      <form class="finder" @submit.prevent="search">
        <input
          v-model="draft"
          class="field"
          :placeholder="$t('courses.searchPlaceholder')"
          :aria-label="$t('courses.search')"
          autocomplete="off"
        />
        <button class="btn btn--primary" type="submit">{{ $t('courses.search') }}</button>
      </form>
      <label class="campus">
        <span class="tiny muted">{{ $t('tree.campus') }}</span>
        <select v-model="campus" class="field">
          <option v-for="choice in CAMPUS_CHOICES" :key="choice" :value="choice">{{ campusName(choice) }}</option>
          <option value="">{{ $t('tree.campusAny') }}</option>
        </select>
      </label>
      <YearPicker
        :model-value="year ?? data?.academic_year"
        :years="facets?.years || []"
        @update:model-value="pickYear"
      />
    </div>

    <p v-if="!pending" class="count">
      {{ campus ? $t('courses.countAt', { n: data?.total ?? 0, campus: campusLabel }) : $t('courses.count', { n: data?.total ?? 0 }) }}
    </p>

    <Skeleton v-if="pending" :lines="8" />
    <EmptyState v-else-if="!data?.total" :title="$t('courses.noneTitle')" :body="$t('courses.noneBody')" />

    <template v-else>
      <nav class="jump" :aria-label="$t('courses.jump')">
        <a
          v-for="group in jumpGroups"
          :key="group.type"
          :href="`#${anchor(group.type)}`"
          class="jump-link"
          @click="reveal(group.type)"
        >
          <span class="jump-label">{{ breakAfterSlash(typeLabel(group.type)) }}</span>
          <span class="jump-n">{{ group.courses.length }}</span>
        </a>
      </nav>

      <div class="board">
        <div v-for="(column, i) in columns" :key="i" class="column">
          <section v-for="group in column" :id="anchor(group.type)" :key="group.type" class="panel">
            <details open>
              <summary class="panel-head">
                <h2>{{ typeLabel(group.type) }}</h2>
                <span class="tally" :aria-label="$t('courses.groupCount', { n: group.courses.length })">
                  {{ group.courses.length }}
                </span>
                <PlanIcon name="chevron" class="caret" />
              </summary>
              <ul
                :ref="(el) => bindList(group.type, el)"
                class="panel-list"
                @scroll.passive="measure(group.type)"
              >
                <li v-for="course in group.courses" :key="course.course_code">
                  <CourseCard :course="course" compact />
                </li>
              </ul>
              <button
                v-if="below[group.type]"
                type="button"
                class="more"
                @click="scrollDown(group.type)"
              >
                {{ $t('courses.moreBelow', { n: below[group.type] ?? 0 }) }}
                <PlanIcon name="chevron" :size="14" class="more-icon" />
              </button>
            </details>
          </section>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page { max-width: var(--container); margin: 0 auto; padding: var(--s5) var(--s4) var(--s7); }
.intro h1 { margin: 0 0 var(--s2); }
.lede { color: var(--muted); margin: 0 0 var(--s5); max-width: var(--measure-lede); }

/* Search, campus and year share one row and one control height. On a phone
   the search takes its own row and the two selects split the next one. */
.controls {
  display: grid; grid-template-columns: minmax(0, 1fr) 11rem 8rem; gap: var(--s3);
  align-items: end; margin-bottom: var(--s3);
}
.finder { display: flex; gap: var(--s2); }
.finder .btn { flex: none; }
.campus { display: grid; gap: var(--s1); min-width: 0; }
.controls :deep(.field) { height: 44px; }
.count { color: var(--muted); font-size: 0.9rem; margin: 0 0 var(--s5); }

/* Five equal columns, so ten types make two even rows. */
.jump {
  display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: var(--s2);
  margin: 0 0 var(--s4);
}
.jump-link {
  display: flex; align-items: center; justify-content: space-between; gap: var(--s2);
  min-height: 40px; padding: 6px var(--s3); border: 1px solid var(--border);
  border-radius: var(--radius-sm); background: var(--surface); color: var(--text);
  font-size: 0.85rem; line-height: 1.3; text-decoration: none;
}
.jump-link:hover { border-color: var(--blue); color: var(--blue); }
.jump-label { min-width: 0; }
.jump-n {
  flex: none; font: 600 0.75rem var(--font-mono); color: var(--navy); background: var(--blue-50);
  border-radius: var(--radius-pill); padding: 1px var(--s2); min-width: 1.75rem; text-align: center;
}

.board {
  display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: var(--s4);
  align-items: start;
}
.column { display: grid; gap: var(--s4); min-width: 0; }

.panel {
  scroll-margin-top: calc(var(--header-h, 64px) + var(--s4));
  background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius);
  box-shadow: var(--shadow-sm); overflow: hidden;
}
.panel-head {
  display: flex; align-items: center; gap: var(--s2); padding: var(--s3) var(--s4);
  cursor: pointer; list-style: none; user-select: none;
}
.panel-head::-webkit-details-marker { display: none; }
.panel-head:hover h2 { color: var(--blue); }
.panel-head:focus-visible { outline-offset: -2px; }
.panel-head h2 { font-size: 0.95rem; font-weight: 600; margin: 0; flex: 1; min-width: 0; }
.tally {
  font: 600 0.75rem var(--font-mono); color: var(--navy); background: var(--blue-50);
  border-radius: var(--radius-pill); padding: 2px var(--s2); min-width: 1.75rem; text-align: center;
}
.caret { color: var(--muted-2); transition: transform 0.15s ease; }
details[open] .caret { transform: rotate(90deg); }
details[open] .panel-head { border-bottom: 1px solid var(--border); }

/* Six rows, then the list scrolls inside the panel. The two "local" layers
   cover the shadows once the list is scrolled to that end, so a shadow only
   shows where there is more to see. */
.panel-list {
  /* Positioned so each row's offsetTop is measured from the list itself. */
  position: relative; list-style: none; margin: 0; padding: var(--s1) 0; max-height: 22.5rem; overflow-y: auto;
  overscroll-behavior: contain;
  background:
    linear-gradient(var(--surface) 30%, transparent) top / 100% 28px no-repeat,
    linear-gradient(transparent, var(--surface) 70%) bottom / 100% 28px no-repeat,
    radial-gradient(farthest-side at 50% 0, rgba(12, 27, 42, 0.14), transparent) top / 100% 10px no-repeat,
    radial-gradient(farthest-side at 50% 100%, rgba(12, 27, 42, 0.14), transparent) bottom / 100% 10px no-repeat,
    var(--surface);
  background-attachment: local, local, scroll, scroll;
}
.panel-list li + li { border-top: 1px solid var(--border); }
.more {
  display: flex; align-items: center; justify-content: center; gap: var(--s1);
  width: 100%; padding: 6px var(--s3); border: 0; border-top: 1px solid var(--border);
  background: var(--surface-2); color: var(--muted); font: inherit; font-size: 0.8rem;
  cursor: pointer;
}
.more:hover { color: var(--blue); }
.more:focus-visible { outline-offset: -2px; }
.more-icon { transform: rotate(90deg); }

@media (max-width: 700px) {
  .controls { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); }
  .finder { grid-column: 1 / -1; }
}
@media (max-width: 900px) {
  .board { grid-template-columns: minmax(0, 1fr); }
  /* One swipeable row of jump links instead of a grid too narrow to read. */
  .jump {
    display: flex; overflow-x: auto; scrollbar-width: none;
    margin-inline: calc(-1 * var(--s4)); padding-inline: var(--s4);
  }
  .jump-link { flex: none; min-height: 36px; border-radius: var(--radius-pill); white-space: nowrap; }
  .jump::-webkit-scrollbar { display: none; }
  /* On a phone the page itself scrolls, so a shorter panel and normal scroll
     chaining keep a swipe from getting stuck inside a list. */
  .panel-list { max-height: 19rem; overscroll-behavior: auto; }
}
@media (prefers-reduced-motion: reduce) {
  .caret { transition: none; }
}
</style>
