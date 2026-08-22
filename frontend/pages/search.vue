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
const query = ref((route.query.q as string) || '')

const { data, pending, error, refresh } = await useApiFetch<any>(
  () => `/v1/search?q=${encodeURIComponent((useRoute().query.q as string) || '')}`,
  { watch: [() => route.query.q] }
)

// The zero-AI router runs alongside search, so a question gets an answer and a
// result list from one submission.
const answer = ref<any>(null)
async function loadAnswer(q: string) {
  answer.value = q ? await apiFetch<any>('/v1/ask', { method: 'POST', body: { query: q } }).catch(() => null) : null
}
watch(() => route.query.q, q => { query.value = (q as string) || ''; loadAnswer(query.value) }, { immediate: true })

function search(value: string) {
  navigateTo({ path: '/search', query: value ? { q: value } : {} })
}

const hasResults = computed(() => (data.value?.groups || []).some((g: any) => g.results?.length))

useSeoMeta({ title: () => (query.value ? `${query.value} — Monash Hub search` : 'Search — Monash Hub'), robots: 'noindex' })
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
        <EmptyState
          title="Nothing matched that"
          hint="Check the spelling of the unit code, try fewer words, or ask the community."
        >
          <NuxtLink to="/community" class="btn">Ask the community</NuxtLink>
        </EmptyState>
      </div>

      <div v-else-if="query" class="groups mt">
        <section v-for="group in data.groups" :key="group.kind" class="group">
          <div v-if="group.results.length" class="section-head">
            <h2>
              {{ group.label }}
              <SourceBadge :kind="group.badge" />
            </h2>
            <span class="tiny muted">{{ group.total }} result{{ group.total === 1 ? '' : 's' }}</span>
          </div>

          <div v-if="group.kind === 'handbook' && group.results.length" class="grid">
            <UnitCard v-for="unit in group.results" :key="unit.unit_code" :unit="unit" />
          </div>
          <div v-else-if="group.kind === 'official' && group.results.length" class="grid">
            <GuideCard v-for="page in group.results" :key="page.slug" :page="page" />
          </div>
          <div v-else-if="group.kind === 'faq' && group.results.length" class="grid">
            <article v-for="faq in group.results" :key="faq.slug" class="faq card">
              <SourceBadge kind="official" />
              <h3>{{ faq.question }}</h3>
              <p class="small">{{ faq.answer }}</p>
              <a v-if="faq.official_url" :href="faq.official_url" rel="noopener external" target="_blank" class="small">
                Open the official page ↗
              </a>
              <LastChecked :value="faq.last_checked" />
            </article>
          </div>
          <div v-else-if="group.kind === 'community' && group.results.length" class="grid">
            <PostCard v-for="post in group.results" :key="post.id" :post="post" />
          </div>
        </section>
      </div>

      <EmptyState
        v-else
        class="mt"
        title="Search Monash Hub"
        hint="Try a unit code like FIT2102, a policy phrase like special consideration, or a question."
      />
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
.faq h3 { margin: var(--s2) 0; font-size: 1rem; }
</style>
