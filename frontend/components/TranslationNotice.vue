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
  translation?: { locale: string; stale: boolean; unofficial: boolean } | null
  sourceUrl?: string | null
}>()

const { $t } = useNuxtApp()
const showing = computed(() => !!props.translation)
</script>

<template>
  <div v-if="showing" class="notice" :class="{ 'notice--stale': translation!.stale }">
    <p class="tiny">
      <strong>{{ $t('translation.label') }}</strong>
      {{ $t('translation.explain') }}
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
/* Stale is a different claim from translated, so it is a different colour and
   it also says so in words - colour is never the only signal. */
.notice--stale {
  border-left-color: var(--warning);
  background: var(--warning-bg);
}
.notice p { margin: 0; }
.notice p + p { margin-top: var(--s1); }
.stale-line { color: var(--warning); font-weight: 500; }
</style>
