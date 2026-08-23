<script setup lang="ts">
const route = useRoute()
const router = useRouter()
const { $t } = useNuxtApp()
const query = ref((route.query.q as string) || '')
const category = ref((route.query.category as string) || '')

const path = computed(() => {
  const params = new URLSearchParams()
  if (query.value) params.set('q', query.value)
  if (category.value) params.set('category', category.value)
  return `/v1/guides?${params.toString()}`
})
const { data, pending, error, refresh } = await useApiFetch<any>(() => path.value, { watch: [path] })

watch([query, category], () => {
  const q: Record<string, string> = {}
  if (query.value) q.q = query.value
  if (category.value) q.category = category.value
  router.replace({ query: q })
})

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

    <div class="cats">
      <button class="cat" :class="{ active: !category }" @click="category = ''">
        {{ $t('guides.all') }}
      </button>
      <button
        v-for="cat in data?.categories || []"
        :key="cat.key"
        class="cat"
        :class="{ active: category === cat.key }"
        @click="category = cat.key"
      >
        {{ $t(`category.${cat.key}`) }} ({{ cat.count }})
      </button>
    </div>

    <ErrorState v-if="error" :error="error" :on-retry="refresh" />
    <Skeleton v-else-if="pending" :lines="8" />
    <template v-else>
      <div v-if="data.results.length" class="grid">
        <GuideCard v-for="page in data.results" :key="page.slug" :page="page" />
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
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--s3); }
</style>
