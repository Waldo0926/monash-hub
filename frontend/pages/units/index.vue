<script setup lang="ts">
/**
 * Unit search. The point is fewer steps than the Handbook itself: type a code
 * or a word, narrow by campus, teaching period, faculty, school, level,
 * subject or whether an exam is listed.
 *
 * Everything that changes the result list lives in the URL, page number
 * included, so a filtered search can be shared and the back button returns
 * to the same page of results.
 */
import type { TermKind } from '~/i18n/handbook-terms'

const route = useRoute()
const router = useRouter()
const { $t, $term } = useNuxtApp() as any

const PAGE = 24

/** A filter that can hold several values. One value from an older link still works. */
function many(value: unknown): string[] {
  if (Array.isArray(value)) return value.filter((v): v is string => typeof v === 'string' && !!v)
  return typeof value === 'string' && value ? [value] : []
}

const MULTI = ['campus', 'teaching_period', 'faculty', 'school', 'prefix', 'level'] as const
type MultiKey = typeof MULTI[number]

const query = ref((route.query.q as string) || '')
const filters = reactive({
  // Empty is the current Handbook. A year is kept in the URL so a link to the
  // 2025 list stays the 2025 list, and the unit cards carry it on.
  year: (route.query.year as string) || '',
  campus: many(route.query.campus),
  teaching_period: many(route.query.teaching_period),
  faculty: many(route.query.faculty),
  school: many(route.query.school),
  prefix: many(route.query.prefix),
  level: many(route.query.level),
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

/** The query and filters as URL parameters, shared by the result list and the counts. */
const filterParams = computed(() => {
  const params = new URLSearchParams()
  if (query.value) params.set('q', query.value)
  if (filters.year) params.set('year', filters.year)
  for (const key of MULTI) for (const value of filters[key]) params.append(key, value)
  if (filters.has_exam) params.set('has_exam', filters.has_exam)
  return params
})

const requestPath = computed(() => {
  const params = new URLSearchParams(filterParams.value)
  if (filters.sort !== 'relevance') params.set('sort', filters.sort)
  params.set('limit', String(PAGE))
  if (page.value > 1) params.set('offset', String((page.value - 1) * PAGE))
  return `/v1/units?${params.toString()}`
})

const { data, pending, error, refresh } = await useLocalisedApiFetch<any>(() => requestPath.value, {
  watch: [requestPath]
})

// The numbers beside each checkbox. Fetched on the client after the list, so
// a slow count never holds up the results, and a failed one just hides them.
const facetPath = computed(() => `/v1/units/facets?${filterParams.value.toString()}`)
const { data: facetCounts } = useApiFetch<any>(() => facetPath.value, {
  watch: [facetPath],
  server: false,
  lazy: true
})
const counts = computed(() => facetCounts.value?.counts || null)

function syncUrl() {
  const q: Record<string, string | string[]> = {}
  if (query.value) q.q = query.value
  if (filters.year) q.year = filters.year
  for (const key of MULTI) if (filters[key].length) q[key] = [...filters[key]]
  if (filters.has_exam) q.has_exam = filters.has_exam
  if (filters.sort !== 'relevance') q.sort = filters.sort
  if (page.value > 1) q.page = String(page.value)
  router.replace({ query: q })
}
watch([query, filters, page], syncUrl, { deep: true })

// A new search or filter starts again from the first page; leaving page 4 in
// place would show an empty page for a query with two pages of results.
watch([query, () => JSON.stringify(filters)], () => { page.value = 1 })

// --- filter options ------------------------------------------------------------------

/**
 * How each filter's values are labelled. The value stays the Handbook's own string: it is what the API matches on.
 * The API sends the glossary's label for each value in the reader's language; the local dictionary covers the rest.
 */
const labelled = (kind: TermKind) => (v: string) =>
  facets.value?.labels?.[v] || $term(kind, v) || v
const LABEL: Record<MultiKey, (value: string) => string> = {
  campus: labelled('campus'),
  teaching_period: labelled('period'),
  faculty: labelled('faculty'),
  school: labelled('faculty'),
  prefix: v => v,
  level: labelled('level')
}

const FACET_LIST: Record<MultiKey, string> = {
  campus: 'campuses',
  teaching_period: 'teaching_periods',
  faculty: 'faculties',
  school: 'schools',
  prefix: 'prefixes',
  level: 'levels'
}

function optionsFor(key: MultiKey) {
  return ((facets.value?.[FACET_LIST[key]] || []) as string[]).map(value => ({ value, label: LABEL[key](value) }))
}

const examOptions = computed(() => [
  { value: 'true', label: $t('units.hasExamShort') },
  { value: 'false', label: $t('units.noExamShort') }
])
const examValue = computed({
  get: () => (filters.has_exam ? [filters.has_exam] : []),
  // Two boxes for one yes or no: ticking one unticks the other.
  set: (next: string[]) => { filters.has_exam = next.find(v => v !== filters.has_exam) || '' }
})

// --- filters as chips ---------------------------------------------------------------

type FilterKey = MultiKey | 'has_exam'

const active = computed(() => {
  const chips: { key: FilterKey; value: string; label: string }[] = []
  for (const key of MULTI) for (const value of filters[key]) chips.push({ key, value, label: LABEL[key](value) })
  if (filters.has_exam) {
    chips.push({
      key: 'has_exam',
      value: filters.has_exam,
      label: filters.has_exam === 'true' ? $t('units.hasExam') : $t('units.noExam')
    })
  }
  return chips
})

function clear(key: FilterKey, value: string) {
  if (key === 'has_exam') filters.has_exam = ''
  else filters[key] = filters[key].filter(v => v !== value)
}

function reset() {
  for (const key of MULTI) filters[key] = []
  filters.has_exam = ''
}

// --- phone drawer ---------------------------------------------------------------------

function onKey(event: KeyboardEvent) {
  if (event.key === 'Escape' && drawerOpen.value) drawerOpen.value = false
}
onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => window.removeEventListener('keydown', onKey))
// The page behind an open drawer should not scroll under the finger.
watch(drawerOpen, (open) => { document.documentElement.style.overflow = open ? 'hidden' : '' })
onBeforeUnmount(() => { document.documentElement.style.overflow = '' })

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
      @click="drawerOpen = true"
    >
      <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 6h16 M7 12h10 M10 18h4" /></svg>
      {{ $t('units.filters') }}<span v-if="active.length" class="toggle-count">{{ active.length }}</span>
    </button>

    <div class="layout">
      <div v-if="drawerOpen" class="backdrop" aria-hidden="true" @click="drawerOpen = false" />
      <aside
        id="unit-filters"
        class="filters"
        :class="{ open: drawerOpen }"
        :aria-label="$t('units.filters')"
      >
        <div class="filters-head">
          <h2 class="filters-title">{{ $t('units.filters') }}</h2>
          <button v-if="active.length" type="button" class="clear-btn" @click="reset">
            {{ $t('units.clear') }}
          </button>
          <button type="button" class="close-btn" :aria-label="$t('units.closeFilters')" @click="drawerOpen = false">
            <span aria-hidden="true">×</span>
          </button>
        </div>

        <div class="filters-body">
          <FilterGroup v-if="facets?.years?.length" :title="$t('handbook.year')" open>
            <select
              class="field"
              :value="shownYear ?? ''"
              :aria-label="$t('handbook.year')"
              @change="shownYear = Number(($event.target as HTMLSelectElement).value)"
            >
              <option v-for="y in facets.years" :key="y" :value="y">{{ y }}</option>
            </select>
          </FilterGroup>

          <FilterGroup v-if="facets?.campuses?.length" :title="$t('units.campus')" :selected="filters.campus.length" open>
            <FilterOptions v-model="filters.campus" :options="optionsFor('campus')" :counts="counts?.campus" />
          </FilterGroup>

          <FilterGroup
            v-if="facets?.teaching_periods?.length"
            :title="$t('units.teachingPeriod')"
            :selected="filters.teaching_period.length"
            :open="!!filters.teaching_period.length"
          >
            <FilterOptions
              v-model="filters.teaching_period"
              :options="optionsFor('teaching_period')"
              :counts="counts?.teaching_period"
            />
          </FilterGroup>

          <FilterGroup
            v-if="facets?.faculties?.length"
            :title="$t('units.faculty')"
            :selected="filters.faculty.length"
            :open="!!filters.faculty.length"
          >
            <FilterOptions v-model="filters.faculty" :options="optionsFor('faculty')" :counts="counts?.faculty" :limit="10" />
          </FilterGroup>

          <FilterGroup
            v-if="facets?.schools?.length"
            :title="$t('units.school')"
            :selected="filters.school.length"
            :open="!!filters.school.length"
          >
            <FilterOptions
              v-model="filters.school"
              :options="optionsFor('school')"
              :counts="counts?.school"
              searchable
            />
          </FilterGroup>

          <FilterGroup
            v-if="facets?.prefixes?.length"
            :title="$t('units.prefix')"
            :selected="filters.prefix.length"
            :open="!!filters.prefix.length"
          >
            <FilterOptions v-model="filters.prefix" :options="optionsFor('prefix')" :counts="counts?.prefix" searchable />
          </FilterGroup>

          <FilterGroup
            v-if="facets?.levels?.length"
            :title="$t('units.level')"
            :selected="filters.level.length"
            :open="!!filters.level.length"
          >
            <FilterOptions v-model="filters.level" :options="optionsFor('level')" :counts="counts?.level" :limit="0" />
          </FilterGroup>

          <FilterGroup :title="$t('units.examination')" :selected="filters.has_exam ? 1 : 0" :open="!!filters.has_exam">
            <FilterOptions v-model="examValue" :options="examOptions" :counts="counts?.has_exam" :limit="0" />
            <p class="tiny muted note">{{ $t('units.examNote') }}</p>
          </FilterGroup>
        </div>

        <div class="filters-foot">
          <button type="button" class="btn show-btn" @click="drawerOpen = false">
            {{ $t('units.showResults', { count: total }) }}
          </button>
        </div>
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
            :key="`${chip.key}:${chip.value}`"
            type="button"
            class="chip"
            :aria-label="$t('units.removeFilter', { filter: chip.label })"
            @click="clear(chip.key, chip.value)"
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
/* A card that scrolls on its own, so the headings stay in reach beside a
   long result list. */
.filters {
  display: flex; flex-direction: column; align-self: start; min-width: 0;
  position: sticky; top: calc(var(--header-h) + var(--s4));
  max-height: calc(100vh - var(--header-h) - var(--s6));
  border: 1px solid var(--border); border-radius: var(--radius); background: var(--surface);
}
.filters-head { display: flex; align-items: center; gap: var(--s2); padding: var(--s3) var(--s4); }
.filters-title { flex: 1; margin: 0; font-family: inherit; font-size: 1rem; font-weight: 700; }
.clear-btn {
  padding: 4px 10px; border: 1px solid var(--border-strong); border-radius: var(--radius-sm);
  background: var(--surface); color: var(--brand); font: inherit; font-size: 0.82rem; font-weight: 600; cursor: pointer;
}
.clear-btn:hover { border-color: var(--brand); }
.close-btn {
  display: none; width: 36px; height: 36px; border: 0; border-radius: var(--radius-sm);
  background: none; color: var(--muted); font-size: 1.5rem; line-height: 1; cursor: pointer;
}
.filters-body { flex: 1; min-height: 0; overflow-y: auto; overscroll-behavior: contain; padding: 0 var(--s4) var(--s2); }
.filters-foot { display: none; }
.note { margin: var(--s2) 0 0; }
.backdrop { display: none; }

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

.filter-toggle { display: none; gap: 6px; margin-top: var(--s3); }
.filter-toggle svg { width: 16px; height: 16px; fill: none; stroke: currentColor; stroke-width: 2; stroke-linecap: round; }
.toggle-count {
  display: inline-grid; place-items: center; min-width: 18px; height: 18px; margin-left: 6px; padding: 0 5px;
  border-radius: var(--radius-pill); background: var(--navy); color: var(--text-inverse); font-size: 0.72rem;
}

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; gap: var(--s4); }
  .filter-toggle { display: inline-flex; align-items: center; }
  /* On a phone the filters slide in over the results rather than pushing
     them below the fold. */
  .filters {
    display: none; position: fixed; z-index: 60; inset: 0 auto 0 0; top: 0;
    width: min(360px, 88vw); max-height: none; border: 0; border-radius: 0;
    box-shadow: var(--shadow);
    /* align-self also sizes a fixed box; start would end it where its content does. */
    align-self: stretch;
  }
  .filters-body > :first-child { border-top: 0; }
  .filters.open { display: flex; }
  .backdrop { display: block; position: fixed; inset: 0; z-index: 59; background: rgba(12, 27, 42, 0.4); }
  .filters-head { border-bottom: 1px solid var(--border); }
  .close-btn { display: grid; place-items: center; }
  .filters-foot { display: block; padding: var(--s3) var(--s4); border-top: 1px solid var(--border); }
  .show-btn { width: 100%; justify-content: center; }
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
