<script setup lang="ts">
/**
 * What a faculty says about a unit that is closing, renamed or changing, and
 * what replaces it - word for word, with the page it came from.
 *
 * The wording is the faculty's and stays in English: "Replace with FIT3235 from
 * 2028" is an instruction, and a paraphrase of an instruction is how a student
 * ends up in the wrong unit. The site adds only the frame around it: whose
 * notice it is, when it was last checked, and which campus it is for.
 *
 * Malaysia and the Australian campuses each publish their own list, and they
 * change units on different dates (FIT3161 is gone in Australia and runs to S2
 * 2027 in Malaysia). So both campuses are shown side by side, the reader's own
 * first, each with a link to its page. A campus whose list leaves the unit out
 * says so; it is never filled in with the other campus's row.
 */
import { teachOutFor, teachOutLabel, teachOutRegion, type TeachOutRegion } from '~/utils/teachOut'

type Entry = { change: string; course: string; plan: string; source?: string; applies_to?: string | null }
type Source = { title: string; url: string; last_checked: string | null; applies_to?: string | null }

const props = defineProps<{
  entries: Entry[]
  sources: Record<string, Source>
  /** Every campus's page, including those that do not list the unit. */
  pages?: Record<string, Source> | null
  campus: string
}>()

const { locale } = useLocale()

const home = computed(() => teachOutRegion(props.campus))

const regions = computed(() => {
  const pages = { ...props.sources, ...(props.pages ?? {}) }
  const order: TeachOutRegion[] = home.value === 'malaysia' ? ['malaysia', 'australia'] : ['australia', 'malaysia']
  return order
    .map((region) => {
      const entries = teachOutFor(props.entries, region)
      const slugs = new Set(entries.map(e => e.source))
      const listed = Object.entries(pages).filter(([slug]) => slugs.has(slug))
      // A campus with no row still gets its own page, so the student can check it.
      const own = listed.length ? listed : Object.entries(pages).filter(([, page]) => page.applies_to === region)
      return { region, entries, pages: own }
    })
    // Without that campus's page there is nothing to show or link to.
    .filter(r => r.entries.length || r.pages.length)
})

function chip(change: string): string | null {
  const label = teachOutLabel(change, locale.value)
  return label === change.replace(/\s+/g, ' ').trim() ? null : label
}
</script>

<template>
  <section class="teach card" aria-labelledby="teach-title">
    <h2 id="teach-title">{{ $t('teachOut.title') }}</h2>

    <div class="regions">
      <div v-for="r in regions" :key="r.region" class="region" :class="{ 'region--home': r.region === home }">
        <h3>{{ $t(`teachOut.region.${r.region}`) }}</h3>
        <ul v-if="r.entries.length" class="entries">
          <li v-for="(entry, i) in r.entries" :key="i">
            <p class="change">
              <span v-if="chip(entry.change)" class="chip">{{ chip(entry.change) }}</span>
              {{ entry.change }}
            </p>
            <p v-if="entry.course" class="small muted">{{ entry.course }}</p>
            <p class="plan">{{ entry.plan }}</p>
          </li>
        </ul>
        <p v-else class="small none">{{ $t('teachOut.none') }}</p>
        <p class="tiny muted">
          {{ $t('teachOut.source') }}
          <template v-for="([slug, source], n) in r.pages" :key="slug">
            <template v-if="n">, </template>
            <a :href="source.url" rel="noopener external" target="_blank">{{ source.title }}</a>
            <template v-if="source.last_checked"> · <LastChecked :value="source.last_checked" /></template>
          </template>
        </p>
      </div>
    </div>

    <p class="tiny muted caution">{{ $t('teachOut.caution') }}</p>
  </section>
</template>

<style scoped>
.teach { margin-bottom: var(--s5); padding: var(--s4) var(--s5); border-color: var(--warning); }
.teach h2 { margin: 0 0 var(--s3); font-size: 1.05rem; }
.regions { display: grid; grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr)); gap: var(--s4); margin-bottom: var(--s3); }
.region { min-width: 0; }
.region h3 { margin: 0 0 var(--s2); font-size: 0.9rem; font-weight: 600; color: var(--warning); }
.region:not(.region--home) h3 { color: var(--muted); }
.entries { margin: 0 0 var(--s2); padding: 0; list-style: none; display: grid; gap: var(--s3); }
.entries li { padding-top: var(--s3); border-top: 1px solid var(--border); }
.entries li:first-child { padding-top: 0; border-top: 0; }
.entries p { margin: 0; }
.change { font-weight: 600; }
.chip { display: inline-block; margin-right: var(--s1); padding: 0 var(--s2); border-radius: 999px; font-size: 0.8rem; font-weight: 600; color: var(--warning); border: 1px solid var(--warning); }
.plan { margin-top: var(--s1); white-space: pre-line; }
.none { margin: 0 0 var(--s2); }
.teach .tiny { margin: 0; overflow-wrap: anywhere; }
.caution { padding-top: var(--s2); border-top: 1px solid var(--border); }
</style>
