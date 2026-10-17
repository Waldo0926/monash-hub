<script setup lang="ts">
/**
 * Unit search. The point is fewer steps than the Handbook itself: type a code
 * or a word, narrow by campus, teaching period, level, subject or whether an
 * exam is listed.
 *
 * Everything that changes the result list lives in the URL, page number
 * included, so a filtered search can be shared and the back button returns
 * to the same page of results.
 */
const route = useRoute()
const router = useRouter()
const { $t, $term } = useNuxtApp() as any

const PAGE = 24

const query = ref((route.query.q as string) || '')
const filters = reactive({
  // Empty is the current Handbook. A year is kept in the URL so a link to the
  // 2025 list stays the 2025 list, and the unit cards carry it on.
  year: (route.query.year as string) || '',
  campus: (route.query.campus as string) || '',
  teaching_period: (route.query.teaching_period as string) || '',
  level: (route.query.level as string) || '',
  prefix: (route.query.prefix as string) || '',
  has_exam: (route.query.has_exam as string) || '',
  sort: (route.query.sort as string) || 'relevance'
})
const page = ref(Math.max(1, Number(route.query.page) || 1))
const drawerOpen = ref(false)

const { data: facets } = await useApiFetch<any>(
  () => `/v1/units/filters${filters.year ? `?year=${filters.year}` : ''}`,
  { watch: [() => filters.year] }
)

const shownYear = computed({
  get: () => Number(filters.year) || facets.value?.academic_year || null,
  set: (y: number) => {
    // The newest year is the default, so it leaves the URL clean.
    filters.year = y === Math.max(...(facets.value?.years || [y])) ? '' : String(y)
  }
})

const requestPath = computed(() => {
  const params = new URLSearchParams()
  if (query.value) params.set('q', query.value)
  for (const [key, value] of Object.entries(filters)) if (value) params.set(key, String(value))
  params.set('limit', String(PAGE))
  if (page.value > 1) params.set('offset', String((page.value - 1) * PAGE))
  return `/v1/units?${params.toString()}`
})

const { data, pending, error, refresh } = await useLocalisedApiFetch<any>(() => requestPath.value, {
  watch: [requestPath]
})

function syncUrl() {
  const q: Record<string, string> = {}
  if (query.value) q.q = query.value
  for (const [key, value] of Object.entries(filters)) if (value && value !== 'relevance') q[key] = String(value)
  if (page.value > 1) q.page = String(page.value)
  router.replace({ query: q })
}
watch([query, filters, page], syncUrl, { deep: true })

// A new search or filter starts again from the first page; leaving page 4 in
// place would show an empty page for a query with two pages of results.
watch([query, () => ({ ...filters })], () => { page.value = 1 }, { deep: true })

// --- filters as chips ---------------------------------------------------------------

type FilterKey = 'campus' | 'teaching_period' | 'level' | 'prefix' | 'has_exam'

const active = computed(() => {
  const chips: { key: FilterKey; label: string }[] = []
  if (filters.campus) chips.push({ key: 'campus', label: $term('campus', filters.campus) || filters.campus })
  if (filters.teaching_period) {
    chips.push({ key: 'teaching_period', label: $term('period', filters.teaching_period) || filters.teaching_period })
  }
  if (filters.level) chips.push({ key: 'level', label: $term('level', filters.level) || filters.level })
  if (filters.prefix) chips.push({ key: 'prefix', label: filters.prefix })
  if (filters.has_exam) {
    chips.push({ key: 'has_exam', label: filters.has_exam === 'true' ? $t('units.hasExam') : $t('units.noExam') })
  }
  return chips
})

function clear(key: FilterKey) {
  filters[key] = ''
}

function reset() {
  filters.campus = ''
  filters.teaching_period = ''
  filters.level = ''
  filters.prefix = ''
  filters.has_exam = ''
}

// --- paging ---------------------------------------------------------------------------

const total = computed(() => data.value?.total ?? 0)
const pages = computed(() => Math.max(1, Math.ceil(total.value / PAGE)))
const shownFrom = computed(() => (total.value ? (page.value - 1) * PAGE + 1 : 0))
const shownTo = computed(() => Math.min(total.value, page.value * PAGE))

