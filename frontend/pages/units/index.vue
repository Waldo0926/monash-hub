<script setup lang="ts">
/**
 * Unit search. The point is fewer steps than the Handbook itself: type a code
 * or a word, narrow by campus, teaching period or whether an exam is listed.
 */
const route = useRoute()
const router = useRouter()

const query = ref((route.query.q as string) || '')
const filters = reactive({
  campus: (route.query.campus as string) || '',
  teaching_period: (route.query.teaching_period as string) || '',
  level: (route.query.level as string) || '',
  has_exam: (route.query.has_exam as string) || '',
  sort: (route.query.sort as string) || 'relevance'
})
const drawerOpen = ref(false)

const { data: facets } = await useApiFetch<any>('/v1/units/filters')

const requestPath = computed(() => {
  const params = new URLSearchParams()
  if (query.value) params.set('q', query.value)
  for (const [key, value] of Object.entries(filters)) if (value) params.set(key, String(value))
  params.set('limit', '30')
  return `/v1/units?${params.toString()}`
})

const { data, pending, error, refresh } = await useApiFetch<any>(() => requestPath.value, {
  watch: [requestPath]
})

function syncUrl() {
  const q: Record<string, string> = {}
  if (query.value) q.q = query.value
  for (const [key, value] of Object.entries(filters)) if (value && value !== 'relevance') q[key] = String(value)
  router.replace({ query: q })
}
watch([query, filters], syncUrl, { deep: true })

function reset() {
  filters.campus = ''
  filters.teaching_period = ''
  filters.level = ''
  filters.has_exam = ''
}

useSeoMeta({
  title: 'Unit search — Monash Hub',
  description: 'Search Monash Handbook units by code, title, campus, teaching period and assessment.'
})
</script>

<template>
  <div class="container">
    <h1>Unit search</h1>
    <p class="muted">
      {{ data?.academic_year }} Handbook data. Every result links back to the Handbook page it
      came from.
    </p>

    <SearchInput v-model="query" placeholder="FIT2102, programming, databases…" @submit="v => (query = v)" />

    <button class="btn btn--ghost btn--small filter-toggle" @click="drawerOpen = !drawerOpen">
      Filters{{ drawerOpen ? ' ▲' : ' ▼' }}
    </button>

    <div class="layout">
      <aside class="filters" :class="{ open: drawerOpen }">
        <h2 class="small">Filters</h2>

        <label class="filter">
          <span class="tiny muted">Campus</span>
          <select v-model="filters.campus" class="field">
            <option value="">Any campus</option>
            <option v-for="campus in facets?.campuses || []" :key="campus" :value="campus">{{ campus }}</option>
          </select>
        </label>

        <label class="filter">
          <span class="tiny muted">Teaching period</span>
          <select v-model="filters.teaching_period" class="field">
            <option value="">Any period</option>
            <option v-for="period in facets?.teaching_periods || []" :key="period" :value="period">
              {{ period }}
            </option>
          </select>
        </label>

        <label class="filter">
          <span class="tiny muted">Level</span>
          <select v-model="filters.level" class="field">
            <option value="">Any level</option>
            <option v-for="level in facets?.levels || []" :key="level" :value="level">{{ level }}</option>
          </select>
        </label>

        <label class="filter">
          <span class="tiny muted">Examination</span>
          <select v-model="filters.has_exam" class="field">
            <option value="">Any</option>
            <option value="true">Handbook lists an exam</option>
            <option value="false">No exam listed</option>
          </select>
        </label>

        <label class="filter">
          <span class="tiny muted">Sort</span>
          <select v-model="filters.sort" class="field">
            <option value="relevance">Relevance</option>
            <option value="code">Unit code</option>
            <option value="title">Title</option>
          </select>
        </label>

        <button class="btn btn--ghost btn--small" @click="reset">Clear filters</button>
        <p class="tiny muted note">
          “No exam listed” means the Handbook publishes no examination among the assessment items -
          not a guarantee that none exists.
        </p>
      </aside>

      <div class="results">
        <ErrorState v-if="error" :error="error" :on-retry="refresh" />
        <Skeleton v-else-if="pending" :lines="8" />
        <template v-else>
          <p class="tiny muted count">{{ data.total }} unit{{ data.total === 1 ? '' : 's' }}</p>
          <div v-if="data.results.length" class="grid">
            <UnitCard v-for="unit in data.results" :key="unit.unit_code" :unit="unit" />
          </div>
          <EmptyState
            v-else
            title="No unit matched that"
            hint="Check the unit code spelling, clear a filter, or search official guides and the community instead."
          >
            <NuxtLink :to="`/search?q=${encodeURIComponent(query)}`" class="btn btn--ghost">Search everything</NuxtLink>
            <NuxtLink to="/community" class="btn">Ask the community</NuxtLink>
          </EmptyState>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
h1 { margin-bottom: var(--s2); }
.layout { display: grid; grid-template-columns: 260px 1fr; gap: var(--s6); margin-top: var(--s5); }
.filters { display: grid; gap: var(--s4); align-content: start; }
.filter { display: grid; gap: var(--s1); }
.note { margin: 0; }
.results { min-width: 0; }
.count { margin-bottom: var(--s3); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
.filter-toggle { display: none; margin-top: var(--s3); }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .filter-toggle { display: inline-flex; }
  /* On a phone the filters collapse rather than pushing results below the fold. */
  .filters { display: none; }
  .filters.open { display: grid; }
}
</style>
