<script setup lang="ts">
/**
 * Unified search.
 *
 * Results stay grouped by source instead of being merged into one ranked list:
 * merging them would put a student's opinion next to a Handbook field with no
 * visible difference, which is precisely the failure this product exists to
 * avoid.
 */
const route = useRoute()
const { $t } = useNuxtApp()
const query = ref((route.query.q as string) || '')

const { data, pending, error, refresh } = await useLocalisedApiFetch<any>(
  () => `/v1/search?q=${encodeURIComponent((route.query.q as string) || '')}`,
  { watch: [() => route.query.q] }
)

// The zero-AI router runs alongside search, so one submission produces both an
// answer and a result list.
//
// This resolves during SSR rather than on mount. Filling it in afterwards left
// the server and client markup disagreeing, and the hydration mismatch that
// followed threw out the result groups underneath it.
const { data: answer } = await useAsyncData<any>(
  'ask-answer',
  () => {
    const q = ((route.query.q as string) || '').trim()
    if (!q) return Promise.resolve(null)
    return $fetch<any>(apiUrl('/v1/ask'), { method: 'POST', body: { query: q } }).catch(() => null)
  },
  { watch: [() => route.query.q] }
)

watch(() => route.query.q, q => { query.value = (q as string) || '' }, { immediate: true })

function search(value: string) {
  navigateTo({ path: '/search', query: value ? { q: value } : {} })
}

const hasResults = computed(() => (data.value?.groups || []).some((g: any) => g.results?.length))

useSeoMeta({
  title: () => (query.value ? `${query.value} — Monash Hub` : $t('search.title')),
  robots: 'noindex'
})
</script>

<template>
  <div class="container">
    <SearchInput v-model="query" big @submit="search" />

    <ErrorState v-if="error" :error="error" :on-retry="refresh" class="mt" />

    <template v-else>
      <div v-if="answer && query" class="mt">
        <AnswerBlocks :answer="answer" />
      </div>

      <Skeleton v-if="pending" :lines="6" class="mt" />

      <div v-else-if="query && !hasResults" class="mt">
        <EmptyState :title="$t('search.nothing')" :hint="$t('search.nothingHint')">
          <NuxtLink to="/community" class="btn">{{ $t('units.askCommunity') }}</NuxtLink>
        </EmptyState>
      </div>

      <div v-else-if="query" class="groups mt">
        <section v-for="group in data.groups" :key="group.kind" class="group">
          <div v-if="group.results.length" class="section-head">
            <h2>
              {{ $t(`search.group${group.kind.charAt(0).toUpperCase()}${group.kind.slice(1)}`) }}
              <SourceBadge :kind="group.badge" />
            </h2>
            <span class="tiny muted">
              {{ group.total === 1 ? $t('search.resultsOne') : $t('search.results', { count: group.total }) }}
            </span>
          </div>

          <div v-if="group.kind === 'handbook' && group.results.length" class="grid">
            <UnitCard v-for="unit in group.results" :key="unit.unit_code" :unit="unit" />
          </div>
          <div v-else-if="group.kind === 'official' && group.results.length" class="grid">
            <GuideCard v-for="page in group.results" :key="page.slug" :page="page" />
          </div>
          <div v-else-if="group.kind === 'faq' && group.results.length" class="grid">
            <article v-for="faq in group.results" :key="faq.slug" class="faq card">
              <div class="faq-top">
                <SourceBadge kind="official" />
                <CampusNotice :applies-to="faq.applies_to" compact />
              </div>
              <h3>{{ faq.question }}</h3>
              <p class="small">{{ faq.answer }}</p>
              <a
                v-if="faq.official_url"
                :href="faq.official_url"
                rel="noopener external"
                target="_blank"
                class="small"
              >{{ $t('search.openOfficial') }}</a>
              <LastChecked :value="faq.last_checked" />
            </article>
          </div>
          <div v-else-if="group.kind === 'community' && group.results.length" class="grid">
            <PostCard v-for="post in group.results" :key="post.id" :post="post" />
          </div>
        </section>
      </div>

      <EmptyState v-else class="mt" :title="$t('search.title')" :hint="$t('search.hint')" />
    </template>
  </div>
</template>

<style scoped>
.mt { margin-top: var(--s5); }
.groups { display: grid; gap: var(--s6); }
.section-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s3); }
.section-head h2 { display: flex; align-items: center; gap: var(--s3); font-size: 1.1rem; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
.faq { padding: var(--s4); }
.faq-top { display: flex; align-items: center; gap: var(--s2); flex-wrap: wrap; }
.faq h3 { margin: var(--s2) 0; font-size: 1rem; }
</style>
