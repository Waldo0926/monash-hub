<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()
const query = ref((route.query.q as string) || '')
const category = ref((route.query.category as string) || '')
// Monash Australia and Monash Malaysia publish different rules for the same
// things - fees, visas and student passes, exams - so a reader can keep to the
// pages for their own campus. "all" pages appear under both.
const CAMPUSES = ['australia', 'malaysia'] as const
const initialCampus = route.query.campus as string
const campus = ref(CAMPUSES.includes(initialCampus as any) ? initialCampus : '')
const PAGE = 60
const limit = ref(PAGE)

const path = computed(() => {
  const params = new URLSearchParams()
  if (query.value) params.set('q', query.value)
  if (category.value) params.set('category', category.value)
  if (campus.value) params.set('campus', campus.value)
  params.set('limit', String(limit.value))
  return `/v1/guides?${params.toString()}`
})
const { data, pending, error, refresh } = await useLocalisedApiFetch<any>(
  () => path.value,
  { watch: [path] }
)

watch([query, category, campus], () => {
  limit.value = PAGE
  const q: Record<string, string> = {}
  if (query.value) q.q = query.value
  if (category.value) q.category = category.value
  if (campus.value) q.campus = campus.value
  router.replace({ query: q })
})
// Keep what is on screen while the longer list loads, so "show more" does not
// flash the skeleton over the cards the reader was looking at.
const shown = ref<any>(null)
watch(data, v => { if (v) shown.value = v }, { immediate: true })

useSeoMeta({
  title: () => $t('guides.metaTitle'),
  description:
    'Indexed official Monash pages: special consideration, WAM, GPA, visas, census dates, fees and graduation.'
})
</script>

<template>
  <div class="container">
    <h1>{{ $t('guides.title') }}</h1>
    <p class="muted">{{ $t('guides.lead') }}</p>

    <SearchInput
      v-model="query"
      :placeholder="$t('guides.searchPlaceholder')"
      @submit="v => (query = v)"
    />

    <div class="cats campus" role="group" :aria-label="$t('campus.filter')">
      <button class="cat" :class="{ active: !campus }" @click="campus = ''">
        {{ $t('campus.any') }}
      </button>
      <button
        v-for="c in CAMPUSES"
        :key="c"
        class="cat"
        :class="{ active: campus === c }"
        @click="campus = c"
      >
        {{ $t(`campus.${c}.label`) }}
      </button>
    </div>

    <div class="cats">
      <button class="cat" :class="{ active: !category }" @click="category = ''">
        {{ $t('guides.all') }}
      </button>
      <button
        v-for="cat in shown?.categories || []"
        :key="cat.key"
        class="cat"
        :class="{ active: category === cat.key }"
        @click="category = cat.key"
      >
        {{ $t(`category.${cat.key}`) }} ({{ cat.count }})
      </button>
    </div>

    <ErrorState v-if="error" :error="error" :on-retry="refresh" />
    <Skeleton v-else-if="pending && !shown" :lines="8" />
    <template v-else-if="shown">
      <div v-if="shown.results.length" class="grid">
        <GuideCard v-for="page in shown.results" :key="page.slug" :page="page" />
      </div>
      <div v-if="shown.results.length < shown.total" class="more">
        <button class="btn" :disabled="pending" @click="limit = Math.min(limit + PAGE, 500)">
          {{ $t('guides.more', { shown: shown.results.length, total: shown.total }) }}
        </button>
      </div>
      <EmptyState v-else :title="$t('guides.empty')" :hint="$t('guides.emptyHint')">
        <NuxtLink to="/community" class="btn">{{ $t('units.askCommunity') }}</NuxtLink>
      </EmptyState>
    </template>
  </div>
</template>

<style scoped>
h1 { margin-bottom: var(--s2); }
.cats { display: flex; flex-wrap: wrap; gap: var(--s2); margin: var(--s4) 0 var(--s5); }
.cat {
  padding: 6px 14px;
  min-height: 36px;
  border: 1px solid var(--border-strong);
  border-radius: var(--radius-pill);
  background: var(--surface);
  font: inherit;
  font-size: 0.85rem;
  cursor: pointer;
}
.cat.active { background: var(--navy); border-color: var(--navy); color: var(--text-inverse); }
.campus { margin-bottom: 0; }
.more { display: flex; justify-content: center; margin-top: var(--s5); }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
</style>
