<script setup lang="ts">
/**
 * Says which campus a guide page was written for.
 *
 * Monash publishes a student site per location and on the things that matter
 * most they do not agree. A student pass in Malaysia is issued by the
 * Immigration Department through EMGS and has nothing to do with the Australian
 * subclass 500 visa; health cover there is not OSHC; and the work rights the
 * Australian pages describe do not carry over. Showing a Monash Malaysia
 * student an Australian page without saying so is not a translation problem -
 * it is telling them the wrong country's rules.
 *
 * So the notice states where the page came from, which is a fact, rather than
 * where it applies, which would be a judgement this platform is not entitled to
 * make on the university's behalf.
 */
const props = defineProps<{ appliesTo?: string | null; compact?: boolean }>()
const { $t } = useNuxtApp()

const known = ['australia', 'malaysia', 'all']
const scope = computed(() =>
  known.includes(props.appliesTo || '') ? (props.appliesTo as string) : null
)
</script>

<template>
  <span v-if="scope && compact" class="chip" :class="`chip--${scope}`">
    {{ $t(`campus.${scope}.label`) }}
  </span>
  <aside
    v-else-if="scope"
    class="notice"
    :class="`notice--${scope}`"
    role="note"
  >
    <p class="label">{{ $t(`campus.${scope}.label`) }}</p>
    <p class="small">{{ $t(`campus.${scope}.body`) }}</p>
  </aside>
</template>

<style scoped>
.chip {
  display: inline-block;
  padding: 2px var(--s2);
  border-radius: var(--radius-pill);
  font-size: 0.72rem;
  font-weight: 600;
  white-space: nowrap;
}
.chip--australia { background: #fdf0e3; color: #8a4b08; }
.chip--malaysia { background: #e6f4ec; color: #10633a; }
.chip--all { background: #eaeef8; color: #2a3f74; }

.notice {
  border: 1px solid var(--border);
  border-left-width: 4px;
  border-radius: var(--radius-sm);
  padding: var(--s3) var(--s4);
  margin-bottom: var(--s4);
}
.notice--australia { border-left-color: #d98324; background: #fdf7f0; }
.notice--malaysia { border-left-color: #1c8b55; background: #f2fbf6; }
.notice--all { border-left-color: var(--blue); background: var(--surface-muted, #f5f7fb); }
.label { margin: 0 0 var(--s1); font-weight: 700; font-size: 0.85rem; }
.small { margin: 0; }
</style>
