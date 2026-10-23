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
 * Malaysia and the Australian campuses each publish their own list and they
 * differ, so the reader sees the one for their campus first. The other one is
 * a click away, for someone planning an exchange or checking a friend's plan.
 */
import { teachOutFor, teachOutRegion, type TeachOutRegion } from '~/utils/teachOut'

type Entry = { change: string; course: string; plan: string; source?: string; applies_to?: string | null }
type Source = { title: string; url: string; last_checked: string | null; applies_to?: string | null }

const props = defineProps<{
  entries: Entry[]
  sources: Record<string, Source>
  campus: string
}>()

const home = computed(() => teachOutRegion(props.campus))
const away = computed<TeachOutRegion>(() => (home.value === 'malaysia' ? 'australia' : 'malaysia'))
const homeEntries = computed(() => teachOutFor(props.entries, home.value))
const awayEntries = computed(() => teachOutFor(props.entries, away.value))

const showing = ref<TeachOutRegion | null>(null)
watch(home, () => { showing.value = null })
const region = computed<TeachOutRegion | null>(() => showing.value ?? (homeEntries.value.length ? home.value : null))
const shown = computed(() => (region.value ? teachOutFor(props.entries, region.value) : []))
const shownSources = computed(() => {
  const slugs = new Set(shown.value.map(e => e.source))
  return Object.entries(props.sources).filter(([slug]) => slugs.has(slug))
})
const other = computed<TeachOutRegion | null>(() => {
  if (!region.value) return null
  const next = region.value === 'malaysia' ? 'australia' : 'malaysia'
  return teachOutFor(props.entries, next).length ? next : null
})
</script>

<template>
  <section class="teach card" aria-labelledby="teach-title">
    <h2 id="teach-title">
      {{ $t('teachOut.title') }}
      <span v-if="region" class="where">{{ $t(`teachOut.region.${region}`) }}</span>
    </h2>

    <template v-if="region">
      <ul class="entries">
        <li v-for="(entry, i) in shown" :key="i">
          <p class="change">{{ entry.change }}</p>
          <p v-if="entry.course" class="small muted">{{ entry.course }}</p>
          <p class="plan">{{ entry.plan }}</p>
        </li>
      </ul>
      <p class="tiny muted">
        {{ $t('teachOut.source') }}
        <template v-for="([slug, source], n) in shownSources" :key="slug">
          <template v-if="n">, </template>
          <a :href="source.url" rel="noopener external" target="_blank">{{ source.title }}</a>
          <template v-if="source.last_checked"> · <LastChecked :value="source.last_checked" /></template>
        </template>
      </p>
      <p class="tiny muted">{{ $t('teachOut.caution') }}</p>
      <button v-if="other" type="button" class="btn btn--ghost btn--small" @click="showing = other">
        {{ other === home ? $t('teachOut.back', { campus: $t(`teachOut.region.${other}`) }) : $t('teachOut.see', { campus: $t(`teachOut.region.${other}`) }) }}
      </button>
    </template>

    <template v-else>
      <p class="small">{{ $t('teachOut.onlyAway', { home: $t(`teachOut.region.${home}`), away: $t(`teachOut.region.${away}`) }) }}</p>
      <button type="button" class="btn btn--ghost btn--small" @click="showing = away">
        {{ $t('teachOut.see', { campus: $t(`teachOut.region.${away}`) }) }}
      </button>
    </template>
  </section>
</template>

<style scoped>
.teach { margin-bottom: var(--s5); padding: var(--s4) var(--s5); border-color: var(--warning); }
.teach h2 { margin: 0 0 var(--s3); font-size: 1.05rem; display: flex; flex-wrap: wrap; align-items: baseline; gap: var(--s2); }
.where { font-size: 0.85rem; font-weight: 500; color: var(--warning); }
.entries { margin: 0 0 var(--s3); padding: 0; list-style: none; display: grid; gap: var(--s3); }
.entries li { padding-top: var(--s3); border-top: 1px solid var(--border); }
.entries li:first-child { padding-top: 0; border-top: 0; }
.entries p { margin: 0; }
.change { font-weight: 600; color: var(--warning); }
.plan { margin-top: var(--s1); white-space: pre-line; }
.teach .tiny { margin: 0 0 var(--s1); }
.teach .small { margin: 0 0 var(--s3); }
.teach .btn { margin-top: var(--s2); }
</style>
