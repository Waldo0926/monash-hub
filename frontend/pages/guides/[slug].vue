<script setup lang="ts">
/**
 * Guide detail. Shows the heading outline and the extracted page, and puts the
 * link to the original in front of the reader rather than at the bottom - for
 * anything that matters, the official page is still the authority.
 *
 * The body used to be one long string in a scrolling box. It is now the block
 * list from the crawler, rendered as real headings, lists and tables by
 * PageBlocks - a scroll box inside a page is a place text goes to be ignored,
 * and the string in it had lost every table on the way here anyway.
 */
const route = useRoute()
const config = useRuntimeConfig()
const { $t } = useNuxtApp()
const slug = computed(() => String(route.params.slug))

const { data: guide, error } = await useLocalisedApiFetch<any>(() => `/v1/guides/${slug.value}`)

useSeoMeta({
  title: () => (guide.value ? `${guide.value.title} — Monash Hub` : 'Guide — Monash Hub'),
  description: () => guide.value?.summary || ''
})
useHead(() => ({ link: [{ rel: 'canonical', href: `${config.public.siteUrl}/guides/${slug.value}` }] }))
</script>

<template>
  <div class="container">
    <ErrorState v-if="error" :error="error" />

    <div v-else-if="guide" class="layout">
      <article class="content">
        <header class="card section">
          <div class="head-top">
            <div>
              <p class="tiny muted">
                <NuxtLink to="/guides">{{ $t('guides.title') }}</NuxtLink> /
                {{ $t(`category.${guide.category}`) }}
              </p>
              <h1>{{ guide.title }}</h1>
            </div>
            <SourceBadge kind="official" />
          </div>
          <p class="muted">{{ guide.source_name }}</p>
          <LastChecked :value="guide.last_checked" />
          <p class="mt">
            <a :href="guide.url" rel="noopener external" target="_blank" class="btn">
              {{ $t('guides.viewOfficial') }}
            </a>
          </p>
        </header>

        <section v-if="guide.headings?.length" class="card section">
          <h2>{{ $t('guides.covers') }}</h2>
          <ul class="outline">
            <li v-for="(heading, i) in guide.headings" :key="i" :class="`lvl-${heading.level}`">
              <a v-if="heading.id" :href="`#${heading.id}`">{{ heading.text }}</a>
              <template v-else>{{ heading.text }}</template>
            </li>
          </ul>
        </section>

        <section class="card section">
          <h2>{{ $t('guides.pageText') }}</h2>
          <p class="tiny muted">{{ $t('guides.pageTextNote') }}</p>
          <TranslationNotice
            v-if="guide.translation"
            :translation="guide.translation"
            :source-url="guide.url"
            class="mb"
          />
          <PageBlocks :blocks="guide.blocks" :fallback="guide.clean_text" />
        </section>
      </article>

      <aside class="side stack">
        <div v-if="guide.related_faq?.length" class="card section">
          <h2 class="small">{{ $t('guides.relatedQuestions') }}</h2>
          <div v-for="faq in guide.related_faq" :key="faq.slug" class="faq">
            <h3>{{ faq.question }}</h3>
            <p class="small">{{ faq.answer }}</p>
          </div>
        </div>

        <div class="card section">
          <div class="section-head">
            <h2 class="small">{{ $t('nav.community') }}</h2>
            <SourceBadge kind="community" />
          </div>
          <ul v-if="guide.related_community?.length" class="links">
            <li v-for="post in guide.related_community" :key="post.id">
              <NuxtLink :to="`/community/post/${post.id}`">{{ post.title }}</NuxtLink>
              <span class="tiny muted"> · {{ post.answer_count }} answers</span>
            </li>
          </ul>
          <p v-else class="small muted">{{ $t('guides.communityEmpty') }}</p>
          <NuxtLink to="/community" class="btn btn--ghost btn--small">
            {{ $t('units.askCommunity') }}
          </NuxtLink>
        </div>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.layout { display: grid; grid-template-columns: 1fr 300px; gap: var(--s5); align-items: start; }
/* See units/[code].vue: without this a wide table widens its own grid column
   and the page scrolls sideways instead of the table. */
.layout > * { min-width: 0; }
.content { display: grid; gap: var(--s4); min-width: 0; }
.section { padding: var(--s5); }
.head-top { display: flex; align-items: flex-start; justify-content: space-between; gap: var(--s4); }
.mt { margin-top: var(--s4); }
.mb { margin-bottom: var(--s5); }
.outline { margin: 0; padding-left: var(--s5); }
.outline .lvl-3 { margin-left: var(--s4); color: var(--muted); }
.side { position: sticky; top: calc(var(--header-h) + var(--s4)); }
.faq + .faq { margin-top: var(--s4); }
.faq h3 { font-size: 0.95rem; }
.links { margin: 0 0 var(--s4); padding-left: var(--s5); }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: var(--s3); }

@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .side { position: static; }
}
</style>
