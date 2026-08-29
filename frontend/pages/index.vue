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
const sectionItems = useSectionNavigation()
const secondaryItems = computed(() => sectionItems.value.filter(item =>
  !['/units', '/guides', '/community'].includes(item.to)
))

const { data: units } = await useLocalisedApiFetch<any>('/v1/units?limit=8&sort=code')
const { data: guides } = await useLocalisedApiFetch<any>('/v1/guides?limit=8')
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

    <section class="quick-section" aria-labelledby="quick-section-title">
      <h2 id="quick-section-title">{{ $t('home.moreTools') }}</h2>
      <div class="quick-grid">
        <NuxtLink
          v-for="item in secondaryItems"
          :key="item.to"
          :to="item.to"
          class="quick-link"
        >
          <span class="quick-icon" aria-hidden="true">{{ item.icon }}</span>
          <span>{{ item.label }}</span>
          <span class="quick-arrow" aria-hidden="true">›</span>
        </NuxtLink>
      </div>
    </section>

    <section class="block">
      <div class="section-head">
        <h2>{{ $t('home.unitsInIndex') }}</h2>
        <NuxtLink to="/units" class="small">{{ $t('home.allUnits') }}</NuxtLink>
      </div>
      <div v-if="units?.results?.length" class="grid">
        <UnitCard v-for="unit in units.results" :key="unit.unit_code" :unit="unit" />
      </div>
      <EmptyState v-else :title="$t('home.noUnits')" :hint="$t('home.noUnitsHint')" />
    </section>

    <section class="block">
      <div class="section-head">
        <h2>{{ $t('home.officialGuides') }}</h2>
        <NuxtLink to="/guides" class="small">{{ $t('home.allGuides') }}</NuxtLink>
      </div>
      <div class="grid">
        <GuideCard v-for="page in guides?.results || []" :key="page.slug" :page="page" />
      </div>
    </section>

    <!-- Always rendered, empty or not. An empty forum that says nothing looks
         broken; an empty forum that asks for the first question is an invitation. -->
    <section class="block">
      <div class="section-head">
        <h2>{{ $t('home.latestDiscussions') }}</h2>
        <NuxtLink to="/community" class="small">{{ $t('home.allDiscussions') }}</NuxtLink>
      </div>
      <div v-if="posts?.results?.length" class="grid">
        <PostCard v-for="post in posts.results" :key="post.id" :post="post" />
      </div>
      <EmptyState
        v-else
        :title="$t('home.communityEmpty')"
        :hint="$t('home.communityEmptyHint')"
      >
        <NuxtLink to="/community" class="btn">{{ $t('community.ask') }}</NuxtLink>
      </EmptyState>
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

.quick-section { margin-bottom: var(--s6); }
.quick-section h2 { margin-bottom: var(--s3); font-size: 1.25rem; }
.quick-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: var(--s3);
}
.quick-link {
  display: flex;
  align-items: center;
  gap: var(--s3);
  min-width: 0;
  min-height: 64px;
  padding: var(--s3) var(--s4);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  box-shadow: var(--shadow-sm);
  color: var(--text);
  font-weight: 650;
}
.quick-link:hover {
  border-color: var(--border-strong);
  box-shadow: var(--shadow);
  text-decoration: none;
}
.quick-icon {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  flex: none;
  border-radius: var(--radius-sm);
  background: var(--blue-50);
  color: var(--blue-700);
  font-weight: 800;
}
.quick-arrow { margin-left: auto; color: var(--muted); font-size: 1.35rem; }

.entries { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: var(--s4); margin-bottom: var(--s7); }
.entry { padding: var(--s5); color: inherit; }
.entry:hover { text-decoration: none; border-color: var(--border-strong); box-shadow: var(--shadow); }
.entry h2 { margin: var(--s3) 0 var(--s2); font-size: 1.1rem; }
.entry p { margin: 0; }

/* Stacked full-width sections rather than two columns side by side.
   Unit cards and guide cards are different heights, so a two-column split left
   whichever ran out first as a large empty rectangle - the taller column set the
   height and the shorter one just stopped. */
.block { margin-bottom: var(--s7); }
.section-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: var(--s3);
  margin-bottom: var(--s3);
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: var(--s3);
  /* Cards in a row share a height, so the row reads as a row. */
  align-items: stretch;
}

@media (max-width: 900px) {
  .entries { grid-template-columns: 1fr; }
  .quick-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .quick-link { padding: var(--s3); }
}

@media (max-width: 360px) {
  .quick-link { gap: var(--s2); font-size: 0.9rem; }
  .quick-arrow { display: none; }
}
</style>