/** Page numbers to draw: the first, the last, and two either side of the current one. */
const pageList = computed(() => {
  const out: (number | null)[] = []
  for (let p = 1; p <= pages.value; p++) {
    if (p === 1 || p === pages.value || Math.abs(p - page.value) <= 2) out.push(p)
    else if (out[out.length - 1] !== null) out.push(null)
  }
  return out
})

const top = ref<HTMLElement | null>(null)
function goTo(p: number) {
  page.value = Math.min(Math.max(1, p), pages.value)
  top.value?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

// --- view --------------------------------------------------------------------------------

// Cards show more about each unit; the list fits three times as many on a
// screen for someone scanning codes. Remembered per browser.
const VIEW_KEY = 'mh_units_view'
const view = ref<'cards' | 'list'>('cards')
onMounted(() => {
  try {
    if (localStorage.getItem(VIEW_KEY) === 'list') view.value = 'list'
  } catch { /* no storage, cards it is */ }
})
watch(view, (v) => {
  try { localStorage.setItem(VIEW_KEY, v) } catch { /* not remembered */ }
})

const { withYear } = useHandbookYear()

/** Short teaching period labels for the list view, "S1 · S2" rather than two full names. */
function periodsOf(unit: any): string {
  const seen: string[] = []
  for (const o of unit.offerings || []) {
    const label = o.short || $term('period', o.teaching_period) || o.teaching_period
    if (label && !seen.includes(label)) seen.push(label)
  }
  return seen.join(' · ')
}

useSeoMeta({
  title: () => $t('units.metaTitle'),
  description: 'Search Monash Handbook units by code, title, campus, teaching period and assessment.'
})
</script>

<template>
  <div class="container">
    <h1>{{ $t('units.title') }}</h1>
    <p class="muted">{{ $t('units.lead', { year: data?.academic_year || '' }) }}</p>

    <SearchInput
      v-model="query"
      :placeholder="$t('units.searchPlaceholder')"
      @submit="v => (query = v)"
    />

    <button
      class="btn btn--ghost btn--small filter-toggle"
      type="button"
      :aria-expanded="drawerOpen"
      aria-controls="unit-filters"
      @click="drawerOpen = !drawerOpen"
    >
      {{ $t('units.filters') }}<span v-if="active.length" class="toggle-count">{{ active.length }}</span>
      {{ drawerOpen ? ' ▲' : ' ▼' }}
    </button>

    <div class="layout">
      <aside id="unit-filters" class="filters" :class="{ open: drawerOpen }">
        <h2 class="small">{{ $t('units.filters') }}</h2>

        <YearPicker v-model="shownYear" :years="facets?.years || []" class="filter" />

        <fieldset v-if="facets?.campuses?.length" class="filter">
          <legend class="tiny muted">{{ $t('units.campus') }}</legend>
          <div class="pills">
            <label class="pill" :class="{ on: !filters.campus }">
              <input v-model="filters.campus" type="radio" name="campus" value="" class="visually-hidden">
              {{ $t('units.anyCampus') }}
            </label>
            <!-- The value stays the Handbook's own string: it is the filter the
                 API matches on. Only the label is translated. -->
            <label v-for="campus in facets.campuses" :key="campus" class="pill" :class="{ on: filters.campus === campus }">
              <input v-model="filters.campus" type="radio" name="campus" :value="campus" class="visually-hidden">
              {{ $term('campus', campus) }}
            </label>
          </div>
        </fieldset>

        <label class="filter">
          <span class="tiny muted">{{ $t('units.teachingPeriod') }}</span>
          <select v-model="filters.teaching_period" class="field">
            <option value="">{{ $t('units.anyPeriod') }}</option>
            <option v-for="period in facets?.teaching_periods || []" :key="period" :value="period">
              {{ $term('period', period) }}
            </option>
          </select>
        </label>

        <fieldset v-if="facets?.levels?.length" class="filter">
          <legend class="tiny muted">{{ $t('units.level') }}</legend>
          <div class="pills">
            <label class="pill" :class="{ on: !filters.level }">
              <input v-model="filters.level" type="radio" name="level" value="" class="visually-hidden">
              {{ $t('units.any') }}
            </label>
            <label v-for="level in facets.levels" :key="level" class="pill" :class="{ on: filters.level === level }">
              <input v-model="filters.level" type="radio" name="level" :value="level" class="visually-hidden">
              {{ $term('level', level) }}
            </label>
          </div>
        </fieldset>

        <label v-if="facets?.prefixes?.length" class="filter">
          <span class="tiny muted">{{ $t('units.prefix') }}</span>
          <select v-model="filters.prefix" class="field">
            <option value="">{{ $t('units.anyPrefix') }}</option>
            <option v-for="prefix in facets.prefixes" :key="prefix" :value="prefix">{{ prefix }}</option>
          </select>
        </label>

        <fieldset class="filter">
          <legend class="tiny muted">{{ $t('units.examination') }}</legend>
          <div class="pills">
            <label class="pill" :class="{ on: !filters.has_exam }">
              <input v-model="filters.has_exam" type="radio" name="exam" value="" class="visually-hidden">
              {{ $t('units.any') }}
            </label>
            <label class="pill" :class="{ on: filters.has_exam === 'true' }">
              <input v-model="filters.has_exam" type="radio" name="exam" value="true" class="visually-hidden">
              {{ $t('units.hasExamShort') }}
            </label>
            <label class="pill" :class="{ on: filters.has_exam === 'false' }">
              <input v-model="filters.has_exam" type="radio" name="exam" value="false" class="visually-hidden">
              {{ $t('units.noExamShort') }}
            </label>
          </div>
        </fieldset>

        <button v-if="active.length" class="btn btn--ghost btn--small" type="button" @click="reset">
          {{ $t('units.clearFilters') }}
        </button>
        <p class="tiny muted note">{{ $t('units.examNote') }}</p>
      </aside>

      <div ref="top" class="results">
        <div class="bar">
          <p class="small count" aria-live="polite">
            <template v-if="data && total > PAGE">
              {{ $t('units.showing', { from: shownFrom, to: shownTo, total }) }}
            </template>
            <template v-else-if="data">
              {{ total === 1 ? $t('units.countOne') : $t('units.count', { count: total }) }}
            </template>
          </p>
          <div class="bar-tools">
            <label class="sort">
              <span class="tiny muted">{{ $t('units.sort') }}</span>
              <select v-model="filters.sort" class="field field--small">
                <option value="relevance">{{ $t('units.sortRelevance') }}</option>
                <option value="code">{{ $t('units.sortCode') }}</option>
                <option value="title">{{ $t('units.sortTitle') }}</option>
              </select>
            </label>
            <div class="views" role="group" :aria-label="$t('units.view')">
              <button
                type="button"
                class="view-btn"
                :class="{ on: view === 'cards' }"
                :aria-pressed="view === 'cards'"
                :title="$t('units.viewCards')"
                @click="view = 'cards'"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 4h7v7H4z M13 4h7v7h-7z M4 13h7v7H4z M13 13h7v7h-7z" /></svg>
                <span class="visually-hidden">{{ $t('units.viewCards') }}</span>
              </button>
              <button
                type="button"
                class="view-btn"
                :class="{ on: view === 'list' }"
                :aria-pressed="view === 'list'"
                :title="$t('units.viewList')"
                @click="view = 'list'"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16 M4 12h16 M4 18h16" /></svg>
                <span class="visually-hidden">{{ $t('units.viewList') }}</span>
              </button>
            </div>
          </div>
        </div>

        <p v-if="active.length" class="chips">
          <button
            v-for="chip in active"
            :key="chip.key"
            type="button"
            class="chip"
            :aria-label="$t('units.removeFilter', { filter: chip.label })"
            @click="clear(chip.key)"
          >
            {{ chip.label }}<span aria-hidden="true" class="chip-x">×</span>
          </button>
          <button type="button" class="chip-clear tiny" @click="reset">{{ $t('units.clearFilters') }}</button>
        </p>

        <ErrorState v-if="error" :error="error" :on-retry="refresh" />
        <Skeleton v-else-if="pending && !data" :lines="8" />
        <template v-else-if="data">
          <div :class="{ loading: pending }">
            <div v-if="data.results.length && view === 'cards'" class="grid">
              <UnitCard v-for="unit in data.results" :key="unit.unit_code" :unit="unit" />
            </div>
            <ul v-else-if="data.results.length" class="list card">
              <li v-for="unit in data.results" :key="unit.unit_code">
                <NuxtLink :to="withYear(`/units/${unit.unit_code}`)" class="row">
                  <span class="row-code mono">{{ unit.unit_code }}</span>
                  <span class="row-title">{{ unit.title }}</span>
                  <span class="row-meta tiny muted">
                    <span v-if="unit.rating?.count" class="row-rating" :title="$t('reviews.cardTitle')">
                      <StarRating :value="unit.rating.average" size="sm" />
                      {{ Number(unit.rating.average).toFixed(1) }}
                    </span>
                    <span v-if="periodsOf(unit)">{{ periodsOf(unit) }}</span>
                    <span v-if="unit.credit_points">{{ $t('plan.cp', { n: unit.credit_points }) }}</span>
                  </span>
                </NuxtLink>
              </li>
            </ul>
            <EmptyState v-else :title="$t('units.empty')" :hint="$t('units.emptyHint')">
              <button v-if="active.length" type="button" class="btn btn--ghost" @click="reset">
                {{ $t('units.clearFilters') }}
              </button>
              <NuxtLink :to="`/search?q=${encodeURIComponent(query)}`" class="btn btn--ghost">
                {{ $t('units.searchEverything') }}
              </NuxtLink>
              <NuxtLink to="/community" class="btn">{{ $t('units.askCommunity') }}</NuxtLink>
            </EmptyState>
          </div>

          <nav v-if="pages > 1" class="pager" :aria-label="$t('units.pages')">
            <button type="button" class="page-btn" :disabled="page === 1" @click="goTo(page - 1)">
              ‹ <span class="page-word">{{ $t('units.prev') }}</span>
            </button>
            <template v-for="(p, i) in pageList" :key="i">
              <span v-if="p === null" class="page-gap" aria-hidden="true">…</span>
              <button
                v-else
                type="button"
                class="page-btn page-num"
                :class="{ on: p === page }"
                :aria-current="p === page ? 'page' : undefined"
                @click="goTo(p)"
              >{{ p }}</button>
            </template>
            <button type="button" class="page-btn" :disabled="page === pages" @click="goTo(page + 1)">
              <span class="page-word">{{ $t('units.next') }}</span> ›
            </button>
          </nav>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
h1 { margin-bottom: var(--s2); }
.layout { display: grid; grid-template-columns: 260px minmax(0, 1fr); gap: var(--s6); margin-top: var(--s5); }
.filters {
  display: grid; gap: var(--s4); align-content: start;
  position: sticky; top: calc(var(--header-h) + var(--s4));
}
.filters h2 { margin: 0; }
.filter { display: grid; gap: var(--s1); border: 0; margin: 0; padding: 0; min-width: 0; }
.filter legend { padding: 0; margin-bottom: var(--s1); }
.note { margin: 0; }
.pills { display: flex; flex-wrap: wrap; gap: 6px; }
.pill {
  display: inline-flex; align-items: center; min-height: 32px; padding: 0 12px; cursor: pointer;
  border: 1px solid var(--border-strong); border-radius: var(--radius-pill);
  background: var(--surface); font-size: 0.85rem;
}
.pill:hover { border-color: var(--brand); }
.pill.on { background: var(--navy); border-color: var(--navy); color: var(--text-inverse); }
.pill:has(input:focus-visible) { outline: 2px solid var(--brand); outline-offset: 2px; }

.results { min-width: 0; scroll-margin-top: calc(var(--header-h) + var(--s4)); }
.bar { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: var(--s3); margin-bottom: var(--s3); }
.count { margin: 0; font-weight: 600; }
.bar-tools { display: flex; align-items: center; gap: var(--s3); }
.sort { display: flex; align-items: center; gap: var(--s2); }
.field--small { width: auto; padding: 4px var(--s2); font-size: 0.85rem; }
.views { display: inline-flex; border: 1px solid var(--border-strong); border-radius: var(--radius-sm); overflow: hidden; }
.view-btn {
  display: grid; place-items: center; width: 36px; height: 32px; border: 0; background: var(--surface); cursor: pointer;
}
.view-btn + .view-btn { border-left: 1px solid var(--border-strong); }
.view-btn svg { width: 16px; height: 16px; fill: none; stroke: var(--muted); stroke-width: 2; stroke-linecap: round; }
.view-btn.on { background: var(--surface-2); }
.view-btn.on svg { stroke: var(--text); }

.chips { display: flex; flex-wrap: wrap; align-items: center; gap: var(--s2); margin: 0 0 var(--s3); }
.chip {
  display: inline-flex; align-items: center; gap: 6px; padding: 3px 10px 3px 12px; cursor: pointer;
  border: 1px solid var(--blue-50); border-radius: var(--radius-pill); background: var(--blue-50);
  color: var(--navy); font: inherit; font-size: 0.82rem; font-weight: 500;
}
.chip:hover { border-color: var(--brand); }
.chip-x { font-size: 1rem; line-height: 1; color: var(--muted); }
.chip-clear { border: 0; background: none; color: var(--muted); text-decoration: underline; cursor: pointer; font-family: inherit; }

.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
.loading { opacity: 0.55; transition: opacity 0.15s; }
.list { list-style: none; margin: 0; padding: 0; overflow: hidden; }
.list li + li { border-top: 1px solid var(--border); }
.row {
  display: grid; grid-template-columns: 92px minmax(0, 1fr) auto; gap: var(--s3); align-items: center;
  padding: var(--s3) var(--s4); color: var(--text);
}
.row:hover { background: var(--surface-2); text-decoration: none; }
.row-code { font-weight: 700; color: var(--navy); }
.row-title { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.row-meta { display: flex; gap: var(--s3); white-space: nowrap; }
.row-rating { display: inline-flex; align-items: center; gap: 4px; }

.pager { display: flex; flex-wrap: wrap; justify-content: center; align-items: center; gap: 4px; margin-top: var(--s5); }
.page-btn {
  min-width: 36px; height: 36px; padding: 0 10px; cursor: pointer;
  border: 1px solid var(--border-strong); border-radius: var(--radius-sm);
  background: var(--surface); color: var(--text); font: inherit; font-size: 0.88rem;
}
.page-btn:hover:not(:disabled) { border-color: var(--brand); }
.page-btn:disabled { opacity: 0.4; cursor: default; }
.page-btn.on { background: var(--navy); border-color: var(--navy); color: var(--text-inverse); font-weight: 600; }
.page-gap { padding: 0 4px; color: var(--muted); }

.filter-toggle { display: none; margin-top: var(--s3); }
.toggle-count {
  display: inline-grid; place-items: center; min-width: 18px; height: 18px; margin-left: 6px; padding: 0 5px;
  border-radius: var(--radius-pill); background: var(--navy); color: var(--text-inverse); font-size: 0.72rem;
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; gap: var(--s4); }
  .filter-toggle { display: inline-flex; align-items: center; }
  /* On a phone the filters collapse rather than pushing results below the fold. */
  .filters { display: none; position: static; }
  .filters.open { display: grid; padding: var(--s4); border: 1px solid var(--border); border-radius: var(--radius-sm); }
  /* The button above already says Filters. */
  .filters h2 { display: none; }
}
@media (max-width: 600px) {
  .row { grid-template-columns: 80px minmax(0, 1fr); }
  .row-meta { display: none; }
  .page-word { display: none; }
}
@media (prefers-reduced-motion: reduce) {
  .loading { transition: none; }
}
</style>
