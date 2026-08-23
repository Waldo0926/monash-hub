<script setup lang="ts">
/**
 * Says, on screen, that what follows is a translation.
 *
 * This is not decoration and it is not a disclaimer bolted on afterwards. The
 * whole reason the platform is allowed to show Monash's words in Chinese is
 * that it never pretends Monash said them in Chinese: the notice is visible,
 * the original is one click away, and when the English has moved on since the
 * translation was written, the notice says so instead of letting a student act
 * on a paragraph that has quietly stopped being true.
 *
 * `stale` is the case worth caring about. Everything else here is labelling.
 */
const props = defineProps<{
  translation?: {
    locale: string
    stale: boolean
    unofficial: boolean
    method?: 'human' | 'machine' | 'machine_reviewed'
  } | null
  sourceUrl?: string | null
}>()

const { $t } = useNuxtApp()
const showing = computed(() => !!props.translation)

/**
 * "A person wrote and checked this" and "a translation service produced this
 * and nobody has read it" are different claims, and the second one must never
 * be dressed as the first. The wording changes with the method, and so does the
 * emphasis: a machine translation is presented as something to verify, not as
 * something to rely on.
 */
const byMachine = computed(() => props.translation?.method === 'machine')
const label = computed(() => (byMachine.value ? 'translation.labelMachine' : 'translation.label'))
const explain = computed(() =>
  byMachine.value ? 'translation.explainMachine' : 'translation.explain'
)
</script>

<template>
  <div
    v-if="showing"
    class="notice"
    :class="{ 'notice--stale': translation!.stale, 'notice--machine': byMachine }"
  >
    <p class="tiny">
      <strong>{{ $t(label) }}</strong>
      {{ $t(explain) }}
    </p>
    <p v-if="translation!.stale" class="tiny stale-line">
      {{ $t('translation.stale') }}
    </p>
    <p v-if="sourceUrl" class="tiny">
      <a :href="sourceUrl" rel="noopener external" target="_blank">
        {{ $t('translation.viewOriginal') }}
      </a>
    </p>
  </div>
</template>

<style scoped>
.notice {
  padding: var(--s3) var(--s4);
  border: 1px solid var(--border);
  border-left: 3px solid var(--badge-community);
  border-radius: var(--radius-sm);
  background: var(--badge-community-bg);
}
/* Machine and stale are both different claims from "translated", so each gets
   its own colour - and each also says so in words, because colour is never the
   only signal. Stale wins: an out-of-date translation is the more urgent thing
   to know about. */
.notice--machine {
  border-left-color: var(--warning);
}
.notice--stale {
  border-left-color: var(--warning);
  background: var(--warning-bg);
}
.notice p { margin: 0; }
.notice p + p { margin-top: var(--s1); }
.stale-line { color: var(--warning); font-weight: 500; }
</style>
