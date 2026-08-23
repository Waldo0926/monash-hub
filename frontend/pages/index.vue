<script setup lang="ts">
/**
 * Home answers three questions above the fold and nothing else: what can this
 * do for me, where do I search, and what if I find nothing. No architecture
 * diagrams, no row counts.
 *
 * For a signed-in reader it also carries the notification list, because the
 * point of being told your question was answered is that you see it without
 * going looking for it.
 */
const config = useRuntimeConfig()
const { $t } = useNuxtApp()
const query = ref('')

const { data: units } = await useApiFetch<any>('/v1/units?limit=6&sort=code')
const { data: guides } = await useApiFetch<any>('/v1/guides?limit=6')
const { data: posts } = await useApiFetch<any>('/v1/community/posts?limit=4')

const trending = ['FIT2102', 'Special consideration', 'WAM', 'Census dates', 'Student visa']

function search(value: string) {
  if (value) navigateTo({ path: '/search', query: { q: value } })
}

useSeoMeta({
  title: () => $t('home.title'),
  description: () => $t('home.metaDescription'),
  ogTitle: 'Monash Hub',
  ogDescription: () => $t('home.hero'),
  ogUrl: config.public.siteUrl
})
useHead({ link: [{ rel: 'canonical', href: config.public.siteUrl }] })
</script>

<template>
  <div class="container">
    <section class="hero">
      <h1>{{ $t('home.hero') }}</h1>
      <p class="lead">{{ $t('home.lead') }}</p>
      <SearchInput v-model="query" big autofocus @submit="search" />
      <p class="trending tiny muted">
        {{ $t('home.trending') }}:
        <button v-for="term in trending" :key="term" class="term" @click="search(term)">
          {{ term }}
        </button>
      </p>
    </section>

    <NotificationPanel class="notifications" />

    <section class="entries">
      <NuxtLink to="/units" class="entry card">
        <SourceBadge kind="handbook" />
        <h2>{{ $t('home.entryUnits') }}</h2>
        <p class="small muted">{{ $t('home.entryUnitsHint') }}</p>
      </NuxtLink>
      <NuxtLink to="/guides" class="entry card">
        <SourceBadge kind="official" />
        <h2>{{ $t('home.entryGuides') }}</h2>
        <p class="small muted">{{ $t('home.entryGuidesHint') }}</p>
      </NuxtLink>
      <NuxtLink to="/community" class="entry card">
        <SourceBadge kind="community" />
        <h2>{{ $t('home.entryCommunity') }}</h2>
        <p class="small muted">{{ $t('home.entryCommunityHint') }}</p>
      </NuxtLink>
    </section>

    <section class="columns">
      <div>
        <div class="section-head">
          <h2>{{ $t('home.unitsInIndex') }}</h2>
          <NuxtLink to="/units" class="small">{{ $t('home.allUnits') }}</NuxtLink>
        </div>
        <div class="grid">
          <UnitCard v-for="unit in units?.results || []" :key="unit.unit_code" :unit="unit" />
        </div>
        <EmptyState
          v-if="!units?.results?.length"
          :title="$t('home.noUnits')"
          :hint="$t('home.noUnitsHint')"
        />
      </div>

      <div>
        <div class="section-head">
          <h2>{{ $t('home.officialGuides') }}</h2>
          <NuxtLink to="/guides" class="small">{{ $t('home.allGuides') }}</NuxtLink>
        </div>
        <div class="grid">
          <GuideCard v-for="page in guides?.results?.slice(0, 4) || []" :key="page.slug" :page="page" />
        </div>
      </div>
    </section>

    <section v-if="posts?.results?.length" class="latest">
      <div class="section-head">
        <h2>{{ $t('home.latestDiscussions') }}</h2>
        <NuxtLink to="/community" class="small">{{ $t('home.allDiscussions') }}</NuxtLink>
      </div>
      <div class="grid">
        <PostCard v-for="post in posts.results" :key="post.id" :post="post" />
      </div>
    </section>
  </div>
</template>

<style scoped>
.hero { max-width: 760px; margin: 0 auto var(--s6); text-align: center; }
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

.notifications { margin-bottom: var(--s6); }

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
