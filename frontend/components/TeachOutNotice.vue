<script setup lang="ts">
/**
 * What a faculty says about a unit that is closing, renamed or changing, and
 * what replaces it - word for word, with the page it came from.
 *
 * The wording is the faculty's and stays in English: "Replace with FIT3235 from
 * 2028" is an instruction, and a paraphrase of an instruction is how a student
 * ends up in the wrong unit. The site adds only the frame around it: whose
 * notice it is, when it was last checked, and that the campus it applies to is
 * the reader's to confirm.
 */
defineProps<{
  entries: { change: string; course: string; plan: string }[]
  sources: Record<string, { title: string; url: string; last_checked: string | null }>
}>()
</script>

<template>
  <section class="teach card" aria-labelledby="teach-title">
    <h2 id="teach-title">{{ $t('teachOut.title') }}</h2>
    <ul class="entries">
      <li v-for="(entry, i) in entries" :key="i">
        <p class="change">{{ entry.change }}</p>
        <p v-if="entry.course" class="small muted">{{ entry.course }}</p>
        <p class="plan">{{ entry.plan }}</p>
      </li>
    </ul>
    <p class="tiny muted">
      {{ $t('teachOut.source') }}
      <template v-for="(source, slug, n) in sources" :key="slug">
        <template v-if="n">, </template>
        <a :href="source.url" rel="noopener external" target="_blank">{{ source.title }}</a>
        <template v-if="source.last_checked"> · <LastChecked :value="source.last_checked" /></template>
      </template>
    </p>
    <p class="tiny muted">{{ $t('teachOut.caution') }}</p>
  </section>
</template>

<style scoped>
.teach { margin-bottom: var(--s5); padding: var(--s4) var(--s5); border-color: var(--warning); }
.teach h2 { margin: 0 0 var(--s3); font-size: 1.05rem; }
.entries { margin: 0 0 var(--s3); padding: 0; list-style: none; display: grid; gap: var(--s3); }
.entries li { padding-top: var(--s3); border-top: 1px solid var(--border); }
.entries li:first-child { padding-top: 0; border-top: 0; }
.entries p { margin: 0; }
.change { font-weight: 600; color: var(--warning); }
.plan { margin-top: var(--s1); white-space: pre-line; }
.teach .tiny { margin: 0 0 var(--s1); }
</style>
