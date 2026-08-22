<script setup lang="ts">
/**
 * Home answers three questions above the fold and nothing else: what can this
 * do for me, where do I search, and what if I find nothing. No architecture
 * diagrams, no row counts.
 */
const config = useRuntimeConfig()
const query = ref('')

const { data: units } = await useApiFetch<any>('/v1/units?limit=6&sort=code')
const { data: guides } = await useApiFetch<any>('/v1/guides?limit=6')
const { data: posts } = await useApiFetch<any>('/v1/community/posts?limit=4')

const trending = ['FIT2102', 'Special consideration', 'WAM', 'Census dates', 'Student visa']

function search(value: string) {
  if (value) navigateTo({ path: '/search', query: { q: value } })
}

useSeoMeta({
  title: 'Monash Hub — Handbook, official guides and student community',
  description:
    'Search 2026 Monash Handbook units, official Monash policy pages and a public student ' +
    'community in one place. Independent student platform.',
  ogTitle: 'Monash Hub',
  ogDescription: 'Everything Monash, in one place.',
  ogUrl: config.public.siteUrl
})
useHead({ link: [{ rel: 'canonical', href: config.public.siteUrl }] })
</script>

<template>
  <div class="container">
    <section class="hero">
      <h1>Everything Monash, in one place.</h1>
      <p class="lead">
        Unit data from the 2026 Handbook, the official Monash pages students actually need, and a
        public place to ask everything the official pages do not cover.
      </p>
      <SearchInput v-model="query" big autofocus @submit="search" />
      <p class="trending tiny muted">
        Trending:
        <button v-for="term in trending" :key="term" class="term" @click="search(term)">
          {{ term }}
        </button>
      </p>
    </section>

    <section class="entries">
      <NuxtLink to="/units" class="entry card">
        <SourceBadge kind="handbook" />
        <h2>Units</h2>
        <p class="small muted">查课程 — assessment, requisites, offerings, workload</p>
      </NuxtLink>
      <NuxtLink to="/guides" class="entry card">
        <SourceBadge kind="official" />
        <h2>Official guides</h2>
        <p class="small muted">查政策 — special consideration, WAM, visas, census dates</p>
      </NuxtLink>
      <NuxtLink to="/community" class="entry card">
        <SourceBadge kind="community" />
        <h2>Community</h2>
        <p class="small muted">提问 / 经验分享 — public, searchable, no group chat required</p>
      </NuxtLink>
    </section>

    <section class="columns">
      <div>
        <div class="section-head">
          <h2>Units in the index</h2>
          <NuxtLink to="/units" class="small">All units →</NuxtLink>
        </div>
        <div class="grid">
          <UnitCard v-for="unit in units?.results || []" :key="unit.unit_code" :unit="unit" />
        </div>
        <EmptyState
          v-if="!units?.results?.length"
          title="No units indexed yet"
          hint="The Handbook crawl has not run on this environment."
        />
      </div>

      <div>
        <div class="section-head">
          <h2>Official guides</h2>
          <NuxtLink to="/guides" class="small">All guides →</NuxtLink>
        </div>
        <div class="grid">
          <GuideCard v-for="page in guides?.results?.slice(0, 4) || []" :key="page.slug" :page="page" />
        </div>
      </div>
    </section>

    <section v-if="posts?.results?.length" class="latest">
      <div class="section-head">
        <h2>Latest community discussions</h2>
        <NuxtLink to="/community" class="small">All discussions →</NuxtLink>
      </div>
      <div class="grid">
        <PostCard v-for="post in posts.results" :key="post.id" :post="post" />
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero { max-width: 760px; margin: 0 auto var(--s7); text-align: center; }
.lead { color: var(--muted); font-size: 1.05rem; }
.trending { margin-top: var(--s3); }
.term {
  border: 0;
  background: none;
  padding: 2px 6px;
  color: var(--blue-700);
  font: inherit;
  font-size: 0.8125rem;
  cursor: pointer;
}
.term:hover { text-decoration: underline; }

.entries { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--s4); margin-bottom: var(--s7); }
.entry { padding: var(--s5); color: inherit; }
.entry:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.entry h2 { margin: var(--s3) 0 var(--s2); font-size: 1.1rem; }
.entry p { margin: 0; }

.columns { display: grid; grid-template-columns: 1.4fr 1fr; gap: var(--s6); margin-bottom: var(--s7); }
.section-head { display: flex; align-items: baseline; justify-content: space-between; gap: var(--s3); }
.grid { display: grid; gap: var(--s3); }
.columns .grid { grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); }
.latest .grid { grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }

@media (max-width: 900px) {
  .entries { grid-template-columns: 1fr; }
  .columns { grid-template-columns: 1fr; }
}
</style>
